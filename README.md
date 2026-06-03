# ViviDoc

**ViviDoc** generates interactive educational documents — explorable explanations — from a single topic input. It introduces the **Document Specification (DocSpec)**, a structured intermediate representation that bridges the gap between pedagogical intent and executable code.

**[Demo](https://vividoc.vercel.app/)** · **[Paper](assets/paper.pdf)** · **[Video](https://www.youtube.com/watch?v=rJrnPJLyHUI)**

---

## The Problem

Creating interactive articles requires both domain expertise and web development skills. Fully automatic generation with LLMs is uncontrollable — there is a fundamental gap between what an educator wants the learner to *experience* and the code that realizes that experience.

ViviDoc solves this with **human-agent collaboration through DocSpec**: a structured plan the educator can review and edit *before* any code is produced.

---

## How It Works

```
Topic
  │
  ▼ Planner
DocSpec  ← human review & edit
  │
  ▼ Executor (Stage 1: text · Stage 2: interactive JS)
document.html
  │
  ▼ Evaluator
validated output
```

The **DocSpec** decomposes each section into a knowledge unit with:
- A text description (guides writing)
- An **SRTC Interaction Spec** — State · Render · Transition · Constraint

The SRTC spec is the key abstraction: it expresses *what the learner should discover* (Constraint) and *how interaction reveals it* (State + Transition), independently from any code.

---

## Evaluation

Expert blind evaluation on 10 topics, scored on a 5-point Likert scale:

| Dimension | ViviDoc | Naive Agent |
|---|---|---|
| Content Richness | **4.17** | 2.07 |
| Interaction Quality | **4.00** | 2.40 |
| Visual Quality | **3.73** | 2.37 |

User study (n=3): Easy to learn 5.0 · Easy to use 5.0 · DocSpec editing intuitive 4.33.

*"DocSpec was the first time I could actually decide how the interaction works without writing any code."* — P1

---

## Interaction Taxonomy

ViviDoc's interaction design is grounded in 482 interactions across 101 real-world explorable explanations from 60+ websites and 11 domains. Eight categories emerged:

| Type | When to use |
|---|---|
| Parameter Exploration | Slider adjusts continuous variable → effect updates |
| State Switching | Discrete configs produce qualitatively different results |
| Direct Manipulation | Drag objects; spatial relationships are the concept |
| Freeform Construction | User builds structure to observe emergent behavior |
| Temporal Control | Concept has a time dimension; play/pause/scrub |
| Inspection | Spatial structure explored by hovering |
| Spatial Navigation | Inherently 3D; rotate/pan/zoom |
| Scroll-driven Narrative | Linear progression reveals concept |

Reference implementations (HTML + SRTC spec + style guide) for all 8 types:
`benchmark/datasets/interaction_examples/`

---

## Usage

### With Claude Code — no API key needed

ViviDoc ships as two Claude Code skills. Claude Code is the model.

```
/vividoc Fourier Transform
```

Claude Code reasons about the topic's character, designs a custom visual style, plans the DocSpec, then writes the HTML directly. Output: `outputs/fourier_transform/document.html`

```
/vividoc-learn https://example.com/some-explorable
```

Fetches the page, distills its interaction patterns and visual style into a new template, saves to `benchmark/datasets/interaction_examples/`.

### CLI — batch / research mode

```bash
export OPENROUTER_API_KEY="sk-or-..."

vividoc run "Fourier Transform" openrouter/google/gemini-2.5-pro
vividoc run "Fourier Transform" openrouter/google/gemini-2.5-pro \
  --text-style "Conversational, concrete analogies" \
  --interaction-style "Dark background, bright accents"

# Stage by stage
vividoc plan "Fourier Transform" openrouter/google/gemini-2.5-pro -o spec.json
vividoc exec spec.json openrouter/google/gemini-2.5-pro
```

### Setup

```bash
pip install uv && uv sync --dev
```

---

## Structure

```
.claude/commands/        # Claude Code skills (vividoc, vividoc-learn)
prompts/                 # LLM prompt templates
vividoc/core/            # Pipeline: planner, executor, evaluator, runner
vividoc/utils/llm/       # LLM client + provider adapters
benchmark/
├── datasets/
│   ├── interaction_examples/   # 8 reference cases (HTML + SRTC spec + style guide)
│   └── prepped/                # 101-topic dataset (paper evaluation)
├── baselines/                  # Naive agent + AutoGen + CAMEL + MetaGPT baselines
└── evals/                      # Expert evaluation + LLM-judge scripts
frontend/                # React web UI (optional demo interface)
```

---

## Citation

```bibtex
@inproceedings{vividoc2025,
  title     = {Demonstrating ViviDoc: Generating Interactive Documents through Human-Agent Collaboration},
  booktitle = {},
  year      = {2025}
}
```

---

MIT License
