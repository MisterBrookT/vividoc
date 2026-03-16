# 评估方案

## 评估维度（5个）

| 维度 | 评估方式 | 说明 |
|---|---|---|
| Content Richness | LLM-as-Judge | 内容深度、广度、知识准确性 |
| Interaction Design | LLM-as-Judge | 交互设计是否有教学意义，是否帮助理解概念 |
| Visual Quality | LLM-as-Judge (多模态) | 布局、排版、美观度（截图+代码） |
| Render Correctness | Playwright 自动化 | 页面能否正常加载，JS 有无报错 |
| Interaction Functionality | Playwright 自动化 | 交互元素触发后 DOM 是否变化 |

## 当前实现

代码在 `evals/` 目录：
- `prompts.py` — 评分 rubric
- `llm_judge.py` — LLM 评分（3个维度）
- `functional_eval.py` — Playwright 自动化（2个维度）
- `run_eval.py` — 批量评估入口

运行方式：
```bash
cd codebase
uv run python evals/run_eval.py                          # 评估所有
uv run python evals/run_eval.py --topic what_is_pi       # 评估单个 topic
uv run python evals/run_eval.py --method vividoc --method naive_agent  # 评估指定方法
```

Playwright 自动化指标（RC/IF）已验证可用，区分度良好。

## 当前问题

LLM-as-Judge（CR/ID/VQ）区分度不足，几乎所有方法都拿满分。

可能原因：
1. **评估方式**：Pointwise 绝对评分天然有 leniency bias，LLM 倾向给高分
2. **评估模型**：gemini-3-flash 可能评分能力不够，需要试 GPT-4o / Claude
3. **Prompt 设计**：rubric 不够严格，缺少 "strict evaluator" 约束

## 下一步

1. 先收集人工评估数据（5 topic × 5 method × 3 evaluator），作为 ground truth
2. 对着人工数据调优 LLM-as-Judge，目标是高相关性（Spearman ≥ 0.7）
3. 调优方向：
   - 试 Pairwise 比较（每次给两个文档，判断哪个更好）
   - 试不同 judge model（GPT-4o, Claude）
   - 优化 prompt（加 strict 约束、加 few-shot 锚点示例）
4. 确定最终方案后，大规模跑。
