---
description: Generate an interactive educational document from any topic. Derives a custom visual style from the topic's character, designs SRTC-based interactions, then writes a self-contained HTML file directly.
---

## Input
`$ARGUMENTS`: topic string. If empty, ask the user.

---

## 1 — Style Design

Reason through these questions to synthesize a custom CSS palette.
Do not load any files yet — use the reasoning framework below.

**Background: default light, justify dark**

Default to a light or near-white background (`#f9f9f7` or `#ffffff`). Use a dark background only when the topic has a strong natural association with darkness — chaos/strange attractors, astrophysics, entropy, cryptography, terminal systems. When in doubt, go light. A wrong dark background looks dramatic; a wrong light background just looks clean.

| Topic character | Background |
|---|---|
| Physics instruments, chaos, space, entropy | Dark (#0d0d10 or similar near-black) |
| Formal math, biology, economics, social | Light (#f9f9f7 or white) |
| CS algorithms, ML, data | Light with high-contrast accents |
| Waves, signals, audio | Light or dark depending on whether it evokes an oscilloscope |

**Page frame rule — zero decoration**

The page frame (margins, separators, cards) must be invisible. No ornamental borders, colored `border-top`/`border-left` stripes, double-line dividers, letter-spacing ornaments, or shadow effects on page containers. Decoration lives inside the visualization canvas only. The accent color must not appear on structural page elements — only on interactive controls, annotations, and live readouts inside the widget.

**Domain → typography**
- Physics/engineering → monospace readouts (Space Mono) for numeric displays; sans-serif body
- Formal math/biology → serif body (Merriweather or similar) signals scholarship
- CS/ML/data → clean sans-serif throughout (Inter or similar)
- Avoid decorative display fonts on body text

**Concept → accent color**
Choose a color with a natural semantic tie to the concept:
- Light / optics → green (laser, phosphor)
- Quantum / probability → purple or gold
- Heat / irreversibility → red-orange
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

**Interaction integrity test** — before finalizing any interaction, answer:
> "If I removed the interaction and showed a static image instead, what insight would the learner LOSE?"

If the answer is "not much", redesign or make it static. The interaction must be the only way to convey the concept — not a decoration on top of a concept that could be stated in one sentence.

**Two high-value patterns beyond the 8 categories:**

*Reveal on Demand*: Show the initial state first. Let the user trigger the transformation (click a button, press play). The contrast between before and after creates the aha moment. Use whenever the concept is "what changes when X happens".

*Juxtaposition*: Render the same data/system side-by-side under two parameter values simultaneously. The learner sees the difference without needing to remember "what it looked like before". Use whenever the concept is "how sensitive is Y to X".

**Concrete → Abstract ordering**: Always structure knowledge units so the first section uses the most concrete, smallest example. Complexity grows across sections. Never open with the general formula — open with the specific case that builds the intuition.

**For each knowledge unit**, write the SRTC spec:
- `state`: name each variable, specify control type or "derived"
- `render`: list every visible element as a concrete description
- `transition`: one rule per user action ("dragging X changes Y")
- `constraint`: the invariant stated precisely and measurably — this is the answer to the integrity test above

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

**Writing philosophy — interaction first, explanation second.**

Every section follows this exact order:
1. **Section header** — brief, e.g. `01 — Concept Name`
2. **Interactive widget** — immediately, no preamble
3. **Caption** (plain text, small font, directly under the widget — no colored box):
   - *How*: one imperative sentence per control — "Drag [X] to change [Y]."
   - *What to notice*: one sentence pointing to the constraint — "Watch [Z] approach [limit]."
4. **Insight** (1–3 short prose sentences, **conclusion first**):
   - Open with the key finding, not the setup
   - Follow with one implication or surprising fact
   - Close with a bridge to the next section (last section omits this)

**Typography rules:**
- **Prose only** for core explanations. No `<ul><li>` bullet lists. No `<ol>` numbered lists. Lists are for reference tables only (e.g., parameter glossaries).
- Use `<strong>` to bold key terms inline — not to create fake headings inside paragraphs.
- No colored callout boxes, no `background: accent` info blocks, no colored `border-left` highlights. Let the prose carry the emphasis.
- Short paragraphs: 2–3 sentences maximum. Break at every logical shift.
- Max ~60 words of prose per section. The interaction carries the explanation.

**Voice rules:**
- Conclusion first. Never build to the point — state it, then support it.
- Short sentences. Active voice. Second person ("you", "notice", "try").
- No filler: delete "In this section we will…", "It can be seen that…"
- No hedging: "typically", "in most cases" → remove unless genuinely necessary.

For each knowledge unit, in order:

**Stage 1 (text):** Write the caption + insight only (not a full introduction).
Tone should match the visual register (dark/precise → terse; vivid → one sharp analogy).

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
