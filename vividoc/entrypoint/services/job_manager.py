"""Job management system for asynchronous task execution."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List, Callable, Any
import threading
import uuid


@dataclass
class KUProgress:
    """Progress information for a single knowledge unit."""

    ku_id: str
    title: str
    status: str  # "pending" | "stage1" | "stage2" | "completed"


@dataclass
class ProgressInfo:
    """Progress information for a job."""

    phase: str  # "planning" | "executing" | "evaluating"
    overall_percent: float
    current_ku: Optional[str] = None
    ku_stage: Optional[str] = None  # "stage1" | "stage2"
    ku_progress: List[KUProgress] = field(default_factory=list)


@dataclass
class Job:
    """Job data structure for tracking asynchronous tasks."""

    job_id: str
    job_type: str  # "spec_generation" | "document_generation"
    status: str  # "running" | "completed" | "failed"
    created_at: datetime
    progress: ProgressInfo
    result: Optional[Any] = None
    error: Optional[str] = None


class JobManager:
    """Manages asynchronous job execution and progress tracking."""

    def __init__(self):
        """Initialize the job manager with in-memory storage."""
        self.jobs: Dict[str, Job] = {}
        self.lock = threading.Lock()

    def create_job(self, job_type: str) -> str:
        """
        Create a new job and return its ID.

        Args:
            job_type: Type of job ("spec_generation" or "document_generation")

        Returns:
            Unique job identifier
        """
        job_id = str(uuid.uuid4())

        with self.lock:
            job = Job(
                job_id=job_id,
                job_type=job_type,
                status="running",
                created_at=datetime.now(),
                progress=ProgressInfo(
                    phase="planning" if job_type == "spec_generation" else "executing",
                    overall_percent=0.0,
                    ku_progress=[],
                ),
            )
            self.jobs[job_id] = job

        return job_id

    def start_job(self, job_id: str, target_fn: Callable, *args, **kwargs):
        """
        Execute job in background thread.

        Args:
            job_id: Job identifier
            target_fn: Function to execute in background
            *args: Positional arguments for target function
            **kwargs: Keyword arguments for target function
        """
        thread = threading.Thread(
            target=target_fn, args=args, kwargs=kwargs, daemon=True
        )
        thread.start()

    def update_progress(self, job_id: str, progress_update: Dict[str, Any]):
        """
        Update job progress (called by callbacks).

        Args:
            job_id: Job identifier
            progress_update: Dictionary with progress information
        """
        with self.lock:
            if job_id not in self.jobs:
                return

            job = self.jobs[job_id]

            # Update phase if provided
            if "phase" in progress_update:
                job.progress.phase = progress_update["phase"]

            # Update overall percent if provided
            if "overall_percent" in progress_update:
                job.progress.overall_percent = progress_update["overall_percent"]

            # Update current KU if provided
            if "current_ku" in progress_update:
                job.progress.current_ku = progress_update["current_ku"]

            # Update KU stage if provided
            if "ku_stage" in progress_update:
                job.progress.ku_stage = progress_update["ku_stage"]

            # Update KU progress list if provided
            if "ku_progress" in progress_update:
                job.progress.ku_progress = progress_update["ku_progress"]

    def get_status(self, job_id: str) -> Optional[Job]:
        """
        Get current job status and progress.

        Args:
            job_id: Job identifier

        Returns:
            Job object or None if not found
        """
        with self.lock:
            return self.jobs.get(job_id)

    def mark_completed(self, job_id: str, result: Any):
        """
        Mark job as completed with result.

        Args:
            job_id: Job identifier
            result: Result data from job execution
        """
        with self.lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                job.status = "completed"
                job.result = result
                job.progress.overall_percent = 100.0

    def mark_failed(self, job_id: str, error: str):
        """
        Mark job as failed with error message.

        Args:
            job_id: Job identifier
            error: Error message
        """
        with self.lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                job.status = "failed"
                job.error = error
