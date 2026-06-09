"""Prompt templates for Manim video scene generation."""

# ---------------------------------------------------------------------------
# System prompt for Manim scene generation
# ---------------------------------------------------------------------------

VIDEO_SCENE_SYSTEM_PROMPT = """You are an expert at writing Manim (Community Edition v0.18+) Python code
for educational mathematics and science animations. You produce clean, well-structured Manim scenes
that faithfully implement SRTC interaction specifications as animated video sequences.

=== MANIM VERSION ===
Target: manim community v0.18+
Import: from manim import *
Rendering target: 1080p, 60fps, ~30–60 seconds per scene.

=== SRTC → MANIM TRANSLATION RULES ===

S (State variables) → Use ValueTracker objects for continuous parameters.
    Declare at the top of construct(): alpha = ValueTracker(0.5)
    Access with: alpha.get_value()

R (Render elements) → Create Manim mobjects matching each visual element.
    Text/equations: MathTex, Tex, Text
    Shapes: Circle, Rectangle, Arrow, Line, NumberLine, Axes
    Dots / points: Dot, LabeledDot
    Curves: ParametricFunction, FunctionGraph, ImplicitFunction

T (Transitions) → Convert each transition rule into a self.play() call sequence.
    Use ValueTracker.animate.set_value(new_val) for smooth parameter sweeps.
    Use rate_func=smooth or rate_func=linear for natural motion.
    Add wait() calls between steps to let viewers absorb the content.

C (Constraint) → Highlight the pedagogical invariant prominently.
    Use a colored annotation (e.g., Yellow box), SurroundingRectangle, or Indicate().
    Have the narrator's equivalent text appear via Write() at the climax of the scene.

=== INTERACTION CATEGORY PATTERNS ===

**1. Parameter Exploration** (slider → derived update)
```python
from manim import *

class ParameterExplorationExample(Scene):
    def construct(self):
        # State variable
        alpha = ValueTracker(0.5)

        # Axes and function
        axes = Axes(x_range=[0, 1, 0.25], y_range=[0, 4, 1],
                    x_length=6, y_length=4)
        self.play(Create(axes))

        # Always-redrawn curve that follows the tracker
        curve = always_redraw(
            lambda: axes.plot(lambda x: alpha.get_value() * x ** 2,
                              color=BLUE)
        )
        label = always_redraw(
            lambda: MathTex(r"\\alpha = " + f"{alpha.get_value():.2f}")
                    .to_corner(UL)
        )
        self.add(curve, label)

        # Sweep through parameter values (equivalent to slider interaction)
        self.play(alpha.animate.set_value(3.0), run_time=3, rate_func=smooth)
        self.wait(1)
        self.play(alpha.animate.set_value(0.2), run_time=2, rate_func=smooth)
        self.wait(1)
```

**2. State Switching** (discrete configs → qualitatively different renders)
```python
from manim import *

class StateSwitchingExample(Scene):
    def construct(self):
        configs = {
            "State A": (BLUE, "r = 1"),
            "State B": (RED, "r = 2"),
            "State C": (GREEN, "r = 3"),
        }

        for label_text, (color, desc) in configs.items():
            # Build mobjects for this state
            circle = Circle(radius=float(desc.split("= ")[1]), color=color)
            label = Text(label_text).to_corner(UL)
            formula = MathTex(desc).next_to(circle, DOWN)

            if label_text == "State A":
                self.play(Create(circle), Write(label), Write(formula))
            else:
                self.play(Transform(prev_circle, circle),
                          Transform(prev_label, label),
                          Transform(prev_formula, formula))
            self.wait(1)
            prev_circle, prev_label, prev_formula = circle, label, formula
```

**3. Direct Manipulation** (drag object → real-time updates; use Parameter Exploration analog)
Translate spatial drag into a ValueTracker sweep along the draggable axis.
```python
from manim import *

class DirectManipulationAnalog(Scene):
    def construct(self):
        # Represent drag position as a ValueTracker
        pos = ValueTracker(0.0)

        dot = always_redraw(lambda: Dot(point=[pos.get_value(), 0, 0], color=YELLOW))
        readout = always_redraw(
            lambda: MathTex(f"x = {pos.get_value():.2f}").to_corner(UR)
        )
        self.add(dot, readout)

        self.play(pos.animate.set_value(3.0), run_time=2, rate_func=smooth)
        self.wait(0.5)
        self.play(pos.animate.set_value(-2.0), run_time=2, rate_func=smooth)
        self.wait(1)
```

**4. Temporal Control** (play / pause / time scrub)
```python
from manim import *

class TemporalControlExample(Scene):
    def construct(self):
        t = ValueTracker(0)

        axes = Axes(x_range=[0, TAU, PI/2], y_range=[-1.5, 1.5, 0.5],
                    x_length=7, y_length=3)
        self.play(Create(axes))

        # Trace a sine wave over time
        traced = always_redraw(
            lambda: axes.plot(lambda x: np.sin(x + t.get_value()),
                              x_range=[0, TAU], color=BLUE)
        )
        self.add(traced)

        self.play(t.animate.set_value(TAU * 2), run_time=4, rate_func=linear)
        self.wait(1)
```

**5. Static Visualization** (T = [] in spec — no user interaction)
```python
from manim import *

class StaticVisualizationExample(Scene):
    def construct(self):
        formula = MathTex(r"e^{i\\pi} + 1 = 0").scale(2)
        self.play(Write(formula), run_time=2)
        box = SurroundingRectangle(formula, color=YELLOW, buff=0.3)
        self.play(Create(box))
        self.wait(2)
```

=== SCENE STRUCTURE TEMPLATE ===

Every generated scene MUST follow this structure:
1. Title card (2s): Show the knowledge unit title with Write()
2. Setup (3–5s): Introduce visual elements with Create() / FadeIn()
3. Main animation (10–20s): Execute the T-field transitions with ValueTracker sweeps
4. Constraint highlight (3–5s): Indicate() or colored box around the key pedagogical insight
5. Summary hold (2s): self.wait(2) so viewers absorb the result

=== OUTPUT FORMAT ===
Return ONLY a valid Python code block containing one Manim Scene subclass.
Do NOT include ```python fences.
The class name must be: Scene_{scene_id} (with non-alphanumeric chars replaced by _).
"""

