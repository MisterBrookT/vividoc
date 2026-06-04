# ViviDoc

**ViviDoc** generates interactive educational documents — explorable explanations — from a single topic input. Given a topic, it produces a self-contained HTML file with text, math (KaTeX), and interactive visualizations.

[![ACL 2026 Demo](https://img.shields.io/badge/ACL_2026-System_Demonstrations-blue?style=flat-square)](https://arxiv.org/abs/2603.27991)

**[Demo](https://vividoc.vercel.app/)** · **[Paper](assets/paper.pdf)** · **[arXiv](https://arxiv.org/abs/2603.27991)**

---

## Usage

### Claude Code (recommended — no API key needed)

ViviDoc ships as two Claude Code skills. Claude Code is the model — no external API calls.

```
/vividoc Fourier Transform
```

Claude Code reasons about the topic's character, designs a custom visual style, plans a DocSpec, then writes the HTML directly. Output: `outputs/fourier_transform/document.html`

```
/vividoc-learn https://example.com/some-explorable
```

Fetches the page, distills its interaction patterns and visual style into a reusable template, saves to `benchmark/datasets/interaction_examples/`.

### CLI (batch / research mode)

```bash
pip install uv && uv sync --dev
export OPENROUTER_API_KEY="sk-or-..."

vividoc run "Fourier Transform" openrouter/google/gemini-2.5-pro
vividoc run "Fourier Transform" openrouter/google/gemini-2.5-pro \
  --text-style "Conversational, concrete analogies" \
  --interaction-style "Dark background, bright accents"

# Stage by stage
vividoc plan "Fourier Transform" openrouter/google/gemini-2.5-pro -o spec.json
vividoc exec spec.json openrouter/google/gemini-2.5-pro
```

---

## How It Works

Each document is decomposed into **knowledge units** via the **Document Specification (DocSpec)**. Every unit has a text description and an **SRTC Interaction Spec** — State · Render · Transition · Constraint — that expresses what the learner should discover, independently from any code.

```
Topic
  │
  ▼ Plan  →  DocSpec (SRTC specs per section)
  │
  ▼ Execute  →  Stage 1: text  ·  Stage 2: interactive JS
  │
  ▼ Evaluate  →  document.html
```

---

## Interaction Taxonomy

ViviDoc's interaction design is grounded in **482 interaction instances** across 101 real-world explorable explanations from 63 websites and 11 domains (ViviBench):

| Type | When to use |
|---|---|
| Parameter Exploration | Slider → continuous variable effect |
| State Switching | Discrete modes → qualitatively different results |
| Direct Manipulation | Drag objects; spatial relationships are the concept |
| Freeform Construction | Build structure to observe emergent behavior |
| Temporal Control | Play/pause/scrub through a time-indexed concept |
| Inspection | Hover to reveal spatial structure |
| Spatial Navigation | Inherently 3D; rotate/pan/zoom |
| Scroll-driven Narrative | Linear progression reveals the concept |

Reference implementations (HTML + SRTC spec + style guide) for all 8:
`benchmark/datasets/interaction_examples/`

---

## Structure

```
.claude/commands/        # Claude Code skills (vividoc, vividoc-learn)
prompts/                 # LLM prompt templates (planner, executor, evaluator, styler)
vividoc/core/            # Pipeline: planner, executor, evaluator, runner, styler
vividoc/utils/llm/       # LLM client + provider adapters
benchmark/
├── datasets/
│   ├── interaction_examples/   # 8 reference cases (HTML + SRTC spec + style guide)
│   └── prepped/                # ViviBench — 101-topic evaluation dataset
├── baselines/                  # Comparison baselines (AutoGen, CAMEL, MetaGPT, naive)
└── evals/                      # Automated evaluation scripts
frontend/                # React web UI (optional demo interface)
```

---

## Citation

```bibtex
@article{tang2026vividoc,
  title   = {ViviDoc: Generating Interactive Documents through Human-Agent Collaboration},
  author  = {Tang, Yinghao and Xie, Yupeng and Feng, Yingchaojie and Lan, Tingfeng and Lao, Jiale and Cheng, Yue and Chen, Wei},
  journal = {arXiv preprint arXiv:2603.27991},
  year    = {2026}
}
```

---

MIT License
