# viviDoc

viviDoc 是一个用于生成交互式文档的系统，采用多智能体架构，包括规划、执行和评估三个核心组件。

## 安装

### 前置要求

- [uv](https://github.com/astral-sh/uv) (安装方法: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 安装步骤

```bash
# 克隆仓库
git clone <repository-url>
cd viviDoc

# 使用 uv 安装依赖
uv sync --dev
```
### 执行
```bash
vividoc --help
```

## 数据集

数据集位于 `datasets/prepped/topic.jsonl` 目录下，包含处理后的 JSONL 格式数据文件。

## 流程描述

详细的流程和方法说明请参考 `docs/` 目录下的文档，特别是 `docs/method.md`，其中描述了：

- **Planner Agent**: 负责生成文档结构和逻辑规划
- **Exec Agent**: 负责文本和交互式代码的生成
- **Eval Agent**: 负责评估文档的连贯性和运行时正确性
