"""
DEEPSWE 评估结果转换工具

该模块负责处理 DEEPSWE 评估结果的转换：
将原始 deepswe_results.json（模型为行、case 为列）
转换为标准的 metadata 格式（case 为行、模型为列）。
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Any


METADATA_NAME = "deepswe_metadata"
RESULTS_FILENAME = "deepswe_results.json"


def generate_metadata(input_dir: str, output_dir: str) -> None:
    """
    处理原始评估结果，生成标准的 metadata 格式

    输入文件格式（deepswe_results.json）:
        [
            {
                "model_name": "claude-opus-5 [max]",
                "pass_rate": 0.7365,
                "<case_id_1>": 1.0,
                "<case_id_2>": 0.5,
                ...
            },
            ...
        ]

    输出:
        - {METADATA_NAME}.csv: id, <model1>/correct, <model2>/correct, ..., difficulty
        - info.json: name, count, avg_scores, difficulty_map

    Args:
        input_dir: 原始评估结果目录路径（包含 deepswe_results.json）
        output_dir: 输出的 metadata 文件夹路径
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results_file = input_path / RESULTS_FILENAME
    if not results_file.exists():
        raise FileNotFoundError(
            f"找不到评估结果文件: {results_file}\n"
            f"期望文件名: {RESULTS_FILENAME}"
        )

    with open(results_file, "r", encoding="utf-8") as f:
        results: List[Dict[str, Any]] = json.load(f)

    print(f"加载评估结果: {results_file}")
    print(f"模型数: {len(results)}")

    # 收集所有 case_id（保留首次出现顺序）
    case_ids: List[str] = []
    case_id_set: set = set()
    for model in results:
        for key in model.keys():
            if key in ("model_name", "pass_rate"):
                continue
            if key not in case_id_set:
                case_id_set.add(key)
                case_ids.append(key)

    model_names: List[str] = [m["model_name"] for m in results]
    avg_scores: List[float] = [m["pass_rate"] for m in results]

    print(f"Case 数: {len(case_ids)}")

    # 构建 model_name -> score mapping
    model_scores: Dict[str, Dict[str, float]] = {}
    for model in results:
        name = model["model_name"]
        model_scores[name] = {
            k: v for k, v in model.items() if k not in ("model_name", "pass_rate")
        }

    # 生成 metadata CSV
    metadata_csv_path = output_path / f"{METADATA_NAME}.csv"
    fieldnames = ["id"] + [f"{m}/correct" for m in model_names] + ["difficulty"]

    with open(metadata_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for case_id in case_ids:
            row = {"id": case_id, "difficulty": "level0"}
            for model_name in model_names:
                col = f"{model_name}/correct"
                row[col] = model_scores[model_name].get(case_id, 0.0)
            writer.writerow(row)

    print(f"Metadata CSV 已保存: {metadata_csv_path}")

    # 生成 info.json
    info_path = output_path / "info.json"
    info_data = [
        {
            "name": METADATA_NAME,
            "count": len(case_ids),
            "avg_scores": avg_scores,
            "difficulty_map": {"level0": 0},
        }
    ]
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(info_data, f, ensure_ascii=False, indent=4)

    print(f"Info 文件已保存: {info_path}")
    print(f"总实例数: {len(case_ids)}")
    print(f"模型数: {len(model_names)}")


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="将 DEEPSWE 评估结果 JSON 转换为标准 metadata 格式"
    )
    parser.add_argument("input_dir", help="deepswe_results.json 所在目录路径")
    parser.add_argument("output_dir", help="输出 metadata 文件夹路径")
    args = parser.parse_args()

    print(f"args.input_dir={args.input_dir}, args.output_dir={args.output_dir}")

    if not Path(args.input_dir).is_dir():
        print(f"错误: 目录不存在: {args.input_dir}", file=sys.stderr)
        sys.exit(1)

    generate_metadata(args.input_dir, args.output_dir)
