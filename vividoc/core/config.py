"""Unified configuration for vividoc pipeline."""

from dataclasses import dataclass
from typing import Set

AVAILABLE_LLM_MODELS: Set[str] = {
    "openrouter/google/gemini-3-flash-preview",
}


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

    @staticmethod
    def validate_llm_model(llm_model: str) -> None:
        """
        Validate that the LLM model is in the available models set.

        Args:
            llm_model: Model string in format "provider/model-name"

        Raises:
            ValueError: If the model is not in the available models set
        """
        if llm_model not in AVAILABLE_LLM_MODELS:
            available_list = "\n  - ".join(sorted(AVAILABLE_LLM_MODELS))
            raise ValueError(
                f"Invalid llm_model: '{llm_model}'\n\n"
                f"Available models:\n  - {available_list}\n\n"
                f"Format: 'provider/model-name'"
            )

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate_llm_model(self.llm_model)
