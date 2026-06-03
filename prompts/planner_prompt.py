"""Prompt template for Planner agent document spec generation."""

PLANNER_PROMPT_TEMPLATE = """You are an expert educational content planner. Your task is to create a structured document specification for an interactive educational document on the given topic.

Topic: {topic}

Generate a comprehensive document specification with 3–4 knowledge units. Each knowledge unit must include an **interaction_spec** using the SRTC framework (State, Render, Transition, Constraint).

---

## SRTC Interaction Spec Format

Each interaction_spec has four fields:

**state** — Variables that define the visualization's configuration:
  - User-controllable: {{"control": "<type>", "range": [...], "default": <val>, "label": "<label>"}}
    Control types: "slider", "dropdown", "segmented-button", "toggle", "drag-x", "drag-y",
                   "click-to-place", "hover", "scroll-wheel", "playback", "none"
  - Computed/derived: {{"derived": "<formula or description>"}}
  - Constant: {{"control": "constant", "value": <val>, "label": "<label>"}}

**render** — A list of strings, each describing one visible element on screen.

**transition** — A list of cause-and-effect rules: "When X happens, Y updates."
  **Set transition: [] when the section is genuinely better as a static visualization.**
  Not every section needs interaction.

**constraint** — The pedagogical invariant: the key insight the learner should discover.
  Make it precise and measurable (e.g., "ratio ≈ 3.14159 regardless of r").
  Set to null only if no single invariant applies.

---

## Interaction Design Principles

**Choose the interaction type that serves the concept — do not force interaction.**
Here are the 8 types with their appropriate use cases:

| Type | When to use | Signature control |
|------|-------------|-------------------|
| Parameter Exploration | Learner adjusts a continuous variable to observe its effect | slider |
| State Switching | Discrete configurations produce qualitatively different outcomes | segmented-button / dropdown |
| Direct Manipulation | Spatial relationships are core to the concept | drag-x / drag-y on canvas objects |
| Freeform Construction | Learner builds something (graph, circuit, network) to see emergent behavior | click-to-place / draw |
| Temporal Control | The concept has a time dimension (animation, algorithm steps, waveform) | playback + slider |
| Inspection | The concept is about spatial structure; learner explores by hovering | hover |
| Spatial Navigation | The concept is inherently 3D or requires perspective | drag-rotate / zoom |
| Scroll-driven Narrative | A linear progression best reveals the concept | scroll-wheel |

**Static is fine.** If a knowledge unit is best understood by seeing a clear diagram or animation without user input, set transition: [] and design a beautiful, informative render.

---

## Examples by Interaction Type

### Parameter Exploration
```json
{{
  "state": {{
    "sigma": {{"control": "slider", "range": [1, 30], "default": 10, "label": "σ (Prandtl Number)"}},
    "rho":   {{"control": "slider", "range": [10, 60], "default": 28, "label": "ρ (Rayleigh Number)"}},
    "trajectory": {{"derived": "numerical integration of Lorenz equations"}}
  }},
  "render": [
    "3D phase-space trajectory projected onto 2D canvas, trail fades over time",
    "Two sliders for σ and ρ"
  ],
  "transition": [
    "Adjusting σ slider resets the trajectory and restarts integration"
  ],
  "constraint": "For classical values σ=10, ρ=28, β=8/3, the trajectory never repeats — butterfly shape demonstrates sensitive dependence on initial conditions."
}}
```

### State Switching
```json
{{
  "state": {{
    "orbital_state": {{"control": "segmented-button", "options": ["1s", "2p", "3d"], "default": "1s"}},
    "density_cloud": {{"derived": "Monte Carlo sampling ∝ |ψ(x,y)|²"}}
  }},
  "render": [
    "2D canvas showing accumulating probability density cloud",
    "Segmented button control: 1s | 2p | 3d"
  ],
  "transition": [
    "Clicking a segment clears existing points and starts new Monte Carlo sampling"
  ],
  "constraint": "1s is spherically symmetric; 2p is a dumbbell; 3d is four-lobed — each matches theoretical quantum mechanics."
}}
```

### Direct Manipulation
```json
{{
  "state": {{
    "object_x": {{"control": "drag-x", "range": [20, "lens_x - 10"], "label": "Object position"}},
    "f": {{"control": "drag-x", "range": [40, 300], "label": "Focal length"}},
    "v": {{"derived": "(u * f) / (u - f) [thin lens equation]"}}
  }},
  "render": [
    "Convex lens at center", "Draggable object arrow (left)", "Three principal rays"
  ],
  "transition": [
    "Dragging object arrow changes u and updates all optical values in real-time"
  ],
  "constraint": "1/u + 1/v = 1/f is always satisfied. When u < f, v becomes negative (virtual image)."
}}
```

### Temporal Control
```json
{{
  "state": {{
    "time": {{"control": "playback", "range": [0, "∞"], "default": 0}},
    "is_playing": {{"control": "toggle", "default": true}},
    "n_harmonics": {{"control": "slider", "range": [1, 15], "step": 2, "default": 5}}
  }},
  "render": [
    "Chain of rotating epicycles", "Reconstructed waveform on the right", "Play/Pause button"
  ],
  "transition": [
    "Play/Pause toggles animation", "Harmonic slider adds/removes outer epicycles"
  ],
  "constraint": "As n_harmonics → ∞, the waveform converges to a perfect square wave (Fourier's theorem)."
}}
```

---

## Output Format

Generate a DocumentSpec JSON with:
- topic: the input topic
- knowledge_units: 3–4 units, each with id, unit_content, text_description, interaction_spec

text_description: A self-contained paragraph describing what the reader should understand after reading this section. Written as an instruction to a future content writer — describe the goal, not just the facts.

Now generate the complete document specification for the topic: {topic}
"""


def get_planner_prompt(topic: str) -> str:
    """Generate the planner prompt for a given topic."""
    return PLANNER_PROMPT_TEMPLATE.format(topic=topic)
