"""Unified configuration for vividoc pipeline."""

from dataclasses import dataclass, field


@dataclass
class RunnerConfig:
    """Unified configuration for running complete pipeline."""

    llm_model: str
    max_fix_attempts: int = 3
    output_dir: str = "output"
    resume: bool = False
    plan_only: bool = False
    execute_only: bool = False
    evaluate_only: bool = False
    text_style_instructions: str = ""
    interaction_style_instructions: str = ""

    def __post_init__(self):
        if "/" not in self.llm_model:
            raise ValueError(
                f"Invalid llm_model format: '{self.llm_model}'. "
                "Expected 'provider/model-name', e.g. 'openrouter/google/gemini-2.5-pro' "
                "or 'anthropic/claude-sonnet-4-5'."
            )
