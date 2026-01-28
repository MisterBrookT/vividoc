"""Runner workflow for vividoc pipeline."""

from dataclasses import dataclass
from pathlib import Path
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
    output_dir: str = "output"
    resume: bool = False


class Runner:
    """Handles the complete pipeline execution."""
    
    def __init__(self, config: RunnerConfig):
        """Initialize runner with configuration."""
        self.config = config
        
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        
        self.planner = Planner(PlannerConfig(
            llm_provider=config.llm_provider,
            llm_model=config.llm_model,
            output_path=f"{config.output_dir}/doc_spec.json"
        ))
        
        self.executor = Executor(ExecutorConfig(
            llm_provider=config.llm_provider,
            llm_model=config.llm_model,
            output_dir=config.output_dir,
            resume=config.resume
        ))
        
        self.evaluator = Evaluator(EvaluatorConfig(
            llm_provider=config.llm_provider,
            llm_model=config.llm_model,
            output_path=f"{config.output_dir}/evaluation.json"
        ))
    
    def run(self, topic: str) -> GeneratedDocument:
        """Execute the complete pipeline: plan → exec → eval."""
        logger.info(f"Starting pipeline for topic: {topic}")
        
        # Phase 1: Planning
        spec_path = self.planner.config.output_path
        if self.config.resume and Path(spec_path).exists():
            logger.info("Phase 1: Planning (resuming from existing spec)...")
            doc_spec = load_json(spec_path, DocumentSpec)
            logger.info(f"Loaded {len(doc_spec.knowledge_units)} knowledge units")
        else:
            logger.info("Phase 1: Planning...")
            doc_spec = self.planner.run(topic)
            save_json(doc_spec, spec_path)
            logger.info(f"Generated {len(doc_spec.knowledge_units)} knowledge units")
        
        # Phase 2: Execution
        doc_path = f"{self.config.output_dir}/generated_doc.json"
        if self.config.resume and Path(doc_path).exists():
            logger.info("Phase 2: Execution (resuming from existing document)...")
            generated_doc = load_json(doc_path, GeneratedDocument)
        else:
            logger.info("Phase 2: Execution...")
            generated_doc = self.executor.run(doc_spec)
        
        # Phase 3: Evaluation
        eval_path = self.evaluator.config.output_path
        if self.config.resume and Path(eval_path).exists():
            logger.info("Phase 3: Evaluation (resuming from existing evaluation)...")
            from vividoc.models import EvaluationFeedback
            feedback = load_json(eval_path, EvaluationFeedback)
        else:
            logger.info("Phase 3: Evaluation...")
            feedback = self.evaluator.run(generated_doc)
            save_json(feedback, eval_path)
        
        if feedback.requires_revision:
            logger.warning(f"Document requires revision: {len(feedback.component_issues)} issues found")
        else:
            logger.info("Document validated successfully")
        
        logger.info("Pipeline completed")
        return generated_doc