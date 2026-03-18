# 评估方案

## 评估维度

| 维度 | 缩写 | 评估方式 | 说明 |
|---|---|---|---|
| Content Richness | CR | LLM-as-Judge | 内容深度、广度、知识准确性 |
| Interaction Design | ID | LLM-as-Judge | 交互设计意图（纯看代码，不考虑是否能跑） |
| Interaction Quality | IQ | ID × IF | 交互综合质量 = 设计分 × 可用率 |
| Visual Quality | VQ | LLM-as-Judge (多模态) | 布局、排版、美观度（截图+代码） |
| Render Correctness | RC | Playwright 自动化 | 页面能否正常加载，JS 有无报错 |
| Interaction Functionality | IF | Playwright 自动化 | 交互元素触发后 DOM 是否变化 |

## 版本迭代

结果存储格式：`llm_judge[model@version]`，如 `google/gemini-3.1-pro-preview@v2`。

### v1（基线）

- ID prompt 包含 IF 自动化测试结果，告诉 LLM 哪些交互能用哪些不能
- 问题：3.1-pro 过度依赖 IF 结果，几乎所有方法 ID=1；flash 偏高但排序更合理
- IQ = ID × IF 在 v1 下意义不大（ID 已被 IF 污染）

| 模型 | CR Pearson | ID Pearson | VQ Pearson | ID MAE |
|---|---|---|---|---|
| gemini-3-flash@v1 | 0.660 | 0.498 | 0.715 | 1.04 |
| gemini-3.1-pro@v1 | 0.800 | 0.222 | 0.679 | 1.85 |

### v2（当前）

- ID prompt 去掉 IF 参考，LLM 纯看代码评设计意图
- IQ = ID × IF，分离"设计质量"和"实现质量"
- 采用 gemini-3.1-pro（CR 对齐更好）
- VQ prompt 待调优（系统性偏高）

## 代码结构

代码在 `benchmark/evals/` 目录：
- `prompts.py` — 评分 rubric（含版本）
- `llm_judge.py` — LLM 评分（CR/ID/VQ）
- `functional_eval.py` — Playwright 自动化（RC/IF）
- `run_eval.py` — 批量评估入口

运行方式：
```bash
cd codebase

# 评估（默认 v2）
uv run python benchmark/evals/run_eval.py --force --llm-only \
    --judge-model openrouter/google/gemini-3.1-pro-preview

# 指定版本
uv run python benchmark/evals/run_eval.py --force --llm-only \
    --judge-model openrouter/google/gemini-3.1-pro-preview --version v3

# 只跑某些维度
uv run python benchmark/evals/run_eval.py --force --dimension ID --dimension VQ

# 查看对齐
uv run python benchmark/evals/human/alignment.py
```

## 已知局限

### IF 的 canvas 盲区

IF 通过 DOM diff 检测交互是否生效。canvas 上的交互（mousedown/mousemove）不改变 DOM，会被误判为失败。这对所有方法公平，相对排序不受影响。
