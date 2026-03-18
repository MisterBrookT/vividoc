"""Evaluator workflow for vividoc pipeline."""

import re
from typing import List
from vividoc.core.models import GeneratedDocument, EvaluationFeedback
from vividoc.core.config import RunnerConfig
from vividoc.utils.logger import logger


class Evaluator:
    """Handles the evaluation phase of the vividoc pipeline (rule-based)."""

    def __init__(self, config: RunnerConfig):
        self.config = config

    def check_html(self, generated_doc: GeneratedDocument) -> str:
        """Check HTML file exists and has valid basic structure."""
        try:
            with open(generated_doc.html_file_path, "r", encoding="utf-8") as f:
                html = f.read()
        except FileNotFoundError:
            return "HTML file not found"

        if len(html) < 500:
            return "HTML document appears incomplete (< 500 chars)"

        if not re.search(r"<html", html, re.IGNORECASE):
            return "Missing <html> tag"
        if not re.search(r"<body", html, re.IGNORECASE):
            return "Missing <body> tag"
        if not re.search(r"</html>", html, re.IGNORECASE):
            return "Missing closing </html> tag"

        return "OK"

    def check_components(self, generated_doc: GeneratedDocument) -> List[str]:
        """Verify all knowledge units completed both stages."""
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
        """Execute rule-based evaluation."""
        logger.info("Evaluator: Running document evaluation...")

        html_status = self.check_html(generated_doc)
        issues = self.check_components(generated_doc)

        if html_status != "OK":
            issues.insert(0, html_status)

        return EvaluationFeedback(
            overall_coherence=html_status,
            component_issues=issues,
            requires_revision=len(issues) > 0,
        )
