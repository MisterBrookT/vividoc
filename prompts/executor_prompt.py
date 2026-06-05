"""Prompt templates for Executor V2 - Fragment-based generation."""

# Stage 1: Generate text content fragment only
FRAGMENT_STAGE1_PROMPT = """You are an expert educational content writer creating an interactive document about "{topic}".

{style_instructions}

=== COMPLETED SECTIONS (for style reference only, DO NOT modify) ===
{completed_sections}

=== CURRENT TASK ===
Section ID: {scope_id}
Section Title: {unit_content}
Content Description: {text_description}

=== REQUIREMENTS ===
1. Maintain the SAME writing style, tone, and detail level as completed sections
2. Ensure content difficulty progresses naturally from previous sections
3. Use HTML formatting:
   - <p> tags for paragraphs (2–3 sentences max per paragraph)
   - <strong> for key terms inline — not as fake sub-headings
   - <em> for italics
   - KaTeX syntax for math: $\\pi$, $E=mc^2$, $\\frac{{a}}{{b}}$
4. ONLY return the HTML fragment for the text content
5. DO NOT include <div class="text-content"> tags
6. DO NOT include any other sections

=== TYPOGRAPHY CONSTRAINTS (strictly enforced) ===
- PROSE ONLY. Do not use <ul><li> or <ol><li> for core explanations. Lists are forbidden for concept text.
- Do NOT create colored callout boxes, info blocks, or <div> with background-color. No border-left highlights.
- Emphasis = <strong> inline only. Not headers, not boxes, not colored text spans.
- Conclusion first: open every paragraph with the key finding, then support it. Never build to the point.
- Second person, active voice: "you", "notice", "drag", not "one can observe that".

=== OUTPUT FORMAT ===
Return ONLY the HTML fragment (no div wrapper):

<p>First paragraph with <strong>emphasis</strong> and math $\\pi$.</p>
<p>Second paragraph explaining the concept.</p>
<p>Formula: $E = mc^2$</p>

Now generate the text content fragment for section {scope_id}:
"""


