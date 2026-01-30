"""Runner workflow for vividoc pipeline."""

from dataclasses import dataclass
from pathlib import Path
import hashlib
import uuid
from vividoc.planner import Planner, PlannerConfig
from vividoc.executor import Executor, ExecutorConfig
from vividoc.evaluator import Evaluator, EvaluatorConfig
from vividoc.models import GeneratedDocument, DocumentSpec
from vividoc.utils.io import save_json, load_json
from vividoc.utils.logger import logger


@dataclass
class RunnerConfig:
    """Configuration for running complete pipeline."""

    llm_provider: str = "google"
    llm_model: str = "gemini-2.5-pro"
    output_dir: str = "outputs"
    resume: bool = False


def topic_to_uuid(topic: str) -> str:
    """Generate deterministic UUID from topic using MD5 hash."""
    hash_obj = hashlib.md5(topic.encode("utf-8"))
    return str(uuid.UUID(hash_obj.hexdigest()))


class Runner:
    """Handles the complete pipeline execution."""

    def __init__(self, config: RunnerConfig):
        """Initialize runner with configuration."""
        self.config = config

        # Create base output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)

        self.planner = Planner(
            PlannerConfig(
                llm_provider=config.llm_provider,
                llm_model=config.llm_model,
            )
        )

        self.executor = Executor(
            ExecutorConfig(
                llm_provider=config.llm_provider,
                llm_model=config.llm_model,
                resume=config.resume,
            )
        )

        self.evaluator = Evaluator(
            EvaluatorConfig(
                llm_provider=config.llm_provider,
                llm_model=config.llm_model,
            )
        )

    def _get_topic_dir(self, topic: str) -> Path:
        """Get output directory for a topic (using UUID)."""
        topic_uuid = topic_to_uuid(topic)
        topic_dir = Path(self.config.output_dir) / topic_uuid
        topic_dir.mkdir(parents=True, exist_ok=True)
        return topic_dir

    def run(self, topic: str) -> GeneratedDocument:
        """Execute the complete pipeline: plan → exec → eval."""
        logger.info(f"Starting pipeline for topic: {topic}")

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
        self.executor.config.output_dir = str(topic_dir)
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
            from vividoc.models import EvaluationFeedback

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

        logger.info("Pipeline completed")
        return generated_doc
