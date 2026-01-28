"""Prompt templates for Evaluator agent."""

COHERENCE_CHECK_PROMPT = """You are an expert educational content evaluator. Evaluate the overall coherence and quality of the following educational document.

Topic: {topic}

Content:
{content}

Evaluate:
1. Text fluency and readability
2. Logical flow between sections
3. Clarity of explanations
4. Overall coherence

Provide a brief assessment (2-3 sentences) of the document's quality and coherence.
"""


def get_coherence_check_prompt(topic: str, content: str) -> str:
    """Generate prompt for coherence checking."""
    return COHERENCE_CHECK_PROMPT.format(topic=topic, content=content)
