"""
SWE-bench-pro 评估结果转换工具

该模块负责处理 SWE-bench-pro 评估结果的转换：
将原始 evaluate JSON 转换为标准的 metadata 格式
"""

import os
import json
import csv
from pathlib import Path
from typing import Dict, Any


def load_eval_results(eval_file: Path) -> Dict[str, float]:
    """
    加载单个评测结果文件并转换为分数格式
    
    Args:
        eval_file: 评测结果文件路径
        
    Returns:
        实例ID到分数的映射字典
    """
    instance_scores = {}
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_results = json.load(f)
    
    for instance_id, is_correct in eval_results.items():
        instance_scores[instance_id] = 1.0 if is_correct else 0.0
    
    return instance_scores


def extract_model_name(file_path: Path) -> str:
    """
    从文件名中提取模型名称
    
    文件格式: {model_name}_eval_results.json
    提取后: model_name
    
    Args:
        file_path: 评测结果文件路径
        
    Returns:
        模型名称
    """
    return file_path.stem.replace("_eval_results", "")


def generate_metadata(input_dir: str, output_dir: str) -> None:
    """
    处理原始评估结果，生成标准的 metadata 格式

    支持的评测文件格式: {model_name}_eval_results.json
    例如: claude-4sonnet_eval_results.json → 模型名称: claude-4sonnet

    Args:
        input_dir: 原始评估结果目录路径（包含多个 *_eval_results.json 文件）
        output_dir: 输出的 metadata 文件夹路径
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)

    # 查找所有评测结果文件（格式: {model_name}_eval_results.json）
    eval_files = sorted(input_path.glob("*_eval_results.json"))

    if not eval_files:
        raise FileNotFoundError(
            f"在目录 {input_dir} 中找不到任何符合格式的评测文件\n"
            f"期望格式: {{model_name}}_eval_results.json\n"
            f"例如: claude-4sonnet_eval_results.json"
        )

    print(f"找到 {len(eval_files)} 个评测结果文件:")
    for ef in eval_files:
        print(f"  - {ef.name}")

    # 定义输出文件路径
    metadata_csv_name = "swe_bench_pro_metadata"
    metadata_csv_path = output_path / f"{metadata_csv_name}.csv"
    info_path = output_path / "info.json"

    # 加载或初始化 info.json
    if info_path.exists():
        with open(info_path, "r", encoding="utf-8") as f:
            info_data = json.load(f)
    else:
        info_data = []

    info_dict: Dict[str, Any] = {item["name"]: item for item in info_data}
    all_instance_ids: set = set()
    model_scores: Dict[str, Dict[str, float]] = {}

    # 先收集所有数据
    for eval_file in eval_files:
        model_name = extract_model_name(eval_file)
        scores = load_eval_results(eval_file)
        model_scores[model_name] = scores
        all_instance_ids.update(scores.keys())
        
        print(f"\n处理模型: {model_name}")
        print(f"  记录数: {len(scores)}")
        print(f"  平均得分: {sum(scores.values()) / len(scores):.4f}")

    # 生成或更新 metadata CSV
    if metadata_csv_path.exists():
        # 读取现有数据
        with open(metadata_csv_path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            existing_fieldnames = reader.fieldnames.copy()
            existing_rows = {row["id"]: row for row in reader}

        # 添加新模型列
        for model_name in model_scores:
            score_col_name = f"{model_name}/correct"
            if score_col_name not in existing_fieldnames:
                existing_fieldnames.insert(-1, score_col_name)

        # 合并所有实例ID
        for instance_id in all_instance_ids:
            if instance_id not in existing_rows:
                existing_rows[instance_id] = {"id": instance_id, "difficulty": "level0"}

        # 更新分数
        for instance_id, row in existing_rows.items():
            for model_name, scores in model_scores.items():
                score_col_name = f"{model_name}/correct"
                row[score_col_name] = scores.get(instance_id, 0.0)

        # 写入文件
        with open(metadata_csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=existing_fieldnames)
            writer.writeheader()
            for instance_id in sorted(existing_rows.keys()):
                writer.writerow(existing_rows[instance_id])

        # 更新 info.json
        for model_name, scores in model_scores.items():
            avg_score = sum(scores.values()) / len(scores) if scores else 0.0
            if metadata_csv_name in info_dict:
                if avg_score not in info_dict[metadata_csv_name]["avg_scores"]:
                    info_dict[metadata_csv_name]["avg_scores"].append(avg_score)
                info_dict[metadata_csv_name]["count"] = len(existing_rows)
            else:
                info_dict[metadata_csv_name] = {
                    "name": metadata_csv_name,
                    "count": len(existing_rows),
                    "avg_scores": [avg_score],
                    "difficulty_map": {"level0": 0}
                }

    else:
        # 新建文件
        fieldnames = ["id"] + [f"{m}/correct" for m in model_scores] + ["difficulty"]
        
        with open(metadata_csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for instance_id in sorted(all_instance_ids):
                row = {"id": instance_id, "difficulty": "level0"}
                for model_name, scores in model_scores.items():
                    row[f"{model_name}/correct"] = scores.get(instance_id, 0.0)
                writer.writerow(row)

        # 初始化 info.json
        avg_scores = [
            sum(scores.values()) / len(scores) if scores else 0.0
            for scores in model_scores.values()
        ]
        info_dict[metadata_csv_name] = {
            "name": metadata_csv_name,
            "count": len(all_instance_ids),
            "avg_scores": avg_scores,
            "difficulty_map": {"level0": 0}
        }

    # 保存 info.json
    info_data = list(info_dict.values())
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(info_data, f, ensure_ascii=False, indent=4)

    print(f"\nMetadata 生成完成:")
    print(f"  - CSV 文件: {metadata_csv_path}")
    print(f"  - Info 文件: {info_path}")
    print(f"  - 总实例数: {len(all_instance_ids)}")
    print(f"  - 模型数: {len(model_scores)}")


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="将 SWE-bench-pro evaluate JSON 转换为 multi_data_sample 格式的 metadata CSV"
    )
    parser.add_argument(
        "input_dir",
        help="evaluate 结果 JSON 所在目录路径",
    )
    parser.add_argument(
        "output_dir",
        help="输出 metadata 文件夹路径",
    )
    args = parser.parse_args()

    print(f"args.input_dir={args.input_dir}, args.output_dir={args.output_dir}")

    if not os.path.isdir(args.input_dir):
        print(f"错误: 目录不存在: {args.input_dir}", file=sys.stderr)
        sys.exit(1)

    generate_metadata(args.input_dir, args.output_dir)