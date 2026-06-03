---
description: Distill a real interactive webpage into a ViviDoc template. Fetches the URL, extracts its interaction patterns and visual style into SRTC format, and saves as a reusable template in the library.
---

You are extracting interaction and style patterns from a real explorable explanation webpage.
The goal: understand how it works, distill it into SRTC format, and save as a named template
so future `/vividoc` runs can reference it.

## Input
`$ARGUMENTS`: the URL to learn from, followed by an optional template name.
Example: `/vividoc-learn https://ncase.me/trust/ social-game`

If no URL provided, ask the user for one.
If no template name provided, infer a short slug from the page title.

---

## Step 1 — Fetch the page

Use WebFetch to retrieve the URL. Also try fetching the page source if the tool supports it.

---

## Step 2 — Analyze: interaction patterns

From the page content, identify:

**Which of the 8 interaction types is dominant?**
(Parameter Exploration / State Switching / Direct Manipulation / Freeform Construction /
Temporal Control / Inspection / Spatial Navigation / Scroll-driven Narrative)

If multiple, identify the primary and secondary.

**State variables** — What does the user control? What is derived?

**Render** — What visual elements are present?

**Transition** — What happens when the user interacts?

**Constraint** — What is the key pedagogical insight being demonstrated?

---

## Step 3 — Analyze: visual style

From the CSS and HTML, extract:

1. **Color palette** — background, text, accent(s), interactive element colors
2. **Typography** — font families, sizes, weights used for headings vs. body
3. **Layout** — card-based? full-bleed? sidebar? centered column width?
4. **Decoration style** — minimal / geometric / data-rich / editorial
5. **Animation aesthetic** — snappy / smooth / physics-based / none
6. **Key CSS patterns** — extract 5–10 characteristic CSS rules that define the style

Write a `style_notes.md` summarizing the above in plain language.

---

## Step 4 — Create a minimal reference HTML

Write a compact, self-contained HTML file (~200 lines) that:
- Demonstrates the interaction pattern using a simplified but representative example
- Uses the distilled CSS style (colors, fonts, layout)
- Is clean and readable as a code reference
- Includes comments explaining key implementation choices

This file will be used by future `/vividoc` runs as a style+code template.

---

## Step 5 — Save to the template library

Create directory: `benchmark/datasets/interaction_examples/<template_name>/`

Save:
- `spec.json` — the SRTC spec extracted from this page
- `reference.html` — the minimal reference HTML from Step 4
- `style_notes.md` — the visual style analysis from Step 3

`spec.json` format:
```json
{
  "category": "<primary interaction type>",
  "source_url": "<original URL>",
  "topic": "<what concept this page teaches>",
  "style": "<one-line style description, e.g. 'dark editorial with amber accents'>",
  "srtc": {
    "S": { ... },
    "R": [ ... ],
    "T": [ ... ],
    "C": "..."
  }
}
```

---

## Step 6 — Report

```
✅ Template saved: benchmark/datasets/interaction_examples/<template_name>/

Interaction type:  <category>
Style:             <one-line style description>
Source:            <URL>

Files:
  spec.json       — SRTC specification
  reference.html  — Minimal reference implementation
  style_notes.md  — Visual style guide

To use this style in your next document:
  /vividoc "<topic>" → choose "custom" style → reference <template_name>
```

---

## Notes

- Focus on extracting patterns, not copying code. The reference.html should be original.
- If the page is complex (many interactions), focus on the most pedagogically interesting one.
- The `C` (constraint) field is the most important: what's the "aha moment" this page delivers?
- If the page source is behind JavaScript rendering and you can't see the code, describe the
  visual patterns from what you can observe and note the limitation.
