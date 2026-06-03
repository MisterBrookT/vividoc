---
description: Generate an interactive educational document (explorable explanation) from any topic. Designs a custom visual style from topic character, plans with SRTC specs, then writes a self-contained HTML file directly — no external API needed.
---

You are generating an interactive educational document using the ViviDoc pipeline.
You are the model — no external API calls are needed. Work directly.

## Input
`$ARGUMENTS`: optional topic string. If empty, ask the user.

---

## Step 1 — Get the topic

If `$ARGUMENTS` is empty, ask:
> "What topic should I generate an interactive document for?"

---

## Step 2 — Load design vocabulary

Read ALL of these files before designing anything:

```
benchmark/datasets/interaction_examples/parameter_exploration/style_notes.md
benchmark/datasets/interaction_examples/state_switching/style_notes.md
benchmark/datasets/interaction_examples/direct_manipulation/style_notes.md
benchmark/datasets/interaction_examples/freeform_construction/style_notes.md
benchmark/datasets/interaction_examples/inspection/style_notes.md
benchmark/datasets/interaction_examples/spatial_navigation/style_notes.md
benchmark/datasets/interaction_examples/temporal_control/style_notes.md
benchmark/datasets/interaction_examples/scroll_driven_narrative/style_notes.md
```

These are not options to pick from — they are examples of how visual design should be
*derived from the character of a topic*. Read the "When to use" and "Design rationale"
sections carefully. Your goal is to design something new that fits this specific topic,
drawing from this vocabulary.

---

## Step 3 — Design the visual style

Reason about the topic's character across these dimensions:

**Emotional register**
- Cold / precise / rigorous → dark backgrounds, monochrome, technical fonts
- Warm / exploratory / playful → light or vivid backgrounds, rounded forms
- Mysterious / spatial / abstract → deep colors, dramatic contrast

**Domain character**
- Physics / engineering → instrument aesthetic (dark + single accent = oscilloscope/terminal)
- Formal mathematics → scholarly serif, structured, possibly academic antiquarian
- CS / algorithms → constructive, can be bold (neo-brutalist) or dark+precise
- Natural / emergent phenomena → organic palette, gradients, particle textures
- Time / dynamics / waves → retro/synthwave OR dark grid — anything that evokes motion
- Geometry / topology → clean and spatial, light or dark, no clutter

**Accent color logic**
What color is intrinsically associated with this concept?
- Optics / light → green (like a laser)
- Quantum / probability → purple or gold
- Heat / entropy / irreversibility → red
- Chaos / nonlinear → cyan / teal
- Biology / growth → green-yellow
- Networks / social systems → warm orange or amber
- Information / data → blue

**Tone decision**
Will the learner feel like they're: in a lab? reading a textbook? playing a game? gazing at space?
This should drive font choice, border style, and spacing.

---

After reasoning, synthesize a **custom CSS spec** with:
1. Background + card colors
2. Primary accent hex
3. Font pairing (headings + body + monospace if needed)
4. 2–3 characteristic CSS rules that define the aesthetic

Then briefly show the user the proposed style and ask for confirmation before proceeding:

> "**Proposed style:** [2-sentence description]. Palette: bg `#...`, accent `#...`.  
> Continue with this, or adjust?"

If the user suggests changes, revise and confirm again. If they approve, proceed.

---

## Step 4 — Plan the document (generate spec.json)

Read `CLAUDE.md` for SRTC format and interaction taxonomy.

Create a DocumentSpec with **3–4 knowledge units**. For each unit, design the interaction:

**Interaction design principles:**
- Match the interaction type to the concept's nature (see CLAUDE.md taxonomy)
- Ask: "what is the single most important thing for the learner to discover here?"
  That's the `constraint` — design the interaction to make it unmissable
- `transition: []` is correct when static is genuinely better than forced interaction
- Don't add controls just to have controls

Compute the output directory: `outputs/<topic_slug>/` (lowercase, spaces → underscores).

Save: `outputs/<topic_slug>/spec.json`

Show the user a 3-line summary of planned knowledge units. Ask if they want to adjust
any knowledge unit or interaction type before generating.

---

## Step 5 — Create HTML skeleton

```bash
python -c "
import json, sys
sys.path.insert(0, '.')
from vividoc.core.models import DocumentSpec
from vividoc.utils.html.template import create_document_skeleton
spec = DocumentSpec.model_validate(json.load(open('outputs/SLUG/spec.json')))
create_document_skeleton(spec, 'outputs/SLUG/document.html')
"
```

Then **replace the `<style>` block** in `document.html` with the custom CSS you designed in Step 3.
The template's default indigo theme is a starting point — override all colors, fonts, and
characteristic patterns with your custom design.

---

## Step 6 — Generate each knowledge unit

For each knowledge unit (ku1, ku2, …), in order:

### Stage 1: Text content

Write HTML for `<div class="text-content">`:
- `<p>` tags, `<strong>`, `<em>`
- KaTeX math: `$formula$` inline, `$$formula$$` display
- Tone should match the visual style (dark/technical → precise language; playful → analogies)
- Follow the `text_description` from spec

Insert: find `<section id="ku{n}">` → find `<div class="text-content">` → replace contents.

### Stage 2: Interactive content

Write the complete fragment for `<div class="interactive-content">`:

```
<style>  /* scoped with #ku{n} prefix */
<html>   /* controls + canvas — all IDs prefixed ku{n}- */
<script> /* IIFE */
```

**Style the interaction to match the document's visual design:**
- Sliders, buttons, and readouts should use the same palette/fonts as the rest of the document
- Don't use generic gray/blue browser defaults — style them consistently

Reference `benchmark/datasets/interaction_examples/<matching-category>/` for code patterns.
The matching category's HTML is the closest reference for implementation patterns —
but adapt the CSS to your custom design, don't copy it verbatim.

Log: `"[{n}/{total}] {unit_content} ✓"`

---

## Step 7 — Report

```
✅ Document generated: outputs/<topic_slug>/document.html

Open: open outputs/<topic_slug>/document.html

Style: <your 1-line style description>
Sections:
  • ku1: <unit_content>  [<interaction type>]
  • ku2: ...

To regenerate a section: edit spec.json and say "regenerate ku{n}"
```
