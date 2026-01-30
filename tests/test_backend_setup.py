"""Tests for backend project structure and core models."""

import pytest
from fastapi.testclient import TestClient
from vividoc.entrypoint.web_server import create_app
from vividoc.entrypoint.models import (
    SpecGenerateRequest,
    JobStatusResponse,
    ProgressInfo,
    KUProgress,
)
from vividoc.entrypoint.services import JobManager, SpecService, DocumentService


def test_fastapi_app_creation():
    """Test that FastAPI app is created successfully."""
    app = create_app()
    assert app is not None
    assert app.title == "ViviDoc Web UI API"


def test_health_endpoint():
    """Test health check endpoint."""
    app = create_app()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """Test root endpoint."""
    app = create_app()
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "ViviDoc Web UI API"
    assert data["status"] == "running"


def test_cors_middleware():
    """Test that CORS middleware is configured."""
    app = create_app()
    # Check that middleware is present
    # FastAPI wraps middleware in Middleware objects
    assert len(app.user_middleware) > 0
    # Just verify middleware exists, the actual CORS functionality
    # will be tested through integration tests


def test_api_models_import():
    """Test that all API models can be imported."""
    # Test request models
    request = SpecGenerateRequest(topic="Test Topic")
    assert request.topic == "Test Topic"

    # Test response models
    assert ProgressInfo is not None
    assert KUProgress is not None
    assert JobStatusResponse is not None


def test_services_import():
    """Test that all services can be imported."""
    assert JobManager is not None
    assert SpecService is not None
    assert DocumentService is not None


def test_job_manager_creation():
    """Test JobManager can be instantiated."""
    job_manager = JobManager()
    assert job_manager.jobs == {}
    assert job_manager.lock is not None


def test_job_creation():
    """Test creating a job."""
    job_manager = JobManager()
    job_id = job_manager.create_job("spec_generation")

    assert job_id is not None
    assert len(job_id) > 0

    job = job_manager.get_status(job_id)
    assert job is not None
    assert job.job_id == job_id
    assert job.job_type == "spec_generation"
    assert job.status == "running"
    assert job.progress.phase == "planning"
    assert job.progress.overall_percent == 0.0


def test_job_status_update():
    """Test updating job status."""
    job_manager = JobManager()
    job_id = job_manager.create_job("document_generation")

    # Update progress
    job_manager.update_progress(
        job_id, {"phase": "executing", "overall_percent": 50.0, "current_ku": "ku_1"}
    )

    job = job_manager.get_status(job_id)
    assert job.progress.phase == "executing"
    assert job.progress.overall_percent == 50.0
    assert job.progress.current_ku == "ku_1"


def test_job_completion():
    """Test marking job as completed."""
    job_manager = JobManager()
    job_id = job_manager.create_job("document_generation")

    result = {"document_id": "doc_123"}
    job_manager.mark_completed(job_id, result)

    job = job_manager.get_status(job_id)
    assert job.status == "completed"
    assert job.result == result
    assert job.progress.overall_percent == 100.0


def test_job_failure():
    """Test marking job as failed."""
    job_manager = JobManager()
    job_id = job_manager.create_job("spec_generation")

    error_msg = "Test error"
    job_manager.mark_failed(job_id, error_msg)

    job = job_manager.get_status(job_id)
    assert job.status == "failed"
    assert job.error == error_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
