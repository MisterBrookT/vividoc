# ViviDoc — Project Guide for Claude Code

ViviDoc generates **interactive educational documents** (explorable explanations) from any topic.
Given a topic, it produces a single self-contained HTML file with text, math (KaTeX), and interactive
visualizations, without requiring a browser build step.

The codebase is a Python pipeline. You (Claude Code) are the harness: you talk to the user,
decide which stages to run, and call the CLI or Python API as needed.

---

## Quick Start

```bash
# Install
uv sync --dev

# Set API key (OpenRouter covers most models; Anthropic direct also works)
export OPENROUTER_API_KEY="sk-or-..."
# or: export ANTHROPIC_API_KEY="sk-ant-..."

# Generate a document
vividoc run "Fourier Transform" openrouter/google/gemini-2.5-pro

# Output: outputs/fourier_transform/vividoc_gemini-2.5-pro/document.html
```

Open `document.html` directly in a browser — no server needed.

---

## Architecture

```
Topic (string)
    │
    ▼
┌─────────────┐     spec.json
│   Planner   │ ──────────────────────────────────────────┐
│  (SRTC spec)│                                           │
└─────────────┘                                           │
                                                          ▼
                                              ┌─────────────────────┐
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
vividoc eval output/generated_doc.json openrouter/google/gemini-2.5-pro
```

---

## Key Files

| Path | Purpose |
|------|---------|
| `vividoc/core/runner.py` | Orchestrates plan → exec → eval |
| `vividoc/core/planner.py` | Calls LLM to produce DocumentSpec |
| `vividoc/core/executor.py` | Fragment-based HTML generation (Stage 1 text, Stage 2 interactive) |
| `vividoc/core/evaluator.py` | Coherence and rendering validation |
| `vividoc/core/styler.py` | Generates style dimension options from spec content |
| `vividoc/core/models.py` | Pydantic models: DocumentSpec, KnowledgeUnitSpec, InteractionSpec |
| `vividoc/core/config.py` | RunnerConfig dataclass |
| `prompts/planner_prompt.py` | Planner system prompt with SRTC examples |
| `prompts/executor_prompt.py` | Executor prompts with 8-category interaction taxonomy |
| `prompts/styler_prompt.py` | Styler prompt for generating style dimensions |
| `vividoc/utils/llm/client.py` | LLMClient wrapping provider callers |
| `vividoc/cli.py` | Typer CLI entry points |

---

## The SRTC Interaction Spec

Every knowledge unit has an `interaction_spec` with four fields:

```
S — State:      variables (user-controlled or derived)
R — Render:     list of visual elements
T — Transition: list of cause→effect interaction rules  ([] = static, no interaction needed)
C — Constraint: the pedagogical invariant to highlight
```

**Interaction is not mandatory.** If `T = []`, the executor creates a beautiful static or
auto-animated visualization without user controls.

---

## 8 Interaction Categories

These are derived from 482 interactions across 101 real-world explorable explanations.
Each category has a reference example in `benchmark/datasets/interaction_examples/<category>/`.

| # | Category | When to use | Ref example |
|---|----------|-------------|-------------|
| 1 | **Parameter Exploration** | Slider adjusts continuous variable → effect updates | Lorenz Attractor (σ, ρ sliders) |
| 2 | **State Switching** | Discrete configs produce qualitatively different results | Quantum Orbitals (1s / 2p / 3d) |
| 3 | **Direct Manipulation** | Drag objects; spatial relationships are the concept | Geometric Optics (drag lens/object) |
| 4 | **Freeform Construction** | User builds structure to observe emergent behavior | Neural Network (click-to-place neurons) |
| 5 | **Temporal Control** | Concept has a time dimension; play/pause/scrub | Fourier Epicycles (play + harmonic slider) |
| 6 | **Inspection** | Spatial structure explored by hovering | Voronoi Tessellation (hover highlights cell) |
| 7 | **Spatial Navigation** | Inherently 3D; rotate/pan/zoom | Möbius Strip (drag to rotate 3D mesh) |
| 8 | **Scroll-driven Narrative** | Linear progression reveals concept | Entropy (scroll removes wall, particles mix) |

Read the full specs: `benchmark/datasets/interaction_examples/*/spec.json`

---

## Running as a Harness (Recommended)

You are Claude Code — you ARE the model. No external API calls are needed.

### Skills (primary workflow)

Two Claude Code skills are provided in `.claude/commands/`:

| Command | What it does |
|---------|-------------|
| `/vividoc [topic]` | Interactive document generation: ask style → plan → write HTML directly |
| `/vividoc-learn <url> [name]` | Distill a real interactive page into a reusable template |

