# ViviDoc — Method Overview

## Primary Workflow: Claude Code Harness

The primary way to use ViviDoc is as a Claude Code skill. Claude Code is the model — no external API calls or backend server required.

```
/vividoc Fourier Transform
```

Claude reasons about the topic's character, designs a custom visual style, plans a DocSpec with SRTC specs per section, then writes the complete HTML file directly.

### How the skill works

```
Topic
  │
  ▼ Style Design
  │   Emotional register → background color
  │   Domain             → typography
  │   Concept            → accent color (one-accent rule)
  │
  ▼ Interaction Design (per knowledge unit)
  │   "What is the single most important thing to discover?"
  │   → SRTC spec (State · Render · Transition · Constraint)
  │   → interaction category (parameter exploration, temporal control, etc.)
  │
  ▼ Plan → spec.json (3–4 knowledge units)
  │
  ▼ Scaffold → document.html skeleton (via create_document_skeleton)
  │
  ▼ Generate (per KU)
      Stage 1: text content (<p>, KaTeX)
      Stage 2: interactive JS + scoped CSS (IIFE, #ku{n}- prefix)
```

Output: `outputs/<slug>/document.html` — a single self-contained HTML file, no build step.

---

## Secondary Workflow: Python CLI (batch / research mode)

The Python pipeline is used for benchmarking and batch generation with external LLMs via OpenRouter or Anthropic direct.

```bash
vividoc run "Fourier Transform" openrouter/google/gemini-2.5-pro
```

### Architecture

```
Topic (string)
    │
    ▼
┌─────────────┐     spec.json
│   Planner   │ ──────────────────────────────────────────┐
│  (SRTC spec)│                                           │
└─────────────┘                                           │
                                              ┌───────────▼─────────┐
                                              │      Executor       │
                                              │  Stage 1: text      │
                                              │  Stage 2: JS/HTML   │
                                              └──────────┬──────────┘
                                                         │ document.html
                                                         ▼
                                              ┌─────────────────────┐
                                              │     Evaluator       │
                                              │  coherence check    │
                                              └─────────────────────┘
```

Stages can be run independently:

```bash
vividoc plan "Fourier Transform" openrouter/google/gemini-2.5-pro -o spec.json
vividoc exec spec.json openrouter/google/gemini-2.5-pro
vividoc eval output/doc.json openrouter/google/gemini-2.5-pro
```

---

## Document Specification (DocSpec)

Every document is decomposed into **knowledge units**. Each unit has:

- `unit_content` — the learning objective (one sentence)
- `text_description` — what the text section should convey
- `interaction_spec` — SRTC spec (see below)

### SRTC Interaction Spec

```
S — State:      variables (user-controlled or derived)
R — Render:     list of visual elements
T — Transition: list of cause→effect interaction rules  ([] = static)
C — Constraint: the pedagogical invariant to highlight
```

See `docs/interaction_spec_formalization.md` for full design rationale and examples.

---

## Interaction Taxonomy

Derived from 482 interactions across 101 real-world explorable explanations (ViviBench):

| Category | When to use |
|---|---|
| Parameter Exploration | Slider adjusts continuous variable |
| State Switching | Discrete modes produce qualitatively different states |
| Direct Manipulation | Drag objects; spatial relationships are the concept |
| Freeform Construction | User builds structure to observe emergence |
| Temporal Control | Concept has a time dimension; play/pause/scrub |
| Inspection | Spatial structure explored by hovering |
| Spatial Navigation | Inherently 3D; rotate/pan/zoom |
| Scroll-driven Narrative | Linear progression reveals concept |

**Static is not a fallback.** When `T = []`, the executor creates a beautiful static visualization. A well-designed static diagram beats a contrived interactive one.

Reference HTML + SRTC spec + style guide for all 8: `benchmark/datasets/interaction_examples/`

---

## Web UI Demo (Legacy)

A React + FastAPI web interface exists in `frontend/` and `vividoc/entrypoint/`. It is deployed at `https://vividoc.vercel.app/` and used in the paper's evaluation. It calls external LLMs via the Python pipeline. See `frontend/README.md` for details.

For new work, prefer the Claude Code skill (`/vividoc`) — it is faster, requires no API key, and produces better results through direct reasoning.
