# DEEP-SWE-mini

## 简介

DEEP-SWE-mini 是基于 DEEP-SWE 评估结果进行采样得到的一个小规模数据集，它在多模型测试得分上与原始数据集大致相同。

DEEP-SWE 是一个软件工程 Agent 基准测试，包含 113 个来自真实开源仓库的复杂任务。本数据集选取的评估得分涵盖 53 个模型（含不同 effort level），包括 Claude Opus 5、GPT-5.6 系列、Claude Fable 5、Gemini 3.x、GLM-5.2、Kimi-K3 等。

## 数据集获取方式

[🔗DEEP-SWE 完整数据集](<原始 DEEP-SWE 数据集链接>)

## 复现数据提取过程

先安装 kmeans 采样脚本依赖：

```bash
pip3 install -r ../requirements.txt
```

执行采样过程：

```bash
# 步骤1: 使用 K-Means 压缩 metadata，自动为每个子集取最优簇
python ../select_metadata_by_kmeans.py --input ./deepswe_metadata --work-dir ./compressed_output --compression-ratio 0.05 -a

python ../select_metadata_by_kmeans.py --input ./deepswe_metadata --work-dir ./compressed_output --compression-ratio 0.1 -a

python ../select_metadata_by_kmeans.py --input ./deepswe_metadata --work-dir ./compressed_output --compression-ratio 0.2 -a

# 步骤2: 将压缩后的 metadata 转换为最终数据集（需指定原始数据集路径）
python ../compressed_metadata_to_mini_datasets.py deep_swe_mini --input ./compressed_output/deepswe_metadata_compressed_0.05 --output ./DEEP-SWE_select_0.05/data --source-dir <原始DEEP-SWE数据集路径>

python ../compressed_metadata_to_mini_datasets.py deep_swe_mini --input ./compressed_output/deepswe_metadata_compressed_0.10 --output ./DEEP-SWE_select_0.10/data --source-dir <原始DEEP-SWE数据集路径>

python ../compressed_metadata_to_mini_datasets.py deep_swe_mini --input ./compressed_output/deepswe_metadata_compressed_0.20 --output ./DEEP-SWE_select_0.20/data --source-dir <原始DEEP-SWE数据集路径>
```

例如：

```bash
# 步骤1: 使用 K-Means 压缩 metadata，自动为每个子集取最优簇
python ../select_metadata_by_kmeans.py --input ./deepswe_metadata --work-dir ./compressed_output --compression-ratio 0.1 -a

# 步骤2: 将压缩后的 metadata 转换为最终数据集
python ../compressed_metadata_to_mini_datasets.py deep_swe_mini --input ./compressed_output/deepswe_metadata_compressed_0.10 --output ./final_mini_dataset --source-dir /path/to/DEEP-SWE
```

采样效果图结构如下：

```bash
compressed_output/
├── deepswe_metadata_compressed_0.10
│   ├── clustering_visualizations # kmeans聚类效果可视化图
│   ├── random
│   └── representative
└── deepswe_metadata_figures_0.10 # 采样得分效果图
    ├── comparison_summary.json
    ├── deepswe_metadata_means_comparison_part1.png
    ├── deepswe_metadata_means_comparison_part2.png
    └── deepswe_metadata_means_comparison_part3.png
```

最终生成的采样数据集如下（从原始 parquet 文件中筛选对应 instance_id 的数据）：

```bash
DEEP-SWE_select_0.10/data
└── test-00000-of-00001.parquet
```

## 评测模型列表

以下模型已在 DEEP-SWE 公共数据集上进行过评估（共 53 个，含不同 effort level）：

| 模型 | 组织 | 典型得分 |
|------|------|----------|
| claude-opus-5 [max] | Anthropic | ~73.65% |
| claude-opus-5 [xhigh] | Anthropic | ~73.15% |
| claude-opus-5 [high] | Anthropic | ~72.83% |
| gpt-5.6-sol [max] | OpenAI | ~72.67% |
| gpt-5.6-sol [xhigh] | OpenAI | ~70.73% |
| claude-fable-5 [xhigh] | Anthropic | ~69.91% |
| claude-fable-5 [max] | Anthropic | ~69.72% |
| gpt-5.6-terra [max] | OpenAI | ~69.62% |
| gpt-5.6-sol [high] | OpenAI | ~69.40% |
| claude-opus-5 [medium] | Anthropic | ~68.90% |
| kimi-k3 [max] | Moonshot AI | ~68.51% |
| gpt-5.6-luna [max] | OpenAI | ~67.19% |
| gpt-5.5 [xhigh] | OpenAI | ~67.04% |
| claude-fable-5 [medium] | Anthropic | ~65.56% |
| gpt-5.5 [high] | OpenAI | ~64.38% |
| gpt-5.6-sol [medium] | OpenAI | ~61.06% |
| gpt-5.6-terra [xhigh] | OpenAI | ~60.18% |
| claude-fable-5 [low] | Anthropic | ~59.88% |
| claude-opus-4.8 [max] | Anthropic | ~58.78% |
| claude-opus-5 [low] | Anthropic | ~57.74% |
| qwen3.8-max [xhigh] | Alibaba | ~57.08% |
| gpt-5.6-luna [xhigh] | OpenAI | ~56.86% |
| muse-spark-1.2 [xhigh] | Xiaomi | ~54.87% |
| claude-opus-4.8 [xhigh] | Anthropic | ~54.50% |
| gpt-5.5 [medium] | OpenAI | ~53.98% |
| claude-sonnet-5 [max] | Anthropic | ~53.10% |
| grok-4.5 [high] | xAI | ~53.76% |
| gpt-5.6-terra [high] | OpenAI | ~53.76% |
| deepseek-v4-flash [max] | DeepSeek | ~53.32% |
| muse-spark-1.1 [xhigh] | Xiaomi | ~53.32% |
| gpt-5.4 [xhigh] | OpenAI | ~51.77% |
| claude-opus-4.8 [high] | Anthropic | ~51.77% |
| claude-sonnet-5 [xhigh] | Anthropic | ~49.63% |
| claude-opus-4.8 [medium] | Anthropic | ~48.67% |
| gemini-3.6-flash [high] | Google | ~48.53% |
| claude-sonnet-5 [high] | Anthropic | ~48.23% |
| gpt-5.6-sol [low] | OpenAI | ~45.35% |
| gpt-5.6-luna [high] | OpenAI | ~44.25% |
| glm-5.2 [max] | Z.AI | ~43.78% |
| claude-opus-4.8 [low] | Anthropic | ~40.86% |
| claude-sonnet-5 [medium] | Anthropic | ~39.82% |
| gemini-3.5-flash [medium] | Google | ~37.39% |
| glm-5.2 [high] | Z.AI | ~36.28% |
| gpt-5.6-terra [medium] | OpenAI | ~34.96% |
| kimi-k2.7-code | Moonshot AI | ~30.53% |
| claude-sonnet-5 [low] | Anthropic | ~30.31% |
| claude-sonnet-4.6 [high] | Anthropic | ~29.87% |
| gpt-5.5 [low] | OpenAI | ~26.99% |
| gpt-5.6-terra [low] | OpenAI | ~24.19% |
| gemini-3.1-pro [high] | Google | ~11.73% |
| gpt-5.6-luna [medium] | OpenAI | ~11.28% |
| gpt-5.6-luna [low] | OpenAI | ~1.55% |
