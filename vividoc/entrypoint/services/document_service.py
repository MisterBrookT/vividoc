"""Service for document generation and management."""

from typing import Dict, Optional
import uuid
from datetime import datetime
from vividoc.core.models import DocumentSpec
from vividoc.core.config import RunnerConfig
from vividoc.core.evaluator import Evaluator
from .job_manager import JobManager, KUProgress
from .executor_with_progress import ExecutorWithProgress


class DocumentService:
    """Handles document generation and storage."""

    def __init__(
        self,
        config: RunnerConfig,
        evaluator: Evaluator,
        job_manager: JobManager,
    ):
        """
        Initialize the document service.

        Args:
            config: RunnerConfig for creating ExecutorWithProgress instances
            evaluator: ViviDoc Evaluator instance
            job_manager: JobManager for async execution
        """
        self.config = config
        self.evaluator = evaluator
        self.job_manager = job_manager
        self.documents: Dict[str, Dict] = {}  # document_id -> metadata
        self.document_specs: Dict[str, str] = {}  # document_id -> spec_id
        self.job_specs: Dict[str, str] = {}  # job_id -> spec_id

    def generate_document(self, spec_id: str, spec: DocumentSpec) -> str:
        """
        Start document generation job, return job_id.

        Args:
            spec_id: Spec identifier
            spec: DocumentSpec to generate from

        Returns:
            Job identifier
        """
        # Create job
        job_id = self.job_manager.create_job("document_generation")

        # Track job_id to spec_id mapping for real-time HTML access
        self.job_specs[job_id] = spec_id

        # Start background execution
        self.job_manager.start_job(
            job_id, self._execute_generation, job_id, spec_id, spec
        )

        return job_id

    def _execute_generation(self, job_id: str, spec_id: str, spec: DocumentSpec):
        """
        Background task: execute generation with progress callbacks.

        Args:
            job_id: Job identifier
            spec_id: Spec identifier
            spec: DocumentSpec to generate from
        """
        try:
            # Initialize KU progress tracking
            ku_progress_list = []
            for idx, ku_spec in enumerate(spec.knowledge_units, 1):
                scope_id = f"ku{idx}"
                ku_progress_list.append(
                    KUProgress(ku_id=scope_id, title=ku_spec.id, status="pending")
                )

            # Update job with initial KU progress list
            self.job_manager.update_progress(
                job_id,
                {
                    "phase": "executing",
                    "overall_percent": 0.0,
                    "ku_progress": ku_progress_list,
                },
            )

            # Create progress callback for this job
            def progress_callback(
                phase: str, ku_id: Optional[str], stage: Optional[str]
            ):
                self._progress_callback(job_id, phase, ku_id, stage, ku_progress_list)

            # Create executor config with spec-specific output directory
            from pathlib import Path
            from dataclasses import replace

            # Get project root and create output directory for this spec
            project_root = Path(__file__).parent.parent.parent.parent
            spec_output_dir = project_root / "outputs" / spec_id
            spec_output_dir.mkdir(parents=True, exist_ok=True)

            # Create new config with updated output_dir
            executor_config = replace(self.config, output_dir=str(spec_output_dir))

            # Create executor with progress callback
            executor = ExecutorWithProgress(
                executor_config, progress_callback=progress_callback
            )

            # Execute document generation
            generated_doc = executor.run(spec)

            # Update progress to evaluating phase
            self.job_manager.update_progress(
                job_id,
                {
                    "phase": "evaluating",
                    "overall_percent": 95.0,
                    "current_ku": None,
                    "ku_stage": None,
                    "ku_progress": ku_progress_list,
                },
            )

            # Evaluate document quality
            try:
                evaluation_result = self.evaluator.evaluate(generated_doc)
                # Store evaluation result with document metadata
                evaluation_data = {
                    "score": evaluation_result.score
                    if hasattr(evaluation_result, "score")
                    else None,
                    "feedback": evaluation_result.feedback
                    if hasattr(evaluation_result, "feedback")
                    else None,
                }
            except Exception as eval_error:
                # Log evaluation error but don't fail the entire job
                # Evaluation is supplementary and shouldn't block document generation
                evaluation_data = {"error": str(eval_error)}

            # Store document
            document_id = str(uuid.uuid4())
            self.documents[document_id] = {
                "document_id": document_id,
                "created_at": datetime.now().isoformat(),
                "spec_id": spec_id,
                "html_file_path": generated_doc.html_file_path,
                "evaluation": evaluation_data,
            }
            self.document_specs[document_id] = spec_id

            # Mark job as completed
            self.job_manager.mark_completed(job_id, {"document_id": document_id})

        except Exception as e:
            # Mark job as failed
            self.job_manager.mark_failed(job_id, str(e))

    def _progress_callback(
        self,
        job_id: str,
        phase: str,
        ku_id: Optional[str],
        stage: Optional[str],
        ku_progress_list: list,
    ):
        """
        Callback invoked by Executor to report progress.

        This method updates the job status via JobManager with current progress
        information including phase, KU identifier, and stage.

        Args:
            job_id: Job identifier
            phase: Current phase ("planning" | "executing" | "evaluating")
            ku_id: Knowledge unit identifier (e.g., "ku1", "ku2")
            stage: Current stage ("stage1" | "stage2" | "completed" | None)
            ku_progress_list: List of KUProgress objects to update
        """
        # Update KU progress list based on current stage
        if ku_id and stage:
            for ku_progress in ku_progress_list:
                if ku_progress.ku_id == ku_id:
                    ku_progress.status = stage
                    break

        # Calculate overall progress based on KU completion
        total_kus = len(ku_progress_list)
        if total_kus > 0:
            completed_count = sum(
                1 for ku in ku_progress_list if ku.status == "completed"
            )
            stage1_count = sum(1 for ku in ku_progress_list if ku.status == "stage1")
            stage2_count = sum(1 for ku in ku_progress_list if ku.status == "stage2")

            # Each KU has 2 stages, so total steps = total_kus * 2
            # stage1 = 0.5 progress, stage2 = 0.5 progress, completed = 1.0 progress
            progress_sum = (
                completed_count + (stage2_count * 0.75) + (stage1_count * 0.25)
            )
            overall_percent = (progress_sum / total_kus) * 100.0
        else:
            overall_percent = 0.0

        # Update job progress
        self.job_manager.update_progress(
            job_id,
            {
                "phase": phase,
                "overall_percent": overall_percent,
                "current_ku": ku_id,
                "ku_stage": stage,
                "ku_progress": ku_progress_list,
            },
        )

    def get_document(self, document_id: str) -> Dict:
        """
        Retrieve generated document metadata.

        Args:
            document_id: Document identifier

        Returns:
            Document metadata dictionary

        Raises:
            KeyError: If document_id not found
        """
        if document_id not in self.documents:
            raise KeyError(f"Document not found: {document_id}")

        return self.documents[document_id]

    def get_html(self, document_id: str) -> str:
        """
        Get HTML content of document.

        Args:
            document_id: Document identifier

        Returns:
            HTML content as string

        Raises:
            KeyError: If document_id not found
        """
        if document_id not in self.documents:
            raise KeyError(f"Document not found: {document_id}")

        html_file_path = self.documents[document_id]["html_file_path"]

        # Read HTML file
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        return html_content

    def get_spec_id_for_job(self, job_id: str) -> Optional[str]:
        """
        Get spec_id associated with a job.

        Args:
            job_id: Job identifier

        Returns:
            Spec identifier or None if not found
        """
        return self.job_specs.get(job_id)