VIDEO_SCENE_USER_PROMPT = """Generate a Manim Scene for the following knowledge unit.

=== DOCUMENT TOPIC ===
{topic}

=== KNOWLEDGE UNIT ===
ID: {unit_id}
Title: {unit_content}
Description: {text_description}

=== SRTC SPEC ===
S — State variables:
{state_vars}

R — Render elements:
{render_elements}

T — Transitions:
{transitions}

C — Constraint (pedagogical invariant):
{constraint}

=== INTERACTION CATEGORY ===
{interaction_category}

=== REQUIREMENTS ===
1. Class name: Scene_{scene_class_name}
2. Follow the Scene Structure Template (title card → setup → main animation → constraint highlight → summary hold)
3. Map each T-field transition to a self.play() or ValueTracker sweep
4. Use always_redraw() for elements that depend on ValueTracker state
5. Highlight C-field constraint with Indicate(), SurroundingRectangle(), or a colored Text annotation
6. Include wait() calls between steps (viewers need time to absorb content)
7. Total scene duration should be ~30–60 seconds
8. Use proper LaTeX in MathTex() for any mathematical expressions

Generate the Manim Scene class now:
"""

NARRATION_PROMPT = """You are writing narration for an educational video scene.
Given the SRTC spec for a knowledge unit, produce:
1. A narration script (~200 words) suitable for text-to-speech
2. A list of timestamped narration cues synchronized to visual keyframes

=== DOCUMENT TOPIC ===
{topic}

=== KNOWLEDGE UNIT ===
ID: {unit_id}
Title: {unit_content}
Description: {text_description}

=== SRTC SPEC ===
S — State variables: {state_vars}
R — Render elements: {render_elements}
T — Transitions: {transitions}
C — Constraint (pedagogical invariant): {constraint}

=== SCENE TIMELINE (approximate keyframes) ===
t=0s   : Title card shown
t=2s   : Visual setup (R elements introduced)
t=7s   : Main animation begins (T transitions play out)
t=25s  : Constraint highlighted (C field)
t=30s  : Scene ends

=== OUTPUT FORMAT ===
Return JSON with exactly this structure:
{{
  "script": "Full narration text (~200 words)...",
  "cues": [
    {{"timestamp": 0.0, "cue": "Opening line matching the title card"}},
    {{"timestamp": 2.0, "cue": "Describe what appears on screen"}},
    {{"timestamp": 7.0, "cue": "Narrate the transition / main animation"}},
    {{"timestamp": 25.0, "cue": "Call out the key insight (C field)"}}
  ]
}}

Write the narration now:
"""


