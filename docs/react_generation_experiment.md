# React Component Generation Experiment Record

## Overview
We conducted an experiment to replace the original vanilla JavaScript + D3.js/Chart.js interactive content generation approach with a modern stack based on **React + Tailwind CSS** loaded via CDN. 

The goal was to improve the visual aesthetics, maintainability, and code structure of LLM-generated interactive knowledge units. Additionally, we implemented a Playwright-based visual evaluator (`Critic`) using LLM Vision to validate visual rendering during the execution phase.

## Method
1. **HTML Template Update**: Modified `vividoc/utils/html/template.py` to include CDNs for:
   - React 18
   - ReactDOM
   - Babel standalone
   - Tailwind CSS
2. **Prompt Engineering Modifications**: Changed `FRAGMENT_STAGE2_PROMPT` in `prompts/executor_prompt.py` to instruct the LLM to output:
   - A `<script type="text/babel">` tag
   - A single cohesive React functional component
   - State management via `React.useState` and `React.useEffect`
   - UI styling exclusively using inline `className` via Tailwind CSS
3. **Visual Evaluator**: Introduced a Playwright testing hook inside `_evaluate_visual_full_page` in `Evaluator` (and initially in the Executor loop). It rendered the generated React code in an invisible browser window and took a screenshot, then fed the screenshot to a VLM (Vision Language Model) to verify the result aesthetically.

## Results & Findings
Unfortunately, the experiment did not achieve the expected improvement and introduced several regressions, leading to its reversion.

1. **Rendering Delays and Instability**:
   - Because we relied on `@babel/standalone` to parse `text/babel` tags on the fly in the browser, there was a noticeable spike in compilation latency.
   - The front end could not immediately render the live previews during the generation phase. Instead, it showed a lag before React components flashed onto the screen, leading to a poor "リアルタイム" (real-time realtime streaming) user experience.
2. **LLM Hallucinations on Complex State**:
   - While the LLMs excelled at generating isolated static Tailwind components, they struggled to correctly wire up complex interactive visual constraints (such as geometry coordinates for diagrams or complex data binding) compared to the mature DOM manipulation APIs found in D3.js.
   - Code sometimes resulted in silent React exceptions inside the `text/babel` block, outputting a blank canvas which broke the experience flow.
3. **Pipeline Overhead**:
   - Introducing Playwright into the execution pipeline caused severe performance degradation. Launching Chromium, awaiting arbitrary Babel mounts, taking screenshots, and consulting a VLM drastically multiplied the time taken to produce a document.
4. **Conclusion**:
   - The React + Tailwind generation approach inside a static CDN environment proves too brittle and detrimental to the real-time interactivity that `viviDoc` aims for.
   - The project reverted to the robust, lightweight, and deterministic vanilla JS generation loop utilizing D3.js/Chart.js.

## Action Items 
- All React/Tailwind/Playwright pipeline and prompt modifications have been completely reverted.
- We will stick to Native JS/CSS and `(function() { ... })()` IIFE wrappers for interactive fragments, as they offer the most predictable execution on simple raw HTML output.
