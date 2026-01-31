"""Planner workflow for vividoc pipeline."""

from vividoc.utils.llm.client import LLMClient
from vividoc.core.models import DocumentSpec
from vividoc.core.config import RunnerConfig
from prompts.planner_prompt import get_planner_prompt


class Planner:
    """Handles the planning phase of the vividoc pipeline."""

    def __init__(self, config: RunnerConfig):
        """Initialize planner with configuration."""
        self.config = config
        self.llm_client = LLMClient(config.llm_model)

    def run(self, topic: str) -> DocumentSpec:
        """Execute the planning phase to generate document specification."""
        prompt = get_planner_prompt(topic)
        doc_spec = self.llm_client.call_structured_output(
            prompt=prompt, schema=DocumentSpec
        )
        return doc_spec
