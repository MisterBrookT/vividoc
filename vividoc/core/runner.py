"""Runner workflow for vividoc pipeline."""

from pathlib import Path
from vividoc.core.planner import Planner
from vividoc.core.executor import Executor
from vividoc.core.evaluator import Evaluator
from vividoc.core.models import GeneratedDocument, DocumentSpec
from vividoc.core.config import RunnerConfig
from vividoc.utils.io import save_json, load_json
from vividoc.utils.logger import logger
from vividoc.utils.naming import topic_to_dirname, model_to_method_suffix


class Runner:
    """Handles the complete pipeline execution."""

    def __init__(self, config: RunnerConfig):
        """Initialize runner with configuration."""
        self.config = config

        # Create base output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)

        self.planner = Planner(config)
        self.executor = Executor(
            config,
            text_style_instructions=config.text_style_instructions,
            interaction_style_instructions=config.interaction_style_instructions,
        )
        self.evaluator = Evaluator(config)

    def _get_topic_dir(self, topic: str) -> Path:
        """Get output directory for a topic: {topic_name}/vividoc_{model_suffix}/."""
        dirname = topic_to_dirname(topic)
        suffix = model_to_method_suffix(self.config.llm_model)
        method_name = f"vividoc_{suffix}"
        topic_dir = Path(self.config.output_dir) / dirname / method_name
        topic_dir.mkdir(parents=True, exist_ok=True)
        return topic_dir

    def run(self, topic: str) -> GeneratedDocument:
        """Execute the complete pipeline: plan → exec → eval."""
        import json
        import time
        from datetime import datetime

        logger.info(f"Starting pipeline for topic: {topic}")
        t0 = time.time()

        # Get topic-specific directory
        topic_dir = self._get_topic_dir(topic)
        logger.info(f"Output directory: {topic_dir}")

        # Phase 1: Planning
        spec_path = topic_dir / "spec.json"
        if self.config.resume and spec_path.exists():
            logger.info("Phase 1: Planning (resuming from existing spec)...")
            doc_spec = load_json(str(spec_path), DocumentSpec)
            logger.info(f"Loaded {len(doc_spec.knowledge_units)} knowledge units")
        else:
            logger.info("Phase 1: Planning...")
            doc_spec = self.planner.run(topic)
            save_json(doc_spec, str(spec_path))
            logger.info(f"Generated {len(doc_spec.knowledge_units)} knowledge units")

        # Phase 2: Execution
        # Update executor output_dir to topic-specific directory
        from dataclasses import replace

        self.executor.config = replace(self.executor.config, output_dir=str(topic_dir))

        doc_path = topic_dir / "generated_doc.json"
        if self.config.resume and doc_path.exists():
            logger.info("Phase 2: Execution (resuming from existing document)...")
            generated_doc = load_json(str(doc_path), GeneratedDocument)
        else:
            logger.info("Phase 2: Execution...")
            generated_doc = self.executor.run(doc_spec)

        # Phase 3: Evaluation
        eval_path = topic_dir / "evaluation.json"
        if self.config.resume and eval_path.exists():
            logger.info("Phase 3: Evaluation (resuming from existing evaluation)...")
            from vividoc.core.models import EvaluationFeedback

            feedback = load_json(str(eval_path), EvaluationFeedback)
        else:
            logger.info("Phase 3: Evaluation...")
            feedback = self.evaluator.run(generated_doc)
            save_json(feedback, str(eval_path))

        if feedback.requires_revision:
            logger.warning(
                f"Document requires revision: {len(feedback.component_issues)} issues found"
            )
        else:
            logger.info("Document validated successfully")

        # Save meta.json with timing (only if not already present)
        elapsed = time.time() - t0
        meta_path = topic_dir / "meta.json"
        if not meta_path.exists():
            html_path = topic_dir / "document.html"
            html_length = (
                len(html_path.read_text(encoding="utf-8")) if html_path.exists() else 0
            )

            meta = {
                "topic": topic,
                "model": self.config.llm_model,
                "baseline": "vividoc",
                "elapsed_sec": round(elapsed, 2),
                "html_length": html_length,
                "num_kus": len(doc_spec.knowledge_units),
                "timestamp": datetime.now().isoformat(),
            }
            meta_path.write_text(
                json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
            )

        logger.info(f"Pipeline completed in {elapsed:.1f}s")
        return generated_doc
