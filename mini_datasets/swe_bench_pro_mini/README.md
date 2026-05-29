# SWE-bench-Pro-mini

## 简介

SWE-bench-Pro-mini 是基于 SWE-bench Pro 评估结果进行采样得到的一个小规模数据集，它在多模型测试得分上与原始数据集大致相同。

SWE-bench Pro 是一个比 SWE-bench Verified 更具挑战性的编程 Agent 基准测试，包含来自真实开源仓库的复杂软件工程任务。公共数据集包含 731 个任务，涵盖 Python、TypeScript、Go 和 JavaScript 四种编程语言。

本数据集选取的评估得分涵盖以下模型：Claude-4.5-Sonnet、Claude-4.5-Opus、Gemini-3-Pro、GPT-5 (High)、Qwen3-480B、Kimi-K2.6、GLM-5.1、DeepSeek-V4-Pro 等。

## 数据集获取方式

[🔗SWE-bench_Pro 完整数据集](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro)

## 复现数据提取过程

先安装 kmeans 采样脚本依赖：

```bash
pip3 install -r ../requirements.txt
```

执行采样过程：

```bash
# 步骤1: 使用 K-Means 压缩 metadata，自动为每个子集取最优簇
python ../select_metadata_by_kmeans.py --input ./swe_bench_pro_metadata --work-dir ./compressed_output --compression-ratio 0.05 -a

python ../select_metadata_by_kmeans.py --input ./swe_bench_pro_metadata --work-dir ./compressed_output --compression-ratio 0.1 -a

python ../select_metadata_by_kmeans.py --input ./swe_bench_pro_metadata --work-dir ./compressed_output --compression-ratio 0.2 -a

# 步骤2: 将压缩后的 metadata 转换为最终数据集（需指定原始数据集路径）
python ../compressed_metadata_to_mini_datasets.py swe_bench_pro_mini --input ./compressed_output/swe_bench_pro_metadata_compressed_0.05 --output ./SWE-Bench_Pro_select_0.05/data --source-dir <原始SWE-bench-Pro数据集路径>

python ../compressed_metadata_to_mini_datasets.py swe_bench_pro_mini --input ./compressed_output/swe_bench_pro_metadata_compressed_0.10 --output ./SWE-Bench_Pro_select_0.10/data --source-dir <原始SWE-bench-Pro数据集路径>

python ../compressed_metadata_to_mini_datasets.py swe_bench_pro_mini --input ./compressed_output/swe_bench_pro_metadata_compressed_0.20 --output ./SWE-Bench_Pro_select_0.20/data --source-dir <原始SWE-bench-Pro数据集路径>
```

例如：

```bash
# 步骤1: 使用 K-Means 压缩 metadata，自动为每个子集取最优簇
python ../select_metadata_by_kmeans.py --input ./swe_bench_pro_metadata --work-dir ./compressed_output --compression-ratio 0.1 -a

# 步骤2: 将压缩后的 metadata 转换为最终数据集
python ../compressed_metadata_to_mini_datasets.py swe_bench_pro_mini --input ./compressed_output/swe_bench_pro_metadata_compressed_0.10 --output ./final_mini_dataset --source-dir /path/to/SWE-bench_Pro
```

采样效果图结构如下：

```bash
compressed_output/
├── swe_bench_pro_metadata_compressed_0.10
│   ├── clustering_visualizations # kmeans聚类效果可视化图
│   ├── random
│   └── representative
└── swe_bench_pro_metadata_figures_0.10 # 采样得分效果图
    ├── comparison_summary.json
    └── swe_bench_pro_metadata_means_comparison.png
```

最终生成的采样数据集如下（从原始 parquet 文件中筛选对应 instance_id 的数据）：

```bash
SWE-Bench_Pro_select_0.10/data
└── <原始parquet文件名>.parquet
```

## 评测模型列表

以下模型已在 SWE-bench Pro 公共数据集上进行过评估：

| 模型 | 组织 | 典型得分 |
|------|------|----------|
| Claude Opus 4.5 | Anthropic | ~45.9% |
| Claude Sonnet 4.5 | Anthropic | ~43.6% |
| Gemini 3 Pro | Google | ~43.3% |
| Claude Sonnet 4 | Anthropic | ~42.7% |
| GPT-5 (High) | OpenAI | ~41.8% |
| GPT-5.2 Codex | OpenAI | ~41.0% |
| Kimi K2.6 | Moonshot AI | ~27.7% |
| Qwen3 480B | Alibaba | ~38.7% |
| GLM-5 | Z.AI | ~55.1% |
| DeepSeek V4 Pro | DeepSeek | ~55.4% |
| Gemini 3 Flash | Google | ~34.6% |
| MiniMax 2.1 | MiniMax | ~36.8% |

更多模型评估结果请参考 [Scale AI SEAL Leaderboard](https://scale.com/leaderboard/swe_bench_pro_public)。
