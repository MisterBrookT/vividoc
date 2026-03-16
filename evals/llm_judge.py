"""LLM-as-Judge evaluation for three dimensions.

- Content Richness: evaluated from HTML source code
- Interaction Design: evaluated from HTML source code
- Visual Quality: evaluated from screenshot + HTML source code
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import BaseModel
from vividoc.utils.llm.client import LLMClient
from evals.prompts import (
    CONTENT_RICHNESS_PROMPT,
    INTERACTION_DESIGN_PROMPT,
    VISUAL_QUALITY_PROMPT,
)


class DimensionScore(BaseModel):
    score: int
    reason: str


def _parse_score(response: str | dict) -> DimensionScore:
    """Parse JSON score from LLM response, with fallback."""
    # call_text_generation may return dict if response was in a code block
    if isinstance(response, dict):
        try:
            return DimensionScore(**response)
        except Exception:
            pass

    text = str(response).strip()
    # Try to extract JSON from markdown code block
    if "```" in text:
        for block in text.split("```"):
            block = block.strip().removeprefix("json").strip()
            if block.startswith("{"):
                text = block
                break
    try:
        data = json.loads(text)
        return DimensionScore(**data)
    except (json.JSONDecodeError, KeyError, TypeError):
        # Fallback: try to find score in text
        for i in range(5, 0, -1):
            if str(i) in text:
                return DimensionScore(score=i, reason=text[:200])
        return DimensionScore(score=0, reason=f"Parse error: {text[:200]}")


def evaluate_content_richness(
    client: LLMClient, topic: str, html: str
) -> DimensionScore:
    prompt = CONTENT_RICHNESS_PROMPT.format(topic=topic, html=html)
    response = client.call_text_generation(prompt)
    return _parse_score(response)


def evaluate_interaction_design(
    client: LLMClient, topic: str, html: str
) -> DimensionScore:
    prompt = INTERACTION_DESIGN_PROMPT.format(topic=topic, html=html)
    response = client.call_text_generation(prompt)
    return _parse_score(response)


def evaluate_visual_quality(
    client: LLMClient, topic: str, html: str, screenshot_path: str
) -> DimensionScore:
    """Evaluate visual quality using multimodal LLM (screenshot + code)."""
    prompt = VISUAL_QUALITY_PROMPT.format(topic=topic, html=html)
    response = client.call_image_understanding(prompt, screenshot_path)
    return _parse_score(response)


def evaluate_document(
    client: LLMClient,
    topic: str,
    html_path: str,
    screenshot_path: str | None = None,
) -> dict:
    """Run all LLM-as-Judge evaluations on a single document.

    Returns dict with scores for each dimension.
    """
    html = Path(html_path).read_text(encoding="utf-8")

    results = {}

    # Content Richness (code only)
    cr = evaluate_content_richness(client, topic, html)
    results["content_richness"] = {"score": cr.score, "reason": cr.reason}

    # Interaction Design (code only)
    iq = evaluate_interaction_design(client, topic, html)
    results["interaction_design"] = {"score": iq.score, "reason": iq.reason}

    # Visual Quality (screenshot + code)
    if screenshot_path and Path(screenshot_path).exists():
        vq = evaluate_visual_quality(client, topic, html, screenshot_path)
    else:
        # Fallback: evaluate from code only
        prompt = VISUAL_QUALITY_PROMPT.format(topic=topic, html=html)
        response = client.call_text_generation(prompt)
        vq = _parse_score(response)
    results["visual_quality"] = {"score": vq.score, "reason": vq.reason}

    return results
