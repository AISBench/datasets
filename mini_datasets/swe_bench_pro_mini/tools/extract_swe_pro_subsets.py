#!/usr/bin/env python3

import csv
import pandas as pd

from pathlib import Path
from typing import List, Set

def load_csv_ids(csv_path: str) -> List[str]:
    """
    从 metadata CSV 文件中加载实例 ID 列表
    
    Args:
        csv_path: metadata CSV 文件路径
        
    Returns:
        实例 ID 列表
    """
    ids = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ids.append(row['id'])
    return ids


def extract_subsets(metadata_path: str, dataset_path: str, output_dir: str) -> None:
    """
    基于 metadata CSV 中的 id 列表，从原始数据集中筛选
    对应的数据，保存为新的 parquet 文件（文件名与原始文件保持一致）。

    Args:
        metadata_path: metadata CSV 文件路径（包含 id 列）
        dataset_path: 原始数据集目录路径（应包含 data 子目录）
        output_dir: 输出目录，保存筛选后的数据集
    """
    csv_ids = load_csv_ids(metadata_path)
    csv_id_set: Set[str] = set(csv_ids)
    print(f"Loaded {len(csv_ids)} ids from metadata CSV")

    data_path = Path(dataset_path) / 'data'
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_path}")

    parquet_files = list(data_path.glob('*.parquet'))
    if not parquet_files:
        raise FileNotFoundError(f"No parquet files found in {data_path}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    total_filtered = 0

    for pf in parquet_files:
        df = pd.read_parquet(pf)
        print(f"Loaded {len(df)} records from {pf.name}")

        if 'instance_id' not in df.columns:
            print(f"Warning: 'instance_id' column not found in {pf.name}, skipping")
            continue

        filtered_df = df[df['instance_id'].isin(csv_id_set)]
        print(f"Filtered to {len(filtered_df)} records from {pf.name}")

        output_file = output_path / pf.name
        filtered_df.to_parquet(output_file, index=False)
        print(f"Saved to {output_file}")
        total_filtered += len(filtered_df)

    print(f"Total filtered records: {total_filtered}")

    all_found_ids: Set[str] = set()
    for pf in parquet_files:
        df = pd.read_parquet(pf)
        if 'instance_id' in df.columns:
            all_found_ids.update(df['instance_id'].tolist())

    missing_ids = csv_id_set - all_found_ids
    if missing_ids:
        print(f"Warning: {len(missing_ids)} ids from CSV not found in dataset:")
        for mid in list(missing_ids)[:10]:
            print(f"  - {mid}")
        if len(missing_ids) > 10:
            print(f"  ... and {len(missing_ids) - 10} more")
