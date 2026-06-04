"""Narration generation for ViviDoc video pipeline.

Given a :class:`~vividoc.core.models.KnowledgeUnitSpec`, this module generates:
- A plain-text narration script (~200 words)
- A list of ``{timestamp, cue}`` dicts synchronized to visual keyframes

The narration is grounded in the SRTC spec:
  C (constraint)    → delivered as the "punchline" at the climax of the scene
  T (transitions)   → drive natural-language cues when each transition happens
  text_description  → provides the intro narration

Usage
-----
    from vividoc.core.narration_gen import NarrationGen
    from vividoc.utils.llm.client import LLMClient

    gen = NarrationGen(llm_client=LLMClient("openrouter/google/gemini-2.5-pro"))
    result = gen.generate(topic="Time Dilation", ku=ku_spec)
    print(result.script)
    for cue in result.narration_cues:
        print(f"t={cue['timestamp']:.1f}s  {cue['cue']}")
"""

from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass, field
from typing import Any, Optional

from vividoc.core.models import KnowledgeUnitSpec
from vividoc.utils.llm.client import LLMClient
from vividoc.utils.logger import logger
from prompts.video_prompt import get_narration_prompt


@dataclass
class NarrationResult:
    """Narration output for a single knowledge unit."""

    unit_id: str
    script: str
    narration_cues: list[dict[str, Any]] = field(default_factory=list)


class NarrationGen:
    """Generates narration scripts and timestamped cues for video scenes.

    Parameters
    ----------
    llm_client:
        Configured :class:`~vividoc.utils.llm.client.LLMClient` instance.
        Pass ``None`` to use the built-in template-based fallback (no LLM call).
    """

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        self.llm_client = llm_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, topic: str, ku: KnowledgeUnitSpec) -> NarrationResult:
        """Generate narration script and timestamped cues for *ku*.

        If an LLM client is available the narration is LLM-generated; otherwise
        a deterministic template-based fallback is used.

        Parameters
        ----------
        topic:
            The overall document topic (e.g., ``"Time Dilation"``).
        ku:
            The :class:`~vividoc.core.models.KnowledgeUnitSpec` to narrate.

        Returns
        -------
        NarrationResult
        """
        if self.llm_client is not None:
            return self._generate_with_llm(topic, ku)
        return self._generate_template(topic, ku)

    def generate_all(
        self, topic: str, knowledge_units: list[KnowledgeUnitSpec]
    ) -> list[NarrationResult]:
        """Generate narration for every knowledge unit in a document."""
        results = []
        for ku in knowledge_units:
            logger.info(f"Generating narration for unit: {ku.id}")
            result = self.generate(topic, ku)
            results.append(result)
        return results

    # ------------------------------------------------------------------
    # LLM-based generation
    # ------------------------------------------------------------------

    def _generate_with_llm(self, topic: str, ku: KnowledgeUnitSpec) -> NarrationResult:
        prompt = get_narration_prompt(
            topic=topic,
            unit_id=ku.id,
            unit_content=ku.unit_content,
            text_description=ku.text_description,
            interaction_spec=ku.interaction_spec,
        )
        raw = self.llm_client.call_text_generation(prompt)

        # The prompt asks for JSON output; try to parse it
        try:
            data = json.loads(raw)
            script = data.get("script", "")
            cues = data.get("cues", [])
            # Normalize cues: ensure each has timestamp (float) and cue (str)
            normalized_cues = []
            for c in cues:
                normalized_cues.append(
                    {
                        "timestamp": float(c.get("timestamp", 0)),
                        "cue": str(c.get("cue", "")),
                    }
                )
            return NarrationResult(
                unit_id=ku.id,
                script=script,
                narration_cues=normalized_cues,
            )
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning(
                f"Failed to parse LLM narration output for '{ku.id}' ({exc}); "
                "falling back to template-based narration."
            )
            return self._generate_template(topic, ku)

    # ------------------------------------------------------------------
    # Template-based fallback (no LLM required)
    # ------------------------------------------------------------------

    def _generate_template(self, topic: str, ku: KnowledgeUnitSpec) -> NarrationResult:
        """Deterministic narration built from SRTC fields."""
        spec = ku.interaction_spec

        # Build script sections
        intro = (
            f"In this section we explore {ku.unit_content}. "
            f"{ku.text_description}"
        )
        intro = _truncate(intro, max_words=80)

        render_desc = _render_description(spec.render)
        transition_desc = _transition_description(spec.transition)
        constraint_line = (
            f"The key insight to take away is: {spec.constraint}"
            if spec.constraint
            else f"Pay close attention to how {ku.unit_content} behaves."
        )
        outro = (
            f"Take a moment to absorb this. "
            f"In the next section we will build on what we've just seen about {topic}."
        )

        script = " ".join(
            [intro, render_desc, transition_desc, constraint_line, outro]
        )
        script = _ensure_word_count(script, target=200)

        # Build cues tied to approximate keyframe timestamps
        cues: list[dict[str, Any]] = [
            {"timestamp": 0.0, "cue": f"Welcome to our exploration of {ku.unit_content}."},
            {"timestamp": 2.0, "cue": render_desc},
        ]
        t = 7.0
        for transition in spec.transition:
            cues.append({"timestamp": t, "cue": f"Now, {transition.lower().rstrip('.')}."})
            t += max(3.0, len(transition.split()) * 0.5)

        cues.append({"timestamp": t, "cue": constraint_line})
        cues.append({"timestamp": t + 5.0, "cue": outro})

        return NarrationResult(
            unit_id=ku.id,
            script=script,
            narration_cues=cues,
        )


# ---------------------------------------------------------------------------
# Internal text helpers
# ---------------------------------------------------------------------------


def _render_description(render_elements: list[str]) -> str:
    if not render_elements:
        return "The scene will show the key concepts visually."
    if len(render_elements) == 1:
        return f"You will see {render_elements[0].lower()}."
    listed = ", ".join(render_elements[:-1]) + f", and {render_elements[-1]}"
    return f"The visualization displays {listed.lower()}."


def _transition_description(transitions: list[str]) -> str:
    if not transitions:
        return "This is a static visualization — observe it carefully."
    if len(transitions) == 1:
        return f"Interaction: {transitions[0].rstrip('.')}."
    lines = [f"{t.rstrip('.')}." for t in transitions]
    return "The animation proceeds through the following steps: " + " ".join(lines)


def _truncate(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def _ensure_word_count(text: str, target: int = 200) -> str:
    """Pad text lightly if under target; truncate if significantly over."""
    words = text.split()
    if len(words) < target * 0.7:
        padding = textwrap.dedent(
            """\
            Understanding this concept is foundational for what comes next.
            Mathematical and scientific ideas like this one often reveal deep
            symmetries in nature, and seeing them animated can make abstract
            relationships concrete and intuitive.
            """
        )
        text = text.rstrip() + " " + padding.replace("\n", " ")
    elif len(words) > target * 1.4:
        text = " ".join(words[: int(target * 1.2)])
    return text
