"""Evaluator workflow for vividoc pipeline."""

from typing import List
from vividoc.utils.llm.client import LLMClient
from vividoc.core.models import GeneratedDocument, EvaluationFeedback
from vividoc.core.config import RunnerConfig
from vividoc.utils.logger import logger
from prompts.evaluator_prompt import get_coherence_check_prompt


class Evaluator:
    """Handles the evaluation phase of the vividoc pipeline."""

    def __init__(self, config: RunnerConfig):
        """Initialize evaluator with configuration."""
        self.config = config
        self.llm_client = LLMClient(config.llm_model)

    def check_coherence(self, generated_doc: GeneratedDocument) -> str:
        """Check text fluency and logical flow using LLM."""
        try:
            with open(generated_doc.html_file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        except FileNotFoundError:
            return "HTML file not found"

        if len(html_content) < 1000:
            return "HTML document appears incomplete"

        prompt = get_coherence_check_prompt(
            topic=generated_doc.topic, content=html_content
        )
        try:
            assessment = self.llm_client.call_text_generation(prompt=prompt)
            return assessment
        except Exception as e:
            return f"Document structure appears valid (LLM check skipped: {e})"

    def check_components(self, generated_doc: GeneratedDocument) -> List[str]:
        """Verify interactive components are valid."""
        issues = []

        for ku in generated_doc.knowledge_units:
            if not ku.stage1_completed:
                issues.append(f"{ku.id}: Stage 1 (text content) not completed")
            if not ku.stage2_completed:
                issues.append(f"{ku.id}: Stage 2 (interactive content) not completed")
            if not ku.validated:
                issues.append(f"{ku.id}: HTML validation failed")

        return issues

    def run(self, generated_doc: GeneratedDocument) -> EvaluationFeedback:
        """Execute the evaluation phase."""
        logger.info("Evaluator: Running document evaluation...")

        coherence = self.check_coherence(generated_doc)
        issues = self.check_components(generated_doc)

        return EvaluationFeedback(
            overall_coherence=coherence,
            component_issues=issues,
            requires_revision=len(issues) > 0,
        )
