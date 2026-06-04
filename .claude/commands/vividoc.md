---
description: Generate an interactive educational document from any topic. Derives a custom visual style from the topic's character, designs SRTC-based interactions, then writes a self-contained HTML file directly.
---

## Input
`$ARGUMENTS`: topic string. If empty, ask the user.

---

## 1 — Style Design

Reason through these questions to synthesize a custom CSS palette.
Do not load any files yet — use the reasoning framework below.

**Emotional register → background choice**
- Precise / cold / rigorous (physics, formal math, systems) → dark background
- Elegant / abstract / spatial (topology, geometry) → light or glass
- Playful / constructive / agentic (algorithms, ML) → vivid or high-contrast
- Narrative / grave / inevitable (entropy, history, ethics) → near-black or muted

**Domain → typography**
- Physics/engineering → monospace readouts (Space Mono) signal instrument output
- Formal math/history → serif body (Merriweather) signals scholarship
- CS/interactive → sans-serif or mixed; bold sans for buttons
- Music/waves/time → retro bitmap (VT323) if the aesthetic fits

**Concept → accent color**
Choose a color that has a natural semantic tie to the concept:
- Light / optics → green (laser, phosphor)
- Quantum / probability → purple or gold
- Heat / irreversibility → red
- Chaos / nonlinear dynamics → cyan
- Waves / music / signal → pink or magenta
- Data / information / networks → blue
- Construction / growth → lime or amber
- Space / geometry → sky blue or gold

**One-accent rule**: pick one accent color and use it for everything interactive.
Multiple accent colors dilute focus — the accent IS the concept's color.

**Information density → layout**
- Single relationship (one variable → one effect) → centered large canvas, generous whitespace, let the change speak
- Multi-state comparison (discrete mode switching) → side-by-side panels, differences visible at a glance
- Time-evolving trajectory → reserve space for history trails; never crowd the buffer region
- Complex system / emergent behavior → full-canvas priority; controls overlaid in corners
- Formula-heavy derivation → alternate text column and canvas column; math and visual must be co-visible

After reasoning, write down:
- `bg`: background hex, `card`: card/surface hex, `accent`: accent hex
- Font pair: heading font + body font
- 1-line description: "Dark laboratory — emerald on near-black, instrument readouts"

Show the user this proposal in 2 sentences and ask: "Continue, or adjust?"

---

## 2 — Interaction Design

For each knowledge unit, choose the interaction type that serves the concept.
Ask: **"What is the single most important thing for the learner to discover?"**
That's the `constraint` — design every element to make it unmissable.

**Choosing interaction type:**

| Concept character | Use |
|---|---|
| A continuous variable has a nonlinear effect | Parameter Exploration (slider) |
| Discrete modes produce qualitatively different states | State Switching (segmented button) |
| Spatial relationships are the concept | Direct Manipulation (drag on canvas) |
| The learner needs to build something to see emergence | Freeform Construction (click-to-place) |
| Time is the core dimension | Temporal Control (play/pause + slider) |
| The structure is already there; learner reveals it | Inspection (hover) |
| The concept is inherently 3D | Spatial Navigation (drag-rotate) |
| A linear progression must unfold in order | Scroll-driven Narrative |
| None of the above, or the concept is clearest as a diagram | Static (transition: []) |

**Static is not a fallback — it is sometimes the right answer.**
A well-designed static visualization beats a contrived interactive one.

**For each knowledge unit**, write the SRTC spec:
- `state`: name each variable, specify control type or "derived"
- `render`: list every visible element as a concrete description
- `transition`: one rule per user action ("dragging X changes Y")
- `constraint`: the invariant stated precisely and measurably

---

## 3 — Plan (spec.json)

Generate 3–4 knowledge units applying the above. Save to `outputs/<slug>/spec.json`.
Show a 3-line summary and ask if the user wants to adjust before generating.

---

## 4 — Scaffold

```bash
python -c "
import json, sys; sys.path.insert(0, '.')
from vividoc.core.models import DocumentSpec
from vividoc.utils.html.template import create_document_skeleton
spec = DocumentSpec.model_validate(json.load(open('outputs/<slug>/spec.json')))
create_document_skeleton(spec, 'outputs/<slug>/document.html')
"
```

Then replace the `<style>` block with the custom CSS from Step 1.

---

## 5 — Generate each section

For each knowledge unit, in order:

**Stage 1 (text):** Write `<p>` / `<strong>` / KaTeX HTML matching the text_description.
Tone should match the visual register (dark/precise → formal language; vivid → analogies).

**Stage 2 (interaction):** Write `<style>` + HTML + `<script>` (IIFE).
- All IDs: `ku{n}-` prefix. All CSS selectors: `#ku{n}` scoped.
- Style controls (sliders, buttons, readouts) consistently with the document palette.
- If you need a code reference for the interaction pattern, read the matching example:
  `benchmark/datasets/interaction_examples/<category>/` — look at the HTML for patterns,
  not the CSS (you already have a custom palette).
- Make the constraint visible: display its value as a live label, use color change on
  satisfied/violated state, annotate directly on the canvas.

Log each completed unit.

---

## 6 — Report

```
✅ outputs/<slug>/document.html

Style: <1-line description>
  ku1: <title>  [<type>]
  ku2: <title>  [<type>]
  ...

open outputs/<slug>/document.html
```
