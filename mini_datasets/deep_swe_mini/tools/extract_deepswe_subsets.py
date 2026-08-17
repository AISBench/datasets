#!/usr/bin/env python3
"""
DEEPSWE 子集抽取工具

基于 metadata CSV 中的 instance_id 列表，从原始 parquet 数据集中
筛选对应的数据，保存为新的 parquet 文件（文件名与原始文件保持一致）。
"""

import csv
from pathlib import Path
from typing import List, Set

import pandas as pd


def load_csv_ids(csv_path: str) -> List[str]:
    """
    从 metadata CSV 文件中加载实例 ID 列表

    Args:
        csv_path: metadata CSV 文件路径

    Returns:
        实例 ID 列表
    """
    ids = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ids.append(row["id"])
    return ids


def extract_subsets(metadata_path: str, dataset_path: str, output_dir: str) -> None:
    """
    基于 metadata CSV 中的 id 列表，从原始数据集中筛选
    对应的数据，保存为新的 parquet 文件（文件名与原始文件保持一致）。

    支持两种 source_dir 布局：
        1. parquet 文件直接位于 dataset_path 下
        2. parquet 文件位于 dataset_path/data/ 下

    Args:
        metadata_path: metadata CSV 文件路径（包含 id 列）
        dataset_path: 原始数据集目录路径
        output_dir: 输出目录，保存筛选后的数据集
    """
    csv_ids = load_csv_ids(metadata_path)
    csv_id_set: Set[str] = set(csv_ids)
    print(f"Loaded {len(csv_ids)} ids from metadata CSV")

    # 定位 parquet 文件：优先 data/ 子目录，其次根目录
    source_root = Path(dataset_path)
    parquet_files: List[Path] = []

    data_subdir = source_root / "data"
    if data_subdir.exists():
        parquet_files = list(data_subdir.glob("*.parquet"))

    if not parquet_files:
        parquet_files = list(source_root.glob("*.parquet"))

    if not parquet_files:
        raise FileNotFoundError(
            f"未找到 parquet 文件，已检查目录: {data_subdir} 和 {source_root}"
        )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    total_filtered = 0
    all_found_ids: Set[str] = set()

    for pf in parquet_files:
        df = pd.read_parquet(pf)
        print(f"Loaded {len(df)} records from {pf.name}")

        # 匹配列：优先 instance_id，其次 task_id
        id_col = None
        for candidate in ("instance_id", "task_id"):
            if candidate in df.columns:
                id_col = candidate
                break

        if id_col is None:
            print(f"Warning: 未找到 instance_id/task_id 列于 {pf.name}，跳过")
            continue

        filtered_df = df[df[id_col].astype(str).isin(csv_id_set)]
        print(f"Filtered to {len(filtered_df)} records from {pf.name} (by {id_col})")

        output_file = output_path / pf.name
        filtered_df.to_parquet(output_file, index=False)
        print(f"Saved to {output_file}")
        total_filtered += len(filtered_df)

        all_found_ids.update(df[id_col].astype(str).tolist())

    print(f"Total filtered records: {total_filtered}")

    # 校验缺失 id
    missing_ids = csv_id_set - all_found_ids
    if missing_ids:
        print(f"Warning: {len(missing_ids)} ids from CSV not found in dataset:")
        for mid in sorted(missing_ids)[:10]:
            print(f"  - {mid}")
        if len(missing_ids) > 10:
            print(f"  ... and {len(missing_ids) - 10} more")


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="基于 metadata CSV 从 DEEPSWE 原始数据集中抽取子集"
    )
    parser.add_argument("metadata_path", help="metadata CSV 文件路径")
    parser.add_argument("dataset_path", help="原始数据集目录路径")
    parser.add_argument("output_dir", help="输出目录路径")
    args = parser.parse_args()

    if not Path(args.metadata_path).exists():
        print(f"错误: metadata 文件不存在: {args.metadata_path}", file=sys.stderr)
        sys.exit(1)
    if not Path(args.dataset_path).is_dir():
        print(f"错误: 数据集目录不存在: {args.dataset_path}", file=sys.stderr)
        sys.exit(1)

    extract_subsets(args.metadata_path, args.dataset_path, args.output_dir)
