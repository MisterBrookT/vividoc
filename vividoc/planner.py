"""Planner workflow for vividoc pipeline."""

from dataclasses import dataclass
from vividoc.utils.llm.client import LLMClient
from vividoc.models import DocumentSpec
from prompts.planner_prompt import get_planner_prompt


@dataclass
class PlannerConfig:
    """Configuration for planning phase."""

    llm_provider: str = "google"
    llm_model: str = "gemini-2.5-pro"
    output_path: str = "output/doc_spec.json"


class Planner:
    """Handles the planning phase of the vividoc pipeline."""

    def __init__(self, config: PlannerConfig):
        """Initialize planner with configuration."""
        self.config = config
        self.llm_client = LLMClient(config.llm_provider)

    def run(self, topic: str) -> DocumentSpec:
        """Execute the planning phase to generate document specification."""
        prompt = get_planner_prompt(topic)
        doc_spec = self.llm_client.call_structured_output(
            model=self.config.llm_model, prompt=prompt, schema=DocumentSpec
        )
        return doc_spec