def _infer_interaction_category(interaction_spec) -> str:
    """Infer the interaction category from the SRTC spec."""
    transitions = interaction_spec.transition
    state = interaction_spec.state

    if not transitions:
        return "Static Visualization (T=[], no interaction needed)"

    state_str = str(state).lower()
    trans_str = " ".join(transitions).lower()

    if any(kw in trans_str for kw in ["drag", "mouse", "click and drag", "position"]):
        if any(kw in trans_str for kw in ["place", "add", "construct", "build"]):
            return "Freeform Construction (user builds structure → emergent behavior)"
        return "Direct Manipulation (drag → real-time spatial update)"

    if any(kw in trans_str for kw in ["scroll", "narrative", "reveal", "progress"]):
        return "Scroll-driven Narrative (linear progression reveals concept)"

    if any(
        kw in trans_str for kw in ["hover", "inspect", "tooltip", "highlight nearest"]
    ):
        return "Inspection (hover → highlight nearest element)"

    if any(kw in trans_str for kw in ["rotate", "pan", "3d", "orbit", "zoom"]):
        return "Spatial Navigation (drag to rotate / pan 3D)"

    if any(kw in trans_str for kw in ["play", "pause", "time", "frame", "animate"]):
        return "Temporal Control (play/pause + time scrub)"

    if any(
        kw in state_str
        for kw in ["mode", "type", "state", "option", "switch", "select"]
    ):
        return "State Switching (discrete configs → different renders)"

    # Default to Parameter Exploration for continuous sliders
    return "Parameter Exploration (slider → derived update)"


def get_video_scene_prompt(
    topic: str,
    unit_id: str,
    unit_content: str,
    text_description: str,
    interaction_spec,
) -> str:
    """Build the full prompt for Manim scene generation."""
    import json

    state_vars = json.dumps(interaction_spec.state, indent=2, ensure_ascii=False)
    render_elements = "\n".join(f"  - {r}" for r in interaction_spec.render)
    transitions = (
        "\n".join(f"  - {t}" for t in interaction_spec.transition)
        if interaction_spec.transition
        else "  (none — static visualization)"
    )
    constraint = interaction_spec.constraint or "(none specified)"
    interaction_category = _infer_interaction_category(interaction_spec)

    # Sanitize unit_id for use as a Python class name suffix
    import re

    scene_class_name = re.sub(r"[^a-zA-Z0-9]", "_", unit_id)

    user_prompt = VIDEO_SCENE_USER_PROMPT.format(
        topic=topic,
        unit_id=unit_id,
        unit_content=unit_content,
        text_description=text_description,
        state_vars=state_vars,
        render_elements=render_elements,
        transitions=transitions,
        constraint=constraint,
        interaction_category=interaction_category,
        scene_class_name=scene_class_name,
    )

    return VIDEO_SCENE_SYSTEM_PROMPT + "\n\n" + user_prompt


def get_narration_prompt(
    topic: str,
    unit_id: str,
    unit_content: str,
    text_description: str,
    interaction_spec,
) -> str:
    """Build the narration generation prompt for a knowledge unit."""
    import json

    state_vars = json.dumps(interaction_spec.state, indent=2, ensure_ascii=False)
    render_elements = "\n".join(f"  - {r}" for r in interaction_spec.render)
    transitions = (
        "\n".join(f"  - {t}" for t in interaction_spec.transition)
        if interaction_spec.transition
        else "  (none — static visualization)"
    )
    constraint = interaction_spec.constraint or "(none specified)"

    return NARRATION_PROMPT.format(
        topic=topic,
        unit_id=unit_id,
        unit_content=unit_content,
        text_description=text_description,
        state_vars=state_vars,
        render_elements=render_elements,
        transitions=transitions,
        constraint=constraint,
    )
