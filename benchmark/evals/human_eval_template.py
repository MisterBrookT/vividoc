"""Generate human evaluation CSV.

Simple table: topic × method, evaluator fills in CR/ID/VQ scores (1-5).

Usage:
    cd codebase
    uv run python benchmark/evals/human_eval_template.py --evaluators 3
"""

import argparse
import csv
from pathlib import Path

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
EVAL_DIR = Path(__file__).parent / "human"
METHODS = ["vividoc", "naive_agent", "autogen", "camel", "metagpt"]


def generate_sheets(num_evaluators: int):
    topics = sorted(
        d.name
        for d in OUTPUTS_DIR.iterdir()
        if d.is_dir() and any((d / m / "document.html").exists() for m in METHODS)
    )
    if not topics:
        print("No documents found.")
        return

    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    for i in range(1, num_evaluators + 1):
        csv_path = EVAL_DIR / f"evaluator_{i}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "topic",
                    "method",
                    "content_richness",
                    "interaction_design",
                    "visual_quality",
                    "notes",
                ]
            )
            for topic in topics:
                for method in METHODS:
                    if (OUTPUTS_DIR / topic / method / "document.html").exists():
                        writer.writerow([topic, method, "", "", "", ""])
        print(f"Created {csv_path}")

    # Rubric
    rubric_path = EVAL_DIR / "rubric.md"
    rubric_path.write_text(RUBRIC_TEXT, encoding="utf-8")
    print(f"Rubric saved to {rubric_path}")
    print(
        f"\n{len(topics)} topics × {len(METHODS)} methods × {num_evaluators} evaluators"
    )


RUBRIC_TEXT = """\
# 人工评估指南

## 评估流程
1. 打开 benchmark/outputs/{topic}/{method}/document.html（用浏览器）
2. 阅读文档，尝试所有交互
3. 对三个维度分别打 1-5 分，填入 CSV

## 评分维度

### Content Richness (CR) — 内容丰富度
- **5:** 多个章节，每个深入讲解不同子概念，有准确的解释、例子、概念间的联系
- **4:** 覆盖较好，有几个有意义的章节，内容准确，细节略有不足
- **3:** 覆盖了基础知识，部分章节较浅或重复
- **2:** 内容单薄，只有 1-2 个简单段落，或大量填充内容
- **1:** 几乎没有有意义的内容，空白、占位文本或完全跑题

### Interaction Design (ID) — 交互设计质量
- **5:** 多种交互元素（滑块、动画、模拟、测验），与教学内容紧密结合，帮助理解静态文本无法传达的概念
- **4:** 有几个相关的交互元素，大部分有明确的教学目的
- **3:** 有一些交互，但比较通用（如点击展开），与核心概念关联不紧密
- **2:** 交互很少，可能只有一个按钮或简单交互，教学价值有限
- **1:** 没有交互，或交互完全无效/无意义

### Visual Quality (VQ) — 视觉质量
- **5:** 专业、精致的布局，清晰的视觉层次，一致的配色，易读易导航
- **4:** 布局良好，可读性好，有轻微的视觉不一致
- **3:** 功能性布局，但视觉上较平淡或略显杂乱
- **2:** 布局混乱，间距不当，字体/颜色不一致，难以阅读
- **1:** 没有样式，原始 HTML 外观，布局破碎或无法使用

## 注意事项
- 请独立评估，不要与其他评估者讨论
- 如有特殊情况请在 notes 列说明
- 每个文档大约需要 2-3 分钟
"""


def main():
    parser = argparse.ArgumentParser(description="Generate human evaluation sheets")
    parser.add_argument("--evaluators", type=int, default=3)
    args = parser.parse_args()
    generate_sheets(args.evaluators)


if __name__ == "__main__":
    main()
