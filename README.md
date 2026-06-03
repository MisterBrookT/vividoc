# ViviDoc

**ViviDoc** generates interactive educational documents — explorable explanations — from a single topic input through human-agent collaboration.

**[Demo](https://vividoc.vercel.app/)** · **[Paper](assets/paper.pdf)** · **[Video](https://www.youtube.com/watch?v=rJrnPJLyHUI)** · **[arXiv](https://arxiv.org/abs/2603.27991)**

---

## The Problem

Creating interactive articles requires both domain expertise and web development skills. Fully automatic LLM generation is uncontrollable — there is a fundamental gap between what an educator wants the learner to *experience* and the code that realizes it.

ViviDoc solves this with **three human control levels** that let non-programmers guide the generation process:

1. **DocSpec editing** — review and modify the structured plan before any code is produced
2. **Style Palette** — customize writing tone and visual style through LLM-generated options  
3. **Chat-based editing** — natural language refinement of spec and generated document

---

## How It Works

```
Topic
  │
  ▼ Planner
DocSpec  ◄── human review & edit (level 1)
  │       ◄── style preferences  (level 2)
  ▼ Executor  (Stage 1: text · Stage 2: interactive JS)
document.html  ◄── chat refinement (level 3)
  │
  ▼ Evaluator
validated output
```

The **Document Specification (DocSpec)** decomposes each section into a knowledge unit with a text description and an **SRTC Interaction Spec** — State · Render · Transition · Constraint — that expresses *what the learner should discover* independently from any code.

---

## Evaluation

Benchmarked on **ViviBench** — 101 topics from 63 real-world interactive documents across 11 domains.

**Automated evaluation** (4 dimensions, LLM-judge aligned with human ratings at Pearson r > 0.84):

| Method | Content Richness | Interaction Quality |
|---|---|---|
| **ViviDoc** | **1.00** | **0.92** |
| AutoGen (best baseline) | 0.53 | 0.64 |

Generation efficiency: **505 chars/s** (3.3× faster than AutoGen).

**User study** (n=12, 5-point Likert scale):

| Dimension | Score |
|---|---|
| Usability | 5.00 |
| DocSpec control | 4.50 |
| Chat editing | 4.67 |
| Output satisfaction | 4.58 |
| Intent to reuse | 4.75 |

---

## Interaction Taxonomy (ViviBench)

Grounded in **482 interaction instances** across 101 real-world explorable explanations from 63 websites and 11 domains:

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

## Usage

### With Claude Code — no API key needed

```
/vividoc Fourier Transform
```

Claude Code reasons about the topic's character, designs a custom visual style, plans the DocSpec, then writes the HTML directly. Output: `outputs/fourier_transform/document.html`

```
/vividoc-learn https://example.com/some-explorable
```

Fetches the page, distills its interaction patterns and visual style, saves to the template library.

### CLI — batch / research mode

```bash
pip install uv && uv sync --dev
export OPENROUTER_API_KEY="sk-or-..."

vividoc run "Fourier Transform" openrouter/google/gemini-2.5-pro
vividoc run "Fourier Transform" openrouter/google/gemini-2.5-pro \
  --text-style "Conversational, concrete analogies" \
  --interaction-style "Dark background, bright accents"
```

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
├── baselines/                  # Naive agent + AutoGen + CAMEL + MetaGPT
└── evals/                      # Automated evaluation (4-dimensional framework)
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
