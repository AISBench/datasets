# Terminal-Bench-2.0-mini

## 简介

Terminal-Bench-2.0-mini 是基于 [Terminal-Bench-2.0](https://www.tbench.ai/benchmarks/terminal-bench-2) 评估结果进行约小规模的采样得到的一个小规模数据集，它在测试得分上与原始数据集大致相同。

Terminal-Bench-2.0 包含 89 个真实任务，涵盖编译构建、代码调试、逆向工程、系统配置、生物信息等多个领域，用于评估 AI Agent 的终端操作能力。

评估得分涵盖以下 46 个模型：Ante__Gemini_3_Pro_Preview、Ante__Gemini_3.1_Pro_Preview、BashAgent__TermiGen_32B、Capy__Claude_Opus_4.6、ClaudeCode__GLM_4.7、CodeBrain_1__GPT_5.3_Codex、CodeBrain_1__Gemini_3_Pro_Preview、Crux__Claude_Opus_4.6、Deep_Agents__GPT_5.2_Codex、Droid__Claude_Opus_4.6、Droid__GPT_5.3_Codex、Forge__GPT_5.4、Forge__Gemini_3.1_Pro_Preview、Forge__Opus_4.6、Gemini_CLI__Gemini_3_Flash_Preview、IndusAGICodingAgent__gpt_5.3_codex、Judy__Claude_Opus_4.6、Judy__Gemini_3.1_Pro_Preview、Junie_CLI__Gemini_3_Flash_Preview_Gemini_3.1_Pro_Preview_Claude_Opus_4.6_GPT_5.3_Codex、MAYA__Claude_4.5_sonnet、MAYA__Claude_4.6_opus、Mux__Claude_Opus_4.5、Mux__Claude_Opus_4.6、Mux__GPT_5.2、Mux__GPT_5.3_Codex、OB_1_GPT_5.3_Codex_Claude_Opus_4.5_Claude_Opus_4.6、OB_1_GPT_5.4_GPT_5.3_Codex_Claude_Opus_4.5_Claude_Opus_4.6、OpenCode__Claude_Opus_4.5、OpenSage__GPT_5.3_Codex、OpenSage__Gemini_3_Pro_Preview、Simple_Codex__GPT_5.3_Codex、Terminus_KIRA__Claude_Opus_4.6、Terminus_KIRA__Gemini_3.1_Pro_Preview、Terminus2__Claude_Opus_4.6、Terminus2__DeepSeek_V3.2、Terminus2__GLM_4.7、Terminus2__GLM_5、Terminus2__GPT_5.3_Codex、Terminus2__Kimi_k2.5、Terminus2__Minimax_m2.5、cchuter__minimax_m2.5、dakou__qwen3_coder_480b、grok_cli__grok_4.20_0309_reasoning、pilot_real__claude_opus_4_6、terminus_2__AfterQuery_GPT_OSS_20B。

## 数据集获取方式

[🔗terminal-bench-2-offline-mini 数据集](https://modelers.cn/datasets/AISBench/terminal-bench-2-offline-mini)
> 注：此数据集是剔除了agent需要访问外网评估任务后剩余70个任务的子集，具体任务列表请参考[run_online_report.md](./run_online_report.md)。

## 复现数据提取过程
获取剔除agent需要访问外网的terminal-bench-2数据集：
```bash
git clone https://github.com/AISBench/terminal-bench-2.git
cd terminal-bench-2
git checkout offline
```

先安装 kmeans 采样脚本依赖：
```bash
pip3 install -r ../requirements.txt
```

执行采样过程(以0.10压缩比为例)：
```bash
# 步骤1: 使用 K-Means 压缩 metadata，自动为每个子集取最优簇
python ../select_metadata_by_kmeans.py --input ./terminal-bench-2.0-metadata-offline --work-dir ./compressed_output --compression-ratio 0.1 -a

# 步骤2: 将压缩后的 metadata 转换为最终数据集（需指定原始数据集路径）
python ../compressed_metadata_to_mini_datasets.py terminal_bench_2.0_mini --input ./compressed_output/terminal-bench-2.0-metadata-offline_compressed_0.10/representative --output ./final_mini_dataset --source-dir <剔除agent需要访问外网的terminal-bench-2数据集路径>
```


采样效果图结构如下：
```bash
compressed_output/
├── terminal-bench-2.0-metadata-offline_compressed_0.10
│   ├── clustering_visualizations # kmeans聚类效果可视化图
│   ├── random
│   └── representative
└── terminal-bench-2.0-metadata-offline_figures_0.10 # 采样得分效果图
    ├── comparison_summary.json
    └── terminal-bench-2.0-metadata-offline_means_comparison.png
```

最终生成的采样数据集如下（从原始数据集目录中筛选对应 case_id 的文件夹）：
```bash
final_mini_dataset/
└── <case_id>/
    ├── task.toml
    ├── reference/
    └── ...
```

## Metadata 说明

该数据集包含两个 metadata 目录：

| 目录 | 描述 | case 数量 |
|------|------|-----------|
| `terminal-bench-2.0-metadata/` | 完整 metadata，包含所有 89 个 case | 89 |
| `terminal-bench-2.0-metadata-offline/` | 离线 metadata，仅包含不涉及外网访问的 70 个 case | 70 |

详细信息请参考 [run_online_report.md](run_online_report.md)，其中包含了对 89 个 case 的外网访问需求分析（19 个需要外网访问，70 个不需要）。

## 处理脚本说明

### processor.py

提供两个主要的处理函数：

1. **process_eval_results**: 将原始评估结果 CSV 文件转换为标准的 metadata 格式

```python
from processor import process_eval_results
process_eval_results(
    input_dir="/path/to/terminus2_eval_results",
    output_dir="/path/to/output_metadata"
)
```

2. **process_compressed_metadata**: 将压缩后的 metadata 转换为最终的数据集内容

```python
from processor import process_compressed_metadata
process_compressed_metadata(
    input_dir="/path/to/compressed_metadata",
    output_dir="/path/to/output_dataset",
    source_dir="/path/to/terminal-bench-2"  # 可选，默认使用同级目录下的 terminal-bench-2
)
```

### tools/

- `convert_eval_to_metadata.py`: 将 tbench.ai 评估 CSV 结果转换为 metadata CSV 格式
- `extract_terminal_bench_subsets.py`: 基于压缩后的 metadata CSV 从原始数据集中筛选对应 case
- `scrape_tbench.py`: 从 tbench.ai 排行榜页面抓取表格数据并导出为 CSV
- `stat_task_fields.py`: 统计 metadata 中各 case 的 difficulty 和 category 字段分布