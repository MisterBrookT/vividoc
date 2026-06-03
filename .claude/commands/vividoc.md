---
description: Generate an interactive educational document (explorable explanation) from any topic. Asks about style, plans with SRTC specs, then writes a self-contained HTML file directly — no external API needed.
---

You are generating an interactive educational document using the ViviDoc pipeline.
You are the model — no external LLM calls are needed. Work directly.

## Input
`$ARGUMENTS`: optional topic string. If empty, ask the user.

---

## Step 1 — Gather inputs

If `$ARGUMENTS` is empty, ask:
> "What topic should I generate an interactive document for?"

Then use AskUserQuestion with two questions:

**Visual style** (pick one):
- `default` — Clean white background, indigo/purple accents, Poppins + Inter typography (see `vividoc/utils/html/template.py`)
- `dark-scientific` — Dark navy/black background, cyan/teal accents, monospace code aesthetic (see `benchmark/datasets/interaction_examples/parameter_exploration/`)
- `minimal` — White background, muted grays, generous whitespace, no decorative elements
- `custom` — Describe your own preference

**Tone** (pick one):
- `conversational` — Friendly, uses "you", concrete real-world analogies
- `academic` — Precise terminology, formal register
- `playful` — Engaging, storytelling, visual metaphors

---

## Step 2 — Read context

Before planning, read these files to load context:
- `CLAUDE.md` — architecture, SRTC format, 8 interaction categories
- `benchmark/datasets/interaction_examples/parameter_exploration/spec.json` — SRTC format example
- If the user chose `dark-scientific`, also read `benchmark/datasets/interaction_examples/parameter_exploration/` (the HTML file) for CSS reference

---

## Step 3 — Plan the document (generate spec.json)

Create a DocumentSpec with **3–4 knowledge units**. Follow `prompts/planner_prompt.py` for detailed guidance.

Key rules:
- Each knowledge unit needs: `id`, `unit_content`, `text_description`, `interaction_spec`
- `interaction_spec` uses SRTC: `state`, `render`, `transition`, `constraint`
- Choose the right interaction type from the 8 categories (CLAUDE.md)
- `transition: []` is valid — static visualizations are often better than forced controls
- `constraint` is the key pedagogical insight; make it specific and measurable

Compute the output directory:
```
outputs/<topic_slug>/
```
where `topic_slug` = topic lowercased, spaces → underscores, special chars removed.

Save: `outputs/<topic_slug>/spec.json`

Show the user a brief summary of the planned knowledge units and ask if they want to proceed or adjust.

---

## Step 4 — Create HTML skeleton

Run:
```bash
python -c "
import json, sys
sys.path.insert(0, '.')
from vividoc.core.models import DocumentSpec
from vividoc.utils.html.template import create_document_skeleton

spec = DocumentSpec.model_validate(json.load(open('outputs/$TOPIC_SLUG/spec.json')))
create_document_skeleton(spec, 'outputs/$TOPIC_SLUG/document.html')
print('Skeleton created')
"
```

If the user chose `dark-scientific`, after creating the skeleton, replace the `<style>` block with the dark theme CSS extracted from the parameter_exploration example HTML.

---

## Step 5 — Generate each knowledge unit

For each knowledge unit (ku1, ku2, …), in order:

### Stage 1: Text content

Write HTML paragraph content for the `<div class="text-content">` of this section.
- Use `<p>` tags, `<strong>`, `<em>`
- Use KaTeX inline math: `$formula$` or `$$formula$$`
- Follow the chosen tone
- Match the `text_description` from the spec

Insert into the HTML: find `<section id="ku{n}">`, find `<div class="text-content">`, replace its content.

### Stage 2: Interactive content

Write the complete interactive fragment for `<div class="interactive-content">`:
- `<style>` block — scoped with `#ku{n}` prefix
- HTML controls and canvas/container elements — all IDs prefixed `ku{n}-`
- `<script>` block — wrapped in IIFE `(function() { ... })()`

Follow `prompts/executor_prompt.py` for:
- Pattern matching by interaction type
- Constraint highlighting
- Static visualization handling (empty transition)

Available libraries: **D3.js**, **Chart.js** (loaded in template).

Reference the matching category example from `benchmark/datasets/interaction_examples/` for code patterns.

Insert into the HTML: find `<div class="interactive-content">` in `<section id="ku{n}">`, replace its content.

Log progress: `"[{n}/{total}] {unit_content} ✓"`

---

## Step 6 — Report

After all sections are complete:

```
✅ Document generated: outputs/<topic_slug>/document.html

To view: open outputs/<topic_slug>/document.html
         (or drag the file into a browser)

Sections:
  • ku1: <unit_content>  [<interaction type>]
  • ku2: <unit_content>  [<interaction type>]
  ...

Spec: outputs/<topic_slug>/spec.json
```

If the user wants to regenerate a specific section, they can edit `spec.json` and say
"regenerate ku2" — you can re-run Stage 1 + Stage 2 for just that section.