**`/vividoc` workflow:**
1. Ask for topic (if not provided) and style preferences
2. Read `CLAUDE.md` + relevant templates for context
3. Generate `spec.json` (SRTC-formatted knowledge units)
4. Create HTML skeleton via `vividoc/utils/html/template.py`
5. For each section: write text (Stage 1) + interactive JS (Stage 2) directly
6. Output: `outputs/<topic_slug>/document.html`

**`/vividoc-learn` workflow:**
1. Fetch the URL
2. Analyze interaction type, state variables, visual style
3. Write a minimal reference HTML + SRTC spec + style notes
4. Save to `benchmark/datasets/interaction_examples/<name>/`
5. Template is immediately available for future `/vividoc` runs

### Template library

`benchmark/datasets/interaction_examples/` contains reference cases, each with:
- `spec.json` — SRTC spec + optional `"style"` key describing the visual aesthetic
- `*.html` or `reference.html` — runnable HTML demonstrating the pattern
- `style_notes.md` — visual style guide (added by `/vividoc-learn`)

The 8 built-in cases cover the full interaction taxonomy. Add more with `/vividoc-learn`.

### Batch / research mode (CLI with external LLM)

The Python pipeline still works for benchmarking and batch generation:

```bash
vividoc run "<topic>" openrouter/google/gemini-2.5-pro \
  --output-dir outputs \
  --text-style "Use a conversational tone" \
  --interaction-style "Dark background, bright accents"
```

Individual stages:
```bash
vividoc plan "<topic>" openrouter/google/gemini-2.5-pro -o spec.json
vividoc exec spec.json openrouter/google/gemini-2.5-pro --text-style "..."
```

Resume partial runs: `--resume` skips already-completed sections.

---

## Style System

`Styler.generate_options(spec, model)` calls the LLM to produce style dimensions relevant to the
specific topic. Example output:

```json
{
  "text_dimensions": [
    {"id": "tone", "label": "Tone", "options": [
      {"id": "conversational", "label": "Conversational", "description": "Friendly, uses 'you', concrete examples"},
      {"id": "academic", "label": "Academic", "description": "Precise terminology, formal register"}
    ]}
  ],
  "interaction_dimensions": [
    {"id": "visual_complexity", "label": "Visual Complexity", "options": [
      {"id": "minimal", "label": "Minimal", "description": "Clean, lots of whitespace"},
      {"id": "rich", "label": "Rich", "description": "Dense annotations, multiple panels"}
    ]}
  ]
}
```

Style instructions are free-form strings injected into executor prompts.

---

## Supported Models

Any `provider/model-name` format. Examples:

```
openrouter/google/gemini-2.5-pro
openrouter/google/gemini-2.5-flash
openrouter/anthropic/claude-sonnet-4-5
openrouter/qwen/qwen3-235b-a22b
anthropic/claude-sonnet-4-5          # direct Anthropic (requires ANTHROPIC_API_KEY)
```

Set the corresponding env var (`OPENROUTER_API_KEY` or `ANTHROPIC_API_KEY`).

---

## Development

```bash
# Run tests
uv run pytest

# Lint / format
uv run ruff check .
uv run ruff format .

# Run benchmark evaluation
uv run python benchmark/run.py

# Run with web UI (optional, for style selection UI)
vividoc serve           # backend at :8000
cd frontend && npm install && npm run dev    # frontend at :5173
```

### Adding a new LLM provider

1. Create `vividoc/utils/llm/callers/<provider>_caller.py` implementing `LLMCaller`
2. Register it in `vividoc/utils/llm/caller_registry.py`
3. Add the env var to `.env.example`

### Improving generation quality

- **Planner quality**: edit `prompts/planner_prompt.py` — add more SRTC examples, tighten constraints
- **Executor quality**: edit `prompts/executor_prompt.py` — add code patterns per interaction type
- **Reference examples**: `benchmark/datasets/interaction_examples/` has 8 gold HTML+spec pairs

---

## Project Structure

```
vividoc/
├── core/           # Pipeline logic (runner, planner, executor, evaluator, styler)
├── entrypoint/     # FastAPI web server (optional UI backend)
├── utils/
│   ├── llm/        # LLM client + provider callers
│   └── html/       # HTML template + validator
├── prep/           # Dataset preparation scripts
└── cli.py          # CLI entry points

prompts/            # LLM prompt templates (separate from vividoc/ for easy editing)
benchmark/
├── datasets/
│   ├── interaction_examples/  # 8 gold examples (one per interaction category)
│   ├── prepped/               # 101-topic dataset
│   └── raw/                   # Raw scraped data
├── baselines/      # Comparison baselines (naive, AutoGen, CAMEL, MetaGPT)
└── evals/          # Evaluation scripts (functional, LLM-as-judge, human eval)

frontend/           # React web UI (optional; primarily for demos)
homepage/           # Project homepage (deployed to Vercel)
assets/             # Paper PDF, demo screenshots
docs/               # Design docs, method notes, interaction specs
```
