"""LLM-based Styler — generates dynamic style options from spec content."""

from pydantic import BaseModel, Field

from vividoc.core.models import DocumentSpec


class StyleOption(BaseModel):
    """A single style option."""

    id: str
    label: str
    description: str


class StyleDimension(BaseModel):
    """A style dimension with multiple options."""

    id: str
    label: str
    options: list[StyleOption]


class StyleOptions(BaseModel):
    """Structured output from LLM: style dimensions grouped by category."""

    text_dimensions: list[StyleDimension] = Field(
        description="Writing/text style dimensions (max 3)"
    )
    interaction_dimensions: list[StyleDimension] = Field(
        description="Interaction/animation style dimensions (max 3)"
    )


class Styler:
    """LLM-based styler that generates dynamic style options from spec content."""

    @staticmethod
    def generate_options(spec: DocumentSpec, llm_model: str) -> dict:
        """Call LLM to generate style options based on spec content.

        Returns dict with text_dimensions and interaction_dimensions.
        """
        from prompts.styler_prompt import get_styler_prompt
        from vividoc.utils.llm.client import LLMClient

        # Build KU summaries
        ku_lines = []
        for i, ku in enumerate(spec.knowledge_units, 1):
            ku_lines.append(f"  KU{i}: {ku.unit_content} — {ku.text_description[:120]}")
        ku_summaries = "\n".join(ku_lines)

        prompt = get_styler_prompt(spec.topic, ku_summaries)

        client = LLMClient(llm_model)
        result: StyleOptions = client.call_structured_output(prompt, StyleOptions)

        return result.model_dump()

    @staticmethod
    def build_instructions(selections: dict) -> dict[str, str]:
        """Build text and interaction instruction strings from user selections.

        Args:
            selections: dict like {
                "text_selections": {"tone": "Use a friendly...", "density": "..."},
                "interaction_selections": {"animation": "Use smooth...", ...},
                "_options": {"text_dimensions": [...], "interaction_dimensions": [...]}
            }

        Returns:
            {"text": "...", "interaction": "..."}
        """
        # Build dimension id -> label lookup from cached options
        dim_labels: dict[str, str] = {}
        options = selections.get("_options") or {}
        for dim in (options.get("text_dimensions") or []) + (
            options.get("interaction_dimensions") or []
        ):
            if isinstance(dim, dict):
                dim_labels[dim.get("id", "")] = dim.get("label", "")

        text_parts = []
        for dim_id, desc in (selections.get("text_selections") or {}).items():
            if desc and desc.strip():
                val = desc.strip()
                if val.startswith("__custom__:"):
                    val = val[len("__custom__:") :]
                if val:
                    label = dim_labels.get(dim_id, dim_id)
                    text_parts.append(f"{label}: {val}")

        interaction_parts = []
        for dim_id, desc in (selections.get("interaction_selections") or {}).items():
            if desc and desc.strip():
                val = desc.strip()
                if val.startswith("__custom__:"):
                    val = val[len("__custom__:") :]
                if val:
                    label = dim_labels.get(dim_id, dim_id)
                    interaction_parts.append(f"{label}: {val}")

        text_instruction = ""
        if text_parts:
            text_instruction = "=== STYLE PREFERENCES ===\n" + "\n".join(text_parts)

        interaction_instruction = ""
        if interaction_parts:
            interaction_instruction = (
                "=== INTERACTION STYLE PREFERENCES ===\n" + "\n".join(interaction_parts)
            )

        return {"text": text_instruction, "interaction": interaction_instruction}

    @staticmethod
    def get_options() -> dict:
        """Legacy: return empty options (no longer fixed)."""
        return {}
