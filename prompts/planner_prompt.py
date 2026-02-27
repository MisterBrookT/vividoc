"""Prompt template for Planner agent document spec generation."""

PLANNER_PROMPT_TEMPLATE = """You are an expert educational content planner. Your task is to create a structured document specification for an interactive educational document on the given topic.

Topic: {topic}

Generate a comprehensive document specification with knowledge units. Each knowledge unit should:
1. Have a unique ID (e.g., "ku1", "ku2", etc.)
2. Contain a brief summary (unit_content)
3. Include a detailed text_description that is self-contained and suitable for generating educational text
4. Include a structured interaction_spec that decomposes the interactive visualization into four components:

   - state: An object where keys are variable names and values describe the variable:
     - For user-controllable variables: {{"control": "<type>", "range": [...], "default": <val>}}
       Control types: "slider", "dropdown", "click", "drag", "toggle", "none" (for static/constant)
     - For computed variables: {{"derived": "<formula or description>"}}

   - render: A list of strings, each describing one visual element on screen

   - transition: A list of strings, each describing one cause-and-effect interaction rule
     (empty list [] if the visualization is static with no user interaction)

   - constraint: A single string describing the pedagogical invariant — the key insight
     the learner should discover through interaction (null if not applicable)

Guidelines:
- Break down the topic into 3-5 logical knowledge units
- Each text_description should explain what the reader should understand after reading that section
- Make interaction_spec self-contained so it can be used independently for code generation
- Focus on building intuition and understanding through interaction

Example knowledge unit:
{{
  "id": "ku1",
  "unit_content": "π represents the ratio between a circle's circumference and its diameter.",
  "text_description": "This section explains that every circle has two essential measurements—its circumference and its diameter—and introduces the idea that the ratio between these two values is always the same regardless of the circle's size.",
  "interaction_spec": {{
    "state": {{
      "r": {{"control": "slider", "range": [0.5, 5], "default": 1}},
      "C": {{"derived": "2 * π * r"}},
      "D": {{"derived": "2 * r"}},
      "ratio": {{"derived": "C / D"}}
    }},
    "render": [
      "A circle whose visual size reflects the current value of r",
      "Labels displaying the current values of C, D, and ratio"
    ],
    "transition": [
      "Dragging the slider changes r; C, D, and ratio update automatically"
    ],
    "constraint": "ratio ≈ 3.14159 regardless of how r changes"
  }}
}}

Now generate the complete document specification for the topic: {topic}
"""


def get_planner_prompt(topic: str) -> str:
    """Generate the planner prompt for a given topic."""
    return PLANNER_PROMPT_TEMPLATE.format(topic=topic)
