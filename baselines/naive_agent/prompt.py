"""Prompt template for Naive Agent baseline."""

NAIVE_AGENT_PROMPT = """\
You are an expert educational content creator. Generate an interactive HTML document about the following topic.

Topic: {topic}

Requirements:
1. The document must be a single, complete HTML file (<!DOCTYPE html> ... </html>).
2. Aim for 3-5 sections.

Return ONLY the complete HTML document, nothing else.
"""


def get_naive_agent_prompt(topic: str) -> str:
    """Format the naive agent prompt with the given topic."""
    return NAIVE_AGENT_PROMPT.format(topic=topic)
