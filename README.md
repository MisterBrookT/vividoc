# ViviDoc

ViviDoc turns any topic into an **interactive educational document** — a self-contained HTML file
combining explanatory text, math (KaTeX), and interactive visualizations.

**[Live Demo](https://vividoc.vercel.app/)** · **[Paper](assets/paper.pdf)**

![screenshot](assets/demo-screenshot.png)

---

## How It Works

ViviDoc uses a three-stage pipeline:

1. **Planner** — decomposes the topic into knowledge units, each with a structured interaction spec
   using the *SRTC framework* (State · Render · Transition · Constraint)
2. **Executor** — generates text and interactive JavaScript/HTML for each unit, fragment by fragment
3. **Evaluator** — checks coherence and rendering correctness

The output is a single `document.html` that runs entirely in the browser with no build step.

---

## Setup

```bash
# Python 3.11+ required
pip install uv
uv sync --dev

# Set your API key (OpenRouter gives access to many models)
export OPENROUTER_API_KEY="sk-or-..."
```

---

## Usage

### With Claude Code (recommended — no API key needed)

ViviDoc ships as two Claude Code skills. Claude Code is the model — no external API calls.

```
/vividoc Fourier Transform
```

Claude Code will ask about style preferences, plan the document, then write the HTML directly.
Output: `outputs/fourier_transform/document.html`

```
/vividoc-learn https://ncase.me/trust/ social-game
```

Fetches the page, distills its interaction patterns and visual style into a reusable template,
and saves it to `benchmark/datasets/interaction_examples/social-game/`.

### CLI (batch / research mode, requires API key)

```bash
export OPENROUTER_API_KEY="sk-or-..."

# Full pipeline
vividoc run "Fourier Transform" openrouter/google/gemini-2.5-pro

# With style instructions
vividoc run "Fourier Transform" openrouter/google/gemini-2.5-pro \
  --text-style "Conversational, concrete analogies" \
  --interaction-style "Dark background, bright accent colors"

# Stage by stage
vividoc plan "Fourier Transform" openrouter/google/gemini-2.5-pro -o spec.json
vividoc exec spec.json openrouter/google/gemini-2.5-pro
```

### Web UI (optional demo interface)

```bash
vividoc serve                                  # backend at http://localhost:8000
cd frontend && npm install && npm run dev      # frontend at http://localhost:5173
```

---

## 8 Interaction Types

ViviDoc's interaction taxonomy is derived from 482 interactions across 101 real-world explorable
explanations. Every generated visualization belongs to one of these categories:

| Type | Description | Reference Example |
|------|-------------|-------------------|
| **Parameter Exploration** | Sliders expose how a continuous variable shapes the system | Lorenz Attractor — σ/ρ sliders reshape the butterfly |
| **State Switching** | Discrete modes produce qualitatively different outcomes | Quantum Orbitals — switch between 1s, 2p, 3d clouds |
| **Direct Manipulation** | Drag objects whose spatial relations encode the concept | Geometric Optics — drag lens/object, watch rays update |
| **Freeform Construction** | Build a structure to observe emergent behavior | Neural Network — click to place neurons, see forward pass |
| **Temporal Control** | Play, pause, scrub through a time-dependent process | Fourier Epicycles — add harmonics, watch square wave emerge |
| **Inspection** | Hover to probe spatial structure without changing it | Voronoi — hover illuminates nearest cell and shows distance |
| **Spatial Navigation** | Rotate or pan an inherently 3D concept | Möbius Strip — drag to rotate, observe single-sided surface |
| **Scroll-driven Narrative** | Scroll advances a narrative variable linearly | Entropy — scroll removes wall, particles irreversibly mix |

Reference implementations (HTML + SRTC spec) for all 8 types are in
`benchmark/datasets/interaction_examples/`.

---

## Supported Models

Any model accessible via OpenRouter or directly via Anthropic:

```bash
openrouter/google/gemini-2.5-pro
openrouter/google/gemini-2.5-flash
openrouter/anthropic/claude-sonnet-4-5
openrouter/qwen/qwen3-235b-a22b
anthropic/claude-sonnet-4-5          # requires ANTHROPIC_API_KEY
```

---

## Using with Claude Code

See [CLAUDE.md](CLAUDE.md) for a complete guide on using Claude Code as an interactive harness
for ViviDoc — including style elicitation, iterative generation, and evaluation workflows.

---

## Project Structure

```
prompts/                 # LLM prompt templates
vividoc/core/            # Pipeline: planner, executor, evaluator, styler, runner
vividoc/utils/llm/       # LLM client + provider adapters
benchmark/
├── datasets/
│   ├── interaction_examples/   # 8 reference cases (HTML + SRTC spec)
│   └── prepped/                # 101-topic dataset used in the paper
├── baselines/                  # Comparison baselines
└── evals/                      # Evaluation scripts
frontend/                # Optional React web UI
homepage/                # Project homepage (vividoc.vercel.app)
```

---

## License

MIT
