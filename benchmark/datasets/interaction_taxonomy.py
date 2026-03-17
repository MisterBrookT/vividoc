"""Classify all interaction forms from topics.jsonl into an intent-based taxonomy.

Categories are based on interaction intent/behavior, NOT UI widget type.
Inspired by Munzner's What-Why-How framework (Ch.11 Manipulate View),
but categories are empirically derived from the dataset.

Usage:
    cd codebase
    uv run python benchmark/datasets/interaction_taxonomy.py
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

TOPICS_FILE = Path(__file__).parent / "prepped" / "topics.jsonl"


TAXONOMY = {
    "Parameter Exploration": (
        "Adjusting a continuous or near-continuous parameter to observe how "
        "the visualization responds (e.g., changing radius, frequency, "
        "learning rate, threshold via slider or dial)."
    ),
    "State Switching": (
        "Switching between discrete configurations, datasets, algorithms, "
        "or modes that qualitatively change what is displayed "
        "(e.g., selecting a dataset, toggling a view, choosing a preset)."
    ),
    "Direct Manipulation": (
        "Dragging or repositioning objects within the visualization to "
        "alter the underlying data or model in real time "
        "(e.g., moving data points, control points, graph nodes)."
    ),
    "Temporal Control": (
        "Controlling the time dimension of a simulation or animation: "
        "play, pause, step through, scrub a timeline, adjust speed "
        "(e.g., stepping through a sorting algorithm, replaying a simulation)."
    ),
    "Freeform Construction": (
        "Creating or editing content freely: drawing on a canvas, writing "
        "code, editing numerical values, uploading media "
        "(e.g., drawing a custom signal, editing matrix cells, writing shader code)."
    ),
    "Inspection": (
        "Exploring details without modifying state: hovering for tooltips, "
        "cursor tracking, highlighting related elements "
        "(e.g., hovering over a data point to see its label)."
    ),
    "Spatial Navigation": (
        "Navigating a spatial view: zooming, panning, rotating a 3D scene "
        "(e.g., rotating a 3D surface, zooming into a fractal)."
    ),
    "Scroll-driven Narrative": (
        "Scrolling the page triggers synchronized animations or progresses "
        "through a step-by-step visual narrative."
    ),
}


def classify(label: str, desc: str) -> str:
    """Classify a single interaction form by interaction intent."""
    t = (label + " " + desc).lower()

    # --- Scroll-driven Narrative (very specific, check first) ---
    if "scroll" in t and any(
        k in t for k in ["progress", "narrative", "animation", "step", "slide"]
    ):
        return "Scroll-driven Narrative"

    # --- Inspection (hover/tooltip, no state change) ---
    if any(
        k in t
        for k in [
            "hover",
            "mouse over",
            "mousing over",
            "tooltip",
            "moving the cursor over",
            "moving the mouse cursor over",
            "cursor position tracking",
            "highlights the corresponding",
            "sweeping the cursor",
        ]
    ):
        return "Inspection"

    # --- Temporal Control (play, pause, step, speed, replay, scrub) ---
    # Check BEFORE Spatial Navigation to catch "speed" sliders etc.
    if any(
        k in t
        for k in [
            "play button",
            "play/pause",
            "play audio",
            "play algorithm",
            "pause button",
            "pause/resume",
            "pause/unpause",
            "pause or resume",
            "start/stop",
            "step-through",
            "step through",
            "single-step",
            "replay",
            "restart",
            "run simulation",
            "run packing algorithm",
            "start simulation",
            "animate simulation",
            "animation control",
            "speed control",
            "playback",
            "simulation speed",
            "initiates.*animation",
            "initiates.*simulation",
            "continuously animates",
        ]
    ):
        return "Temporal Control"

    # --- Freeform Construction (drawing, code/text editing, file upload) ---
    # Check BEFORE Spatial Navigation and Direct Manipulation
    if any(
        k in t
        for k in [
            # Drawing / canvas
            "drawing canvas",
            "draw a",
            "draw on a canvas",
            "draw custom",
            "draw base shape",
            "draw transformation",
            "freeform",
            "drawing a continuous line",
            "drawing a shape",
            "drawing a stroke",
            "drawing a character",
            "drawing a single",
            "handwriting input",
            # Code / text editing
            "code input",
            "code editor",
            "code cell",
            "code snippet",
            "sql cell",
            "writing code",
            "writing.*expression",
            "writing.*queries",
            "manipulate code",
            "modify code",
            "modifying the code",
            "shader code",
            "editing the javascript",
            "editing the code",
            "editing the text",
            "editing the numerical",
            "editing the values",
            "editing its numerical",
            "editing a cell",
            "edit transition matrix",
            "edit model via text",
            "modify payoff",
            "changing the values in the payoff",
            "modify transformation",
            "modify base shape",
            # Direct value editing
            "typing numbers",
            "typing",
            "input field",
            "text field",
            "text input",
            "inputting a number",
            "enter age",
            "enter a ",
            "enter keyword",
            "entering keyword",
            # Sequencing / composing
            "adding or removing notes",
            "sequencing events",
            "copying patterns",
            "agent and rule definition",
            "nest behavior",
            "programmatic property",
            # File / media upload
            "upload",
            "webcam",
            "video feed",
            "live video",
            # AI generation
            "ai-powered generation",
            "ai generation",
        ]
    ):
        return "Freeform Construction"

    # --- Spatial Navigation (zoom, pan, rotate 3D, orbit) ---
    # Only match genuine navigation, not things that happen to contain "rotat"
    if any(
        k in t
        for k in [
            "zoom",
            "pan and zoom",
            "pan map",
            "pan wraparound",
            "panning",
            "pan ",
            "pan,",
            "orbit",
            "3d view",
            "viewing angle",
            "viewing perspective",
            "model rotation",
            "magnif",
        ]
    ):
        return "Spatial Navigation"
    # Rotate/drag 3D — but only if it's about changing viewpoint, not data
    if ("rotat" in t or "camera" in t) and any(
        k in t for k in ["3d", "view", "globe", "earth", "model", "scene"]
    ):
        return "Spatial Navigation"

    # --- Direct Manipulation (dragging objects in the visualization) ---
    if any(
        k in t
        for k in [
            "dragging the flag",
            "dragging the point",
            "dragging the start",
            "dragging the end",
            "dragging the control",
            "dragging the basis",
            "dragging the head",
            "dragging a point",
            "dragging any data point",
            "dragging a data point",
            "dragging points",
            "dragging the nodes",
            "dragging the handles",
            "dragging the figurine",
            "dragging the landscape",
            "dragging the colored",
            "dragging the entire",
            "dragging either",
            "dragging the watch",
            "clicking and dragging a point on the curve",
            "clicking on points or existing geometric",
            "clicking and dragging",
            "reposition",
            "move point",
            "move data",
            "move entities",
            "move element",
            "move circle",
            "manipulating the points",
            "manipulating the transformed",
        ]
    ):
        # If it's actually a slider being dragged, it's Parameter Exploration
        if "slider" in t:
            return "Parameter Exploration"
        return "Direct Manipulation"

    # --- Parameter Exploration (continuous parameter adjustment) ---
    if any(
        k in t
        for k in [
            "slider",
            "scrub",
            "dial",
            "draggable number",
            "dragging the number",
            "range slider",
            "adjust.*parameter",
            "adjust.*coefficient",
            "increasing or decreasing",
            "number of neurons",
            "modify network width",
        ]
    ):
        return "Parameter Exploration"

    # --- State Switching (discrete selection that changes configuration) ---
    # Dropdown / menu / preset / dataset / algorithm selection
    if any(
        k in t
        for k in [
            "dropdown",
            "menu",
            "choose from",
            "select.*from",
            "select.*type",
            "select dataset",
            "select distribution",
            "select algorithm",
            "select surface",
            "select signal",
            "select task",
            "select tool",
            "select block",
            "select sex",
            "load example",
            "load.*preset",
            "sample selection",
            "selecting a",
            "preset",
            "choosing a",
        ]
    ):
        return "State Switching"

    # Buttons, toggles, checkboxes that switch state
    if any(
        k in t
        for k in [
            "button",
            "toggle",
            "radio",
            "switch",
            "checkbox",
            "reset",
            "clear",
            "undo",
            "redo",
            "clicking",
            "click ",
        ]
    ):
        return "State Switching"

    # Keyboard shortcuts for discrete actions
    if any(k in t for k in ["keyboard", "pressing the"]):
        return "State Switching"

    # --- Broader fallbacks ---
    if "select" in t or "advance to" in t or "navigate" in t:
        return "State Switching"
    if any(
        k in t
        for k in [
            "adjust",
            "modify",
            "change ",
            "changed",
            "resiz",
            "sliding a replica",
            "correlation",
            "global.*parameter",
            "configuration",
            "customization",
            "advanced option",
        ]
    ):
        return "Parameter Exploration"
    if "edit" in t or "write" in t or "creat" in t or "defin" in t or "register" in t:
        return "Freeform Construction"
    if "drag" in t or "moving a mouse" in t or "live.*stream" in t:
        return "Direct Manipulation"
    if "inspect" in t or "enlarged" in t or "tapping" in t:
        return "Inspection"
    if any(
        k in t
        for k in [
            "simultaneously updates",
            "linked",
            "reactive",
            "dynamic",
            "automatically",
            "re-execution",
            "redraw",
        ]
    ):
        return "State Switching"

    return "Other"


def main():
    lines = TOPICS_FILE.read_text().strip().split("\n")

    all_forms = []
    for line in lines:
        d = json.loads(line)
        for form in d.get("interaction_forms", []):
            all_forms.append(
                {
                    "label": form["label"],
                    "description": form["description"],
                    "topic": d["topic"],
                    "url": d.get("url", ""),
                    "category": classify(form["label"], form["description"]),
                }
            )

    # Stats
    cat_counts = Counter()
    cat_examples = defaultdict(list)
    for form in all_forms:
        cat = form["category"]
        cat_counts[cat] += 1
        if len(cat_examples[cat]) < 3:
            cat_examples[cat].append(f"{form['label']} ({form['topic'][:50]})")

    total = len(all_forms)
    print(f"Total: {total} interaction instances from {len(lines)} documents\n")
    print(f"{'Category':<30} {'#':>4} {'%':>6}")
    print("-" * 45)
    for cat, count in cat_counts.most_common():
        pct = count / total * 100
        print(f"{cat:<30} {count:>4} {pct:>5.1f}%")
        for ex in cat_examples[cat]:
            print(f"    e.g. {ex}")

    # Save taxonomy summary
    out_path = Path(__file__).parent / "interaction_taxonomy.json"
    summary = {
        "total_interactions": total,
        "total_documents": len(lines),
        "taxonomy": {
            cat: {
                "description": TAXONOMY.get(cat, ""),
                "count": count,
                "percentage": round(count / total * 100, 1),
                "examples": cat_examples[cat],
            }
            for cat, count in cat_counts.most_common()
        },
    }
    out_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nSaved to {out_path}")

    # Save per-form classification
    detail_path = Path(__file__).parent / "interaction_classified.json"
    detail_path.write_text(
        json.dumps(all_forms, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Detailed classification saved to {detail_path}")


if __name__ == "__main__":
    main()
