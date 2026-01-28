"""Prompt template for Planner agent document spec generation."""

PLANNER_PROMPT_TEMPLATE = """You are an expert educational content planner. Your task is to create a structured document specification for an interactive educational document on the given topic.

Topic: {topic}

Generate a comprehensive document specification with knowledge units. Each knowledge unit should:
1. Have a unique ID (e.g., "ku1", "ku2", etc.)
2. Contain a brief summary (unit_content)
3. Include a detailed text_description that is self-contained and suitable for generating educational text
4. Include an interaction_description that is self-contained and suitable for generating interactive Python visualization code

Guidelines:
- Break down the topic into 3-5 logical knowledge units
- Each text_description should explain what the reader should understand after reading that section
- Each interaction_description should describe what interactive elements the reader can use and what they will observe
- Make descriptions self-contained so they can be used independently for generation
- Focus on building intuition and understanding, not just facts

Example knowledge unit structure:
{{
  "id": "ku1",
  "unit_content": "π represents the ratio between a circle's circumference and its diameter.",
  "text_description": "This section explains that every circle has two essential measurements—its circumference, which is the distance around the circle, and its diameter, which is the distance across the circle through its center—and introduces the idea that the ratio between these two values is always the same regardless of the circle's size. The reader should gain an intuitive understanding of why mathematicians define π as this ratio and how this definition connects the geometry of any circle to a universal mathematical constant.",
  "interaction_description": "In this part, the reader can adjust the radius of a circle using a slider, and as the radius changes, the visualization updates the circle in real time while recalculating and displaying the circumference, the diameter, and the resulting ratio between them, allowing the reader to see directly that the ratio stays roughly the same even when the size of the circle varies."
}}

Now generate the complete document specification for the topic: {topic}
"""


def get_planner_prompt(topic: str) -> str:
    """Generate the planner prompt for a given topic."""
    return PLANNER_PROMPT_TEMPLATE.format(topic=topic)
