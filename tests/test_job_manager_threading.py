"""Thread-safety tests for JobManager."""

import pytest
import threading
from vividoc.entrypoint.services.job_manager import JobManager


def test_concurrent_job_creation():
    """Test that multiple threads can create jobs concurrently without conflicts."""
    job_manager = JobManager()
    job_ids = []
    lock = threading.Lock()

    def create_jobs(count):
        """Create multiple jobs in a thread."""
        local_ids = []
        for _ in range(count):
            job_id = job_manager.create_job("document_generation")
            local_ids.append(job_id)

        # Add to shared list with lock
        with lock:
            job_ids.extend(local_ids)

    # Create 10 threads, each creating 10 jobs
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=create_jobs, args=(10,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all jobs were created
    assert len(job_ids) == 100

    # Verify all job IDs are unique
    assert len(set(job_ids)) == 100

    # Verify all jobs exist in job manager
    for job_id in job_ids:
        job = job_manager.get_status(job_id)
        assert job is not None
        assert job.job_id == job_id


def test_concurrent_progress_updates():
    """Test that multiple threads can update job progress concurrently."""
    job_manager = JobManager()
    job_id = job_manager.create_job("document_generation")

    def update_progress(phase, percent):
        """Update job progress."""
        job_manager.update_progress(
            job_id, {"phase": phase, "overall_percent": percent}
        )

    # Create multiple threads updating progress
    threads = []
    updates = [
        ("executing", 25.0),
        ("executing", 50.0),
        ("executing", 75.0),
        ("evaluating", 90.0),
    ]

    for phase, percent in updates:
        thread = threading.Thread(target=update_progress, args=(phase, percent))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify job still exists and has valid state
    job = job_manager.get_status(job_id)
    assert job is not None
    assert job.status == "running"
    # Progress should be one of the updated values
    assert job.progress.overall_percent in [25.0, 50.0, 75.0, 90.0]
    assert job.progress.phase in ["executing", "evaluating"]


def test_concurrent_status_reads():
    """Test that multiple threads can read job status concurrently."""
    job_manager = JobManager()
    job_id = job_manager.create_job("spec_generation")

    results = []
    lock = threading.Lock()

    def read_status():
        """Read job status multiple times."""
        for _ in range(100):
            job = job_manager.get_status(job_id)
            with lock:
                results.append(job)

    # Create 10 threads, each reading status 100 times
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=read_status)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all reads succeeded
    assert len(results) == 1000
    assert all(job is not None for job in results)
    assert all(job.job_id == job_id for job in results)


def test_concurrent_completion_marking():
    """Test that marking jobs as completed is thread-safe."""
    job_manager = JobManager()

    # Create multiple jobs
    job_ids = [job_manager.create_job("document_generation") for _ in range(10)]

    def mark_complete(job_id, result_value):
        """Mark a job as completed."""
        job_manager.mark_completed(job_id, {"value": result_value})

    # Mark all jobs as completed concurrently
    threads = []
    for i, job_id in enumerate(job_ids):
        thread = threading.Thread(target=mark_complete, args=(job_id, i))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all jobs are marked as completed
    for i, job_id in enumerate(job_ids):
        job = job_manager.get_status(job_id)
        assert job.status == "completed"
        assert job.result == {"value": i}
        assert job.progress.overall_percent == 100.0


def test_concurrent_mixed_operations():
    """Test mixed concurrent operations (create, update, read, complete)."""
    job_manager = JobManager()
    job_ids = []
    lock = threading.Lock()

    def create_and_update():
        """Create a job and update its progress."""
        job_id = job_manager.create_job("document_generation")
        with lock:
            job_ids.append(job_id)

        # Update progress
        job_manager.update_progress(
            job_id, {"phase": "executing", "overall_percent": 50.0}
        )

        # Read status
        job = job_manager.get_status(job_id)
        assert job is not None

        # Mark completed
        job_manager.mark_completed(job_id, {"done": True})

    # Run multiple threads performing mixed operations
    threads = []
    for _ in range(20):
        thread = threading.Thread(target=create_and_update)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all jobs were created and completed
    assert len(job_ids) == 20
    for job_id in job_ids:
        job = job_manager.get_status(job_id)
        assert job is not None
        assert job.status == "completed"
        assert job.result == {"done": True}


def test_concurrent_failure_marking():
    """Test that marking jobs as failed is thread-safe."""
    job_manager = JobManager()

    # Create multiple jobs
    job_ids = [job_manager.create_job("spec_generation") for _ in range(10)]

    def mark_failed_job(job_id, error_msg):
        """Mark a job as failed."""
        job_manager.mark_failed(job_id, error_msg)

    # Mark all jobs as failed concurrently
    threads = []
    for i, job_id in enumerate(job_ids):
        thread = threading.Thread(target=mark_failed_job, args=(job_id, f"Error {i}"))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all jobs are marked as failed
    for i, job_id in enumerate(job_ids):
        job = job_manager.get_status(job_id)
        assert job.status == "failed"
        assert job.error == f"Error {i}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
