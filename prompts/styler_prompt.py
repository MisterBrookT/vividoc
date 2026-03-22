"""Prompt template for LLM-based Styler — generates dynamic style options from spec content."""

STYLER_PROMPT = """You are an expert in educational content design. Given a document specification, generate style options for the user to customize.

=== DOCUMENT SPEC ===
Topic: {topic}
Knowledge Units:
{ku_summaries}

=== TASK ===
Generate style dimensions in two categories:
1. **text_dimensions**: Writing/text style options (e.g., tone, text density, narrative style, terminology level)
2. **interaction_dimensions**: Interaction/animation style options (e.g., animation intensity, visual complexity, color theme)

Rules:
- Each category should have at most 3 dimensions (choose the most relevant ones for this topic)
- Each dimension should have 2-3 options
- Each option needs: id (snake_case), label (short), description (1-2 sentences explaining the style effect)
- Dimension needs: id (snake_case), label (short human-readable name)
- Make options specific and relevant to the topic content
- Descriptions should be concrete enough to serve as style instructions for content generation

Return the result as structured JSON.
"""


def get_styler_prompt(topic: str, ku_summaries: str) -> str:
    """Generate the styler prompt."""
    return STYLER_PROMPT.format(topic=topic, ku_summaries=ku_summaries)
