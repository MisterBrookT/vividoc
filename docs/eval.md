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

代码在 `benchmark/evals/` 目录：
- `prompts.py` — 评分 rubric
- `llm_judge.py` — LLM 评分（3个维度）
- `functional_eval.py` — Playwright 自动化（2个维度）
- `run_eval.py` — 批量评估入口

运行方式：
```bash
cd codebase

# 统一入口
uv run python benchmark/run.py --num 5                              # 生成+评估前5个topic
uv run python benchmark/run.py --mode generate --num 5              # 只生成
uv run python benchmark/run.py --mode eval                          # 只评估
uv run python benchmark/run.py --topic "what is pi" --only vividoc  # 单个topic+方法

# 单独跑评估
uv run python benchmark/evals/run_eval.py
uv run python benchmark/evals/run_eval.py --topic what_is_pi
```

Playwright 自动化指标（RC/IF）已验证可用，区分度良好。

Content Richness 评估时会先提取纯文本内容（去掉 script/style/head/canvas/svg），只让 LLM 评文字部分，避免被代码量干扰。

## 已知局限

### IF (Interaction Functionality) 的 canvas 盲区

当前 IF 通过 DOM diff 检测交互是否生效（交互前后 `document.body.innerHTML` 是否变化）。这有两个局限：

1. **canvas 交互未被统计**：canvas 上的 mousedown/mousemove 等交互不在检测范围内（只检测 button/slider/checkbox/select/[onclick]）
2. **canvas 操作被误判为失败**：如 "Clear All" 按钮清空 canvas 内容，DOM 不变但交互实际成功

这对所有方法是公平的（同样的检测方式），相对排序应该不受影响。后续可通过 `canvas.toDataURL()` 截图对比来改进。

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
