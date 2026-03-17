"""Naive Agent runner: single-shot LLM generation without planning or evaluation."""

import json
import time
from pathlib import Path
from datetime import datetime

from vividoc.utils.llm.client import LLMClient
from vividoc.utils.logger import logger
from vividoc.utils.naming import topic_to_dirname
from .prompt import get_naive_agent_prompt

BASELINE_NAME = "naive_agent"


class NaiveAgentRunner:
    """Single-shot baseline: one LLM call to generate the entire document."""

    def __init__(self, llm_model: str, output_dir: str = "outputs"):
        self.llm_model = llm_model
        self.client = LLMClient(llm_model)
        self.output_dir = Path(output_dir)

    def _get_topic_dir(self, topic: str) -> Path:
        """Get output directory: outputs/{topic_name}/naive_agent/."""
        dirname = topic_to_dirname(topic)
        topic_dir = self.output_dir / dirname / BASELINE_NAME
        topic_dir.mkdir(parents=True, exist_ok=True)
        return topic_dir

    def run(self, topic: str, *, skip_existing: bool = True) -> dict:
        """Generate an interactive document in a single LLM call.

        Args:
            topic: The topic to generate a document about.
            skip_existing: If True, skip generation when document.html already exists.

        Returns:
            Dict with topic, status, model, elapsed_sec, html_length.
        """
        out = self._get_topic_dir(topic)
        html_path = out / "document.html"

        if skip_existing and html_path.exists():
            logger.info(f"[{BASELINE_NAME}] Skip (exists): {topic[:60]}")
            return {"topic": topic, "status": "skipped"}

        logger.info(f"[{BASELINE_NAME}] Generating: {topic[:60]}")
        t0 = time.time()

        prompt = get_naive_agent_prompt(topic)
        html = self.client.call_text_generation(prompt=prompt)

        html_path.write_text(html, encoding="utf-8")

        elapsed = time.time() - t0
        meta = {
            "topic": topic,
            "model": self.llm_model,
            "elapsed_sec": round(elapsed, 2),
            "html_length": len(html),
            "timestamp": datetime.now().isoformat(),
        }
        (out / "meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        logger.info(f"[{BASELINE_NAME}] Done {elapsed:.1f}s ({len(html)} chars)")
        return {**meta, "status": "ok"}
