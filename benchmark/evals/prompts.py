"""Rubric prompts for LLM-as-Judge evaluation.

Three dimensions, each scored 1-5 with detailed anchor descriptions.
"""

JUDGE_SYSTEM = """\
You are an expert evaluator of interactive educational documents.
You will be given a topic and an HTML document (and optionally a screenshot).
Rate the document on the specified dimension using the rubric below.
Be strict and objective. Output valid JSON only."""

CONTENT_RICHNESS_PROMPT = """\
Evaluate the **Content Richness** of this interactive educational document.
Focus ONLY on the textual/educational content — ignore styling, layout, and interactivity.

Topic: {topic}

## Rubric
- **5 (Excellent):** Covers the topic with outstanding depth and breadth. Multiple well-developed sections, each exploring a distinct sub-concept. Includes accurate explanations, examples, and connections between ideas.
- **4 (Good):** Covers the topic well with several meaningful sections. Content is accurate and reasonably detailed, with minor gaps in depth or breadth.
- **3 (Adequate):** Covers the basics of the topic. Some sections may be shallow or repetitive. Content is mostly accurate but lacks depth.
- **2 (Poor):** Superficial coverage. Only 1-2 thin sections, or content is largely filler. May contain inaccuracies.
- **1 (Very Poor):** Minimal or no meaningful content. Mostly empty, placeholder text, or completely off-topic.

## Document Text Content (script/style removed)
```
{text_content}
```

Rate this document's Content Richness. Respond with JSON:
{{"score": <1-5>, "reason": "<one sentence justification>"}}"""

INTERACTION_DESIGN_PROMPT = """\
Evaluate the **Interaction Design Quality** of this interactive educational document.
Focus on whether the interactive elements are pedagogically meaningful — do they help the reader explore and understand the concept, or are they superficial?

Topic: {topic}

## Rubric
- **5 (Excellent):** Multiple diverse interactive elements (sliders, canvas animations, simulations, quizzes) that are semantically tied to the educational content. Interactions reveal insights that static text cannot.
- **4 (Good):** Several interactive elements that are relevant to the topic. Most interactions serve a clear educational purpose, with minor missed opportunities.
- **3 (Adequate):** Some interactive elements present, but they may be generic (e.g., click-to-reveal) or only loosely connected to the core concepts.
- **2 (Poor):** Minimal interactivity. Perhaps one button or a trivial interaction that adds little educational value.
- **1 (Very Poor):** No interactive elements, or interactions are broken/meaningless (e.g., buttons that do nothing relevant).

## HTML Source Code
```html
{html}
```

Rate this document's Interaction Design Quality. Respond with JSON:
{{"score": <1-5>, "reason": "<one sentence justification>"}}"""

VISUAL_QUALITY_PROMPT = """\
Evaluate the **Visual Quality** of this interactive educational document.
You are given both the HTML source code and a screenshot of the rendered page.

Topic: {topic}

## Rubric
- **5 (Excellent):** Professional, polished layout. Clear visual hierarchy (headings, sections, spacing). Consistent color scheme. Responsive design. Easy to read and navigate.
- **4 (Good):** Well-organized layout with good readability. Minor visual inconsistencies but overall pleasant appearance.
- **3 (Adequate):** Functional layout but visually plain or somewhat cluttered. Basic styling present but lacks polish.
- **2 (Poor):** Disorganized layout. Poor spacing, inconsistent fonts/colors, or hard to read. Looks unfinished.
- **1 (Very Poor):** No meaningful styling. Raw HTML appearance, broken layout, or visually unusable.

## HTML Source Code
```html
{html}
```

Rate this document's Visual Quality based on the screenshot and code. Respond with JSON:
{{"score": <1-5>, "reason": "<one sentence justification>"}}"""