# Stage 2: Generate interactive content fragment only
FRAGMENT_STAGE2_PROMPT = """You are an expert at creating interactive educational visualizations for a document about "{topic}".

{style_instructions}

=== INTERACTION TAXONOMY — match your implementation to the spec's pattern ===

**Parameter Exploration** (slider → derived update)
  Pattern: read slider value → recompute derived state → redraw canvas or update DOM on 'input' event.
  Example spec: Lorenz Attractor — σ/ρ sliders reset and restart trajectory integration.

**State Switching** (segmented button / dropdown → discrete reconfiguration)
  Pattern: on click, set active state → clear previous render → trigger new render for the chosen config.
  Example spec: Quantum Orbitals — switching 1s/2p/3d clears point cloud and restarts Monte Carlo sampling.

**Direct Manipulation** (drag object on canvas → real-time derived update)
  Pattern: mousedown → track mousemove → update state.x/y → recompute all derived values → redraw.
  Constrain drag to valid region. Show live numeric readouts.
  Example spec: Geometric Optics — dragging object arrow updates u, v, M via thin lens equation in real-time.

**Freeform Construction** (click to place / draw → emergent behavior)
  Pattern: canvas click → add item to collection → run simulation/forward-pass → redraw.
  Provide Clear button to reset collection.
  Example spec: Neural Network — click places hidden neuron, triggers animated forward pass.

**Temporal Control** (play/pause + optional scrub)
  Pattern: requestAnimationFrame loop with is_playing flag. Advance time each frame. Slider for speed or parameter.
  Example spec: Fourier Epicycles — play/pause button + harmonic slider controlling epicycle chain.

**Inspection** (hover / cursor tracking → highlight nearest)
  Pattern: mousemove → find nearest element → update highlighted cell/tooltip. No state mutation on hover.
  Example spec: Voronoi — hover illuminates nearest cell with radial gradient and shows distance line.

**Spatial Navigation** (click-drag to rotate/pan → redraw 3D projection)
  Pattern: mousedown+mousemove → update rotX/rotY → project 3D mesh → sort faces (Painter's Algorithm) → draw.
  Example spec: Möbius Strip — drag updates pitch/yaw angles, mesh redraws with depth shading.

**Scroll-driven Narrative** (scroll → advance narrative variable)
  Pattern: wheel event → clamp scroll_progress [0,1] → update derived state → redraw.
  Example spec: Entropy — scroll raises partition wall, allowing particles to mix.

**STATIC VISUALIZATION** (transition: [] in spec)
  If the spec's "transition" list is empty, do NOT add controls. Create a beautiful static or auto-animated
  visualization using requestAnimationFrame. The goal is clarity, not interactivity.

**REVEAL ON DEMAND** — use this pattern when the concept IS the transformation:
  Show the initial state. Add a single "Reveal" or "Show result" button. On click, animate to the transformed
  state. The gap between before and after is the aha moment. Don't show both states simultaneously by default.
  Example: PCA — show raw scatter plot first, button reveals PC axes overlaid and projected coordinates.

**JUXTAPOSITION** — use this pattern when the concept IS sensitivity to a parameter:
  Render two canvases side by side under two fixed parameter values. A shared slider controls both simultaneously.
  The learner sees the difference without needing to remember "what it looked like before".
  Example: t-SNE perplexity=5 vs perplexity=50 side-by-side, single slider shifts both in sync.

---

=== INTERACTION INTEGRITY — check before implementing ===
Ask: "If I replaced this interaction with a static image, what insight would the learner LOSE?"
If the answer is "not much", simplify or make it static. The interaction must be the only way to convey the concept.
The manipulated variable must be the variable the section is teaching — not a decorative parameter.

=== THE CONSTRAINT IS THE PEDAGOGICAL CORE ===
The spec's "constraint" field is the key insight the learner should discover. Design for it:
  - Display the constraint's formula or value as a live label/badge
  - Use a color change or direct annotation to make it unmissable
  - For static visualizations, the render should directly demonstrate the constraint

=== VISUAL STYLE CONSTRAINTS ===
- Page frame decoration = zero. No colored border-top/border-left on section containers. No ornamental dividers.
- The accent color appears ONLY on: interactive controls (sliders, buttons), live numeric readouts, annotations
  drawn directly on the canvas. Not on section backgrounds, card borders, or text containers.
- Controls should be minimal: plain range inputs, text labels, simple buttons. No drop shadows on UI chrome.

---

=== COMPLETED SECTIONS (for style reference only, DO NOT modify) ===
{completed_sections}

=== CURRENT SECTION'S TEXT CONTENT ===
{current_text_content}

=== CURRENT TASK ===
Section ID: {scope_id}

Interaction Specification (SRTC):
{interaction_spec_text}

=== IMPLEMENTATION REQUIREMENTS ===
1. Implement the spec faithfully: all state variables, all render elements, all transitions
2. Identify the interaction type and follow the pattern described above
3. Highlight the constraint prominently in the visualization
4. Maintain consistent visual design with previous sections
5. Structure:
   a) <style> tag: CSS (all selectors prefixed with #{scope_id})
   b) HTML: controls and visualization containers
   c) <script> tag: JavaScript (IIFE)
6. All DOM IDs must use {scope_id}- prefix (e.g., {scope_id}-slider, {scope_id}-canvas)
7. Available libraries: D3.js, Chart.js (already loaded in document)
8. Canvas containers with Chart.js + maintainAspectRatio:false MUST have explicit CSS height
9. ONLY return the HTML fragment — no <div class="interactive-content"> wrapper

=== OUTPUT FORMAT ===
Return ONLY the HTML fragment:

<style>
    #{scope_id} .controls {{ margin: 20px 0; }}
    #{scope_id} .viz {{ min-height: 300px; }}
</style>

<div class="controls">
    <label for="{scope_id}-slider">Value:</label>
    <input id="{scope_id}-slider" type="range" min="1" max="10" value="5">
    <span id="{scope_id}-value">5</span>
</div>
<div class="viz" id="{scope_id}-viz"></div>

<script>
    (function() {{
        const slider = document.getElementById('{scope_id}-slider');
        const valueSpan = document.getElementById('{scope_id}-value');

        function update() {{
            valueSpan.textContent = slider.value;
        }}

        slider.addEventListener('input', update);
        update();
    }})();
</script>

Now generate the interactive content fragment for section {scope_id}:
"""


def get_fragment_stage1_prompt(
    topic: str,
    completed_sections: str,
    scope_id: str,
    unit_content: str,
    text_description: str,
    style_instructions: str = "",
) -> str:
    """Generate Stage 1 prompt for text content fragment."""
    return FRAGMENT_STAGE1_PROMPT.format(
        topic=topic,
        completed_sections=completed_sections,
        scope_id=scope_id,
        unit_content=unit_content,
        text_description=text_description,
        style_instructions=style_instructions,
    )


def get_fragment_stage2_prompt(
    topic: str,
    completed_sections: str,
    scope_id: str,
    current_text_content: str,
    interaction_spec_text: str,
    style_instructions: str = "",
) -> str:
    """Generate Stage 2 prompt for interactive content fragment."""
    return FRAGMENT_STAGE2_PROMPT.format(
        topic=topic,
        completed_sections=completed_sections,
        scope_id=scope_id,
        current_text_content=current_text_content,
        interaction_spec_text=interaction_spec_text,
        style_instructions=style_instructions,
    )
