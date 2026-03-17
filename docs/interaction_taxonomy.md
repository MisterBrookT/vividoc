# 交互类型分类 (Interaction Taxonomy)

基于 `benchmark/datasets/prepped/topics.jsonl` 中 101 篇真实可交互文档的 482 个交互实例，
我们按**交互意图/行为模式**（而非 UI 控件类型）进行分类。
分类思路受 Munzner 的 What-Why-How 分析框架 [1] 启发（特别是 Chapter 11 Manipulate View
中对 navigate、select、change 等操作的讨论），但具体类别是根据教育可交互文档的实际数据归纳得出的。

[1] Munzner, T. (2014). Visualization Analysis and Design. CRC Press.

## 分类结果

| 类别 | 数量 | 占比 | 说明 |
|------|------|------|------|
| State Switching | 181 | 37.6% | 在离散选项间切换（选数据集、选算法、切换模式） |
| Parameter Exploration | 121 | 25.1% | 调连续参数观察变化（slider 调半径、频率、阈值） |
| Freeform Construction | 53 | 11.0% | 自由创建内容（画图、写代码、编辑数值、上传文件） |
| Direct Manipulation | 45 | 9.3% | 拖拽可视化中的对象（数据点、控制点、节点） |
| Temporal Control | 32 | 6.6% | 控制时间维度（play/pause、step、调速、scrub） |
| Inspection | 24 | 5.0% | 探查细节（hover tooltip、cursor tracking） |
| Spatial Navigation | 24 | 5.0% | 空间导航（zoom、pan、rotate 3D） |
| Scroll-driven Narrative | 2 | 0.4% | 滚动驱动叙事进展 |

## 分类依据

- **按交互意图分类**，不按 UI 控件类型。例如 slider 可能用于 Parameter Exploration（调参数）
  也可能用于 Temporal Control（scrub timeline），取决于用户的意图。
- 分类来源于真实世界的可交互教育文档，覆盖数学、算法、物理、音乐等 11 个学科领域。
- 每个类别都可以用 SRTC（State-Render-Transition-Constraint）规范表达，
  示例见 `benchmark/datasets/interaction_examples/`。

## 相关文件

- 分类脚本: `benchmark/datasets/interaction_taxonomy.py`
- 分类统计: `benchmark/datasets/interaction_taxonomy.json`
- 逐条分类: `benchmark/datasets/interaction_classified.json`
- SRTC 示例: `benchmark/datasets/interaction_examples/*/spec.json`
