---
description: Transform lecture slides, course notes, or a paper into a ViviDoc interactive document. Ingests the source (URL, file, or pasted outline), distills it into SRTC knowledge units, and writes a self-contained HTML file.
---

## Input
`$ARGUMENTS`: one of:
- A **URL** — course page, HTML slide deck, or paper abstract page
- A **local file path** — PDF, PPTX text export, Markdown, or plain text
- **Pasted slide titles / outline** directly in the argument

Optional: append a short output slug, e.g. `/vividoc-slides lecture.pdf eigenvalues`

If empty, ask the user for a source.

---

## 0 — Ingest the Source

**URL**: fetch the page. Look for slide headings, section structure, inline formulas, figure captions.

**File**: read the file. For a PDF, extract text page by page. For a PPTX text export, treat each slide heading as a bullet.

**Pasted text**: use as-is.

From whatever you receive, extract and record:

1. **Attribution** — author, course name/number, institution, year, lecture number if known.
2. **Slide inventory** — ordered list of slide titles or section headings with the core content of each.
3. **Key elements per section** — formulas, described diagrams, data tables, code snippets, worked examples, before/after comparisons.
4. **Pedagogical arc** — what is the progression? What does each section build on? What is the "aha" the lecture is building toward?

---

## 1 — Distill to Knowledge Units

Map the full lecture to **3–5 ViviDoc knowledge units**. Each unit = one idea the learner must discover hands-on.

**Mapping rules:**
- 3–6 slides on the same concept → one knowledge unit.
- Administrative, motivational, or bibliography slides → skip.
- A slide with a formula + a slide with a worked example → the formula is the SRTC constraint; the example drives the interactive widget.
- A slide sequence showing a "before → after" state change → use **Reveal on Demand** pattern.
- A slide that shows how output changes as a parameter varies → **Parameter Exploration**.
- A slide with a spatial diagram the learner should explore → **Direct Manipulation** or **Inspection**.

**Interaction integrity test** (required for every unit):
> "If I replaced this with a static image, what insight would the learner LOSE?"

If the answer is "not much" — make it static. A clean static diagram beats a contrived slider.

For each unit, note:
- Title (clear, concept-first)
- Source slides (e.g., "slides 12–17")
- Candidate interaction type
- The one constraint — the invariant the visualization must make unmissable

---

## 2 — Style Design

Same as `/vividoc` Step 1 (derive palette from topic domain).

**Credit the source** — add a subtitle line directly below the page title in muted text:
- Chinese lecture: `改编自 [作者]《[课程名]》第 N 讲`
- English lecture: `Adapted from [Author], [Course], Lecture N`
- Paper: `Based on [Author et al.], "[Title]" ([Year])`

The attribution must appear on the page — slides-based content is adapted work.

Show the user the proposed style + attribution in 2 sentences. Ask: "Continue, or adjust?"

---

## 3 — Plan (spec.json)

Generate 3–5 knowledge units in SRTC format. Save to `outputs/<slug>/spec.json`.

Show a 3-line summary including the source attribution. Ask if the user wants to adjust before generating.

---

## 4–6 — Scaffold → Generate → Report

Follow steps 4–6 from `/vividoc` exactly.

Output: `outputs/<slug>/document.html`

Report format:
```
✅ outputs/<slug>/document.html

Source: [attribution line]
Style:  <1-line description>
  ku1: <title>  [<type>]  ← slides N–M
  ku2: <title>  [<type>]  ← slides N–M
  ku3: <title>  [<type>]  ← slides N–M

open outputs/<slug>/document.html
```
