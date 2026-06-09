"""LLM-as-Judge evaluation for three dimensions.

- Content Richness: evaluated from text content (script/style stripped)
- Interaction Design: evaluated from HTML source code
- Visual Quality: evaluated from screenshot + HTML source code
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pydantic import BaseModel

from benchmark.evals.prompts import (
    CONTENT_RICHNESS_PROMPT,
    INTERACTION_DESIGN_PROMPT,
    VISUAL_QUALITY_PROMPT,
)
from vividoc.utils.llm.client import LLMClient


def extract_text_content(html: str) -> str:
    """Extract semantic HTML structure, stripping <script> and <style> tags.

    Keeps structural tags (h1-h6, p, ul, ol, li, table, etc.) but removes
    all JavaScript, CSS, and non-content head elements so the LLM focuses
    on textual content only.
    """
    # Remove <script>...</script>
    text = re.sub(
        r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE
    )
    # Remove <style>...</style>
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Remove <head>...</head> (meta, link, title are not educational content)
    text = re.sub(r"<head[^>]*>.*?</head>", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Remove inline event handlers (onclick, onchange, etc.)
    text = re.sub(r'\s+on\w+="[^"]*"', "", text)
    text = re.sub(r"\s+on\w+='[^']*'", "", text)
    # Remove <canvas> tags (no text content)
    text = re.sub(
        r"<canvas[^>]*>.*?</canvas>", "", text, flags=re.DOTALL | re.IGNORECASE
    )
    # Remove <svg> tags
    text = re.sub(r"<svg[^>]*>.*?</svg>", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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
    client: LLMClient, topic: str, text_content: str
) -> DimensionScore:
    prompt = CONTENT_RICHNESS_PROMPT.format(topic=topic, text_content=text_content)
    response = client.call_text_generation(prompt)
    return _parse_score(response)


def evaluate_interaction_design(
    client: LLMClient,
    topic: str,
    html: str,
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
    functional_result: dict | None = None,
) -> dict:
    """Run all LLM-as-Judge evaluations on a single document.

    Args:
        functional_result: Output from evaluate_functional(), used to inform
            the Interaction Design judge about which interactions actually work.

    Returns dict with scores for each dimension.
    """
    html = Path(html_path).read_text(encoding="utf-8")
    text_content = extract_text_content(html)

    results = {}

    # Content Richness (text content only — no script/style)
    cr = evaluate_content_richness(client, topic, text_content)
    results["content_richness"] = {"score": cr.score, "reason": cr.reason}

    # Interaction Design (code only — functional results used separately as multiplier)
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


def _format_functional_summary(func_result: dict | None) -> str:
    """Format functional eval results into a human-readable summary for the LLM."""
    if not func_result:
        return "No automated test results available."

    total = func_result.get("interactive_elements_found", 0)
    responsive = func_result.get("responsive_elements", 0)
    if_score = func_result.get("interaction_functionality", 0)
    details = func_result.get("interaction_details", [])

    lines = [
        f"Found {total} interactive elements, {responsive}/{total} responded to input (IF={if_score:.2f})."
    ]

    if details:
        lines.append("Per-element results:")
        for d in details:
            tag = d.get("tag", "?")
            el_type = d.get("type", "")
            status = "OK" if d.get("responsive") else "FAIL"
            label = f"[{tag}" + (f" type={el_type}" if el_type else "") + f"] {status}"
            lines.append(f"  {label}")

    return "\n".join(lines)
