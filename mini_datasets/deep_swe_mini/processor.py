"""
deep_swe_mini 数据处理模块

该模块负责将原始评估结果转换为标准的 metadata 格式，
以及将压缩后的 metadata 转换为最终的数据集内容。
"""

import os
import sys
from pathlib import Path

# 添加 tools 目录到路径，以便导入相关工具
tools_dir = Path(__file__).parent / "tools"
sys.path.insert(0, str(tools_dir))

from convert_deepswe_results import generate_metadata
from extract_deepswe_subsets import extract_subsets


def process_eval_results(input_dir: str, output_dir: str) -> None:
    """
    处理原始评估结果，生成标准的 metadata 格式

    Args:
        input_dir: 原始评估结果目录路径（应包含 deepswe_results.json）
        output_dir: 输出的 metadata 文件夹路径
    """
    os.makedirs(output_dir, exist_ok=True)

    print(f"处理评估结果: {input_dir}")
    generate_metadata(input_dir, output_dir)
    print(f"Metadata 已保存到: {output_dir}")


def process_compressed_metadata(input_dir: str, output_dir: str, source_dir: str = None) -> None:
    """
    处理压缩后的 metadata，生成最终的数据集内容

    Args:
        input_dir: kmeans压缩后的metadata路径（应包含 representative 子目录）
        output_dir: 基于压缩的metadata文件夹生成的压缩后的数据集内容路径
        source_dir: 原始数据集目录路径（应包含 test-00000-of-00001.parquet）

    Raises:
        FileNotFoundError: metadata CSV 文件不存在时抛出
        ValueError: source_dir 参数未提供时抛出
    """
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("处理压缩后的 metadata")
    print("=" * 60)

    representative_dir = Path(input_dir) / "representative"
    metadata_csv = representative_dir / "deepswe_metadata.csv"

    if not metadata_csv.exists():
        raise FileNotFoundError(f"metadata CSV 文件不存在: {metadata_csv}")

    if source_dir is None:
        raise ValueError("source_dir 参数未提供，无法筛选数据集")

    extract_subsets(str(metadata_csv), source_dir, output_dir)

    print("\n" + "=" * 60)
    print("处理完成！")
    print(f"输出目录: {output_dir}")
