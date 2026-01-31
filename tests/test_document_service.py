"""Unit tests for DocumentService."""

import pytest
from unittest.mock import Mock, patch
from vividoc.entrypoint.services.document_service import DocumentService
from vividoc.entrypoint.services.job_manager import JobManager, KUProgress
from vividoc.core.models import DocumentSpec, KnowledgeUnitSpec, GeneratedDocument
from vividoc.core.config import RunnerConfig
from vividoc.core.evaluator import Evaluator


@pytest.fixture
def job_manager():
    """Create a JobManager instance."""
    return JobManager()


@pytest.fixture
def runner_config():
    """Create a RunnerConfig."""
    return RunnerConfig(output_dir="test_output")


@pytest.fixture
def mock_evaluator():
    """Create a mock Evaluator."""
    return Mock(spec=Evaluator)


@pytest.fixture
def document_service(runner_config, mock_evaluator, job_manager):
    """Create a DocumentService instance."""
    return DocumentService(runner_config, mock_evaluator, job_manager)


@pytest.fixture
def sample_spec():
    """Create a sample DocumentSpec."""
    return DocumentSpec(
        topic="Test Topic",
        knowledge_units=[
            KnowledgeUnitSpec(
                id="ku_1",
                unit_content="First KU",
                text_description="First text",
                interaction_description="First interaction",
            ),
            KnowledgeUnitSpec(
                id="ku_2",
                unit_content="Second KU",
                text_description="Second text",
                interaction_description="Second interaction",
            ),
        ],
    )


class TestDocumentServiceInit:
    """Tests for DocumentService initialization."""

    def test_init_stores_dependencies(self, runner_config, mock_evaluator, job_manager):
        """Test that __init__ stores all dependencies."""
        service = DocumentService(runner_config, mock_evaluator, job_manager)

        assert service.config == runner_config
        assert service.evaluator == mock_evaluator
        assert service.job_manager == job_manager
        assert isinstance(service.documents, dict)
        assert isinstance(service.document_specs, dict)
        assert len(service.documents) == 0
        assert len(service.document_specs) == 0


class TestDocumentServiceGenerateDocument:
    """Tests for generate_document method."""

    def test_generate_document_creates_job(self, document_service, sample_spec):
        """Test that generate_document creates a job."""
        # Act
        job_id = document_service.generate_document("spec_123", sample_spec)

        # Assert
        assert job_id is not None
        assert isinstance(job_id, str)
        assert len(job_id) > 0

        # Verify job exists in job manager
        job = document_service.job_manager.get_status(job_id)
        assert job is not None
        assert job.job_type == "document_generation"
        assert job.status == "running"

    def test_generate_document_starts_background_execution(
        self, document_service, sample_spec
    ):
        """Test that generate_document starts background execution."""
        with patch.object(document_service.job_manager, "start_job") as mock_start:
            # Act
            job_id = document_service.generate_document("spec_123", sample_spec)

            # Assert
            mock_start.assert_called_once()
            call_args = mock_start.call_args
            assert call_args[0][0] == job_id
            assert call_args[0][1] == document_service._execute_generation
            assert call_args[0][2] == job_id
            assert call_args[0][3] == "spec_123"
            assert call_args[0][4] == sample_spec

    def test_generate_document_returns_unique_job_ids(
        self, document_service, sample_spec
    ):
        """Test that generate_document returns unique job IDs."""
        # Act
        job_id_1 = document_service.generate_document("spec_1", sample_spec)
        job_id_2 = document_service.generate_document("spec_2", sample_spec)

        # Assert
        assert job_id_1 != job_id_2


class TestDocumentServiceExecuteGeneration:
    """Tests for _execute_generation background task."""

    @patch("vividoc.entrypoint.services.document_service.ExecutorWithProgress")
    def test_execute_generation_initializes_ku_progress(
        self, mock_executor_class, document_service, sample_spec
    ):
        """Test that _execute_generation initializes KU progress tracking."""
        # Setup mock executor
        mock_executor = Mock()
        mock_generated_doc = Mock(spec=GeneratedDocument)
        mock_generated_doc.html_file_path = "/path/to/doc.html"
        mock_executor.run.return_value = mock_generated_doc
        mock_executor_class.return_value = mock_executor

        # Mock evaluator to avoid errors
        document_service.evaluator.evaluate = Mock(
            return_value=Mock(score=0.9, feedback="Good")
        )

        # Create job
        job_id = document_service.job_manager.create_job("document_generation")

        # Act
        document_service._execute_generation(job_id, "spec_123", sample_spec)

        # Assert - verify job completed successfully
        job = document_service.job_manager.get_status(job_id)
        assert job.status == "completed"
        assert job.progress.overall_percent == 100.0
        assert len(job.progress.ku_progress) == 2
        assert job.progress.ku_progress[0].ku_id == "ku1"
        assert job.progress.ku_progress[0].title == "ku_1"
        assert job.progress.ku_progress[1].ku_id == "ku2"
        assert job.progress.ku_progress[1].title == "ku_2"

    @patch("vividoc.entrypoint.services.document_service.ExecutorWithProgress")
    def test_execute_generation_creates_executor_with_callback(
        self, mock_executor_class, document_service, sample_spec
    ):
        """Test that _execute_generation creates ExecutorWithProgress with callback."""
        # Setup mock executor
        mock_executor = Mock()
        mock_generated_doc = Mock(spec=GeneratedDocument)
        mock_generated_doc.html_file_path = "/path/to/doc.html"
        mock_executor.run.return_value = mock_generated_doc
        mock_executor_class.return_value = mock_executor

        # Mock evaluator
        document_service.evaluator.evaluate = Mock(
            return_value=Mock(score=0.9, feedback="Good")
        )

        # Create job
        job_id = document_service.job_manager.create_job("document_generation")

        # Act
        document_service._execute_generation(job_id, "spec_123", sample_spec)

        # Assert - verify ExecutorWithProgress was created with callback
        mock_executor_class.assert_called_once()
        call_args = mock_executor_class.call_args
        assert call_args[0][0].output_dir  # Check config has output_dir
        assert "progress_callback" in call_args[1]
        assert callable(call_args[1]["progress_callback"])

    @patch("vividoc.entrypoint.services.document_service.ExecutorWithProgress")
    def test_execute_generation_runs_executor(
        self, mock_executor_class, document_service, sample_spec
    ):
        """Test that _execute_generation runs the executor."""
        # Setup mock executor
        mock_executor = Mock()
        mock_generated_doc = Mock(spec=GeneratedDocument)
        mock_generated_doc.html_file_path = "/path/to/doc.html"
        mock_executor.run.return_value = mock_generated_doc
        mock_executor_class.return_value = mock_executor

        # Mock evaluator
        document_service.evaluator.evaluate = Mock(
            return_value=Mock(score=0.9, feedback="Good")
        )

        # Create job
        job_id = document_service.job_manager.create_job("document_generation")

        # Act
        document_service._execute_generation(job_id, "spec_123", sample_spec)

        # Assert
        mock_executor.run.assert_called_once_with(sample_spec)

    @patch("vividoc.entrypoint.services.document_service.ExecutorWithProgress")
    @patch("uuid.uuid4")
    def test_execute_generation_stores_document(
        self, mock_uuid, mock_executor_class, document_service, sample_spec
    ):
        """Test that _execute_generation stores the generated document."""
        # Setup
        mock_uuid.return_value = Mock(hex="doc_123")
        mock_uuid.return_value.__str__ = Mock(return_value="doc_123")

        mock_executor = Mock()
        mock_generated_doc = Mock(spec=GeneratedDocument)
        mock_generated_doc.html_file_path = "/path/to/doc.html"
        mock_executor.run.return_value = mock_generated_doc
        mock_executor_class.return_value = mock_executor

        # Mock evaluator
        document_service.evaluator.evaluate = Mock(
            return_value=Mock(score=0.9, feedback="Good")
        )

        # Create job
        job_id = document_service.job_manager.create_job("document_generation")

        # Act
        document_service._execute_generation(job_id, "spec_123", sample_spec)

        # Assert
        assert "doc_123" in document_service.documents
        doc_metadata = document_service.documents["doc_123"]
        assert doc_metadata["document_id"] == "doc_123"
        assert doc_metadata["spec_id"] == "spec_123"
        assert doc_metadata["html_file_path"] == "/path/to/doc.html"
        assert "created_at" in doc_metadata
        assert "evaluation" in doc_metadata

        assert document_service.document_specs["doc_123"] == "spec_123"

    @patch("vividoc.entrypoint.services.document_service.ExecutorWithProgress")
    def test_execute_generation_marks_job_completed(
        self, mock_executor_class, document_service, sample_spec
    ):
        """Test that _execute_generation marks job as completed."""
        # Setup mock executor
        mock_executor = Mock()
        mock_generated_doc = Mock(spec=GeneratedDocument)
        mock_generated_doc.html_file_path = "/path/to/doc.html"
        mock_executor.run.return_value = mock_generated_doc
        mock_executor_class.return_value = mock_executor

        # Mock evaluator
        document_service.evaluator.evaluate = Mock(
            return_value=Mock(score=0.9, feedback="Good")
        )

        # Create job
        job_id = document_service.job_manager.create_job("document_generation")

        # Act
        document_service._execute_generation(job_id, "spec_123", sample_spec)

        # Assert
        job = document_service.job_manager.get_status(job_id)
        assert job.status == "completed"
        assert job.result is not None
        assert "document_id" in job.result
        assert job.progress.overall_percent == 100.0

    @patch("vividoc.entrypoint.services.document_service.ExecutorWithProgress")
    def test_execute_generation_handles_exceptions(
        self, mock_executor_class, document_service, sample_spec
    ):
        """Test that _execute_generation handles exceptions and marks job as failed."""
        # Setup mock executor to raise exception
        mock_executor = Mock()
        mock_executor.run.side_effect = Exception("Test error")
        mock_executor_class.return_value = mock_executor

        # Create job
        job_id = document_service.job_manager.create_job("document_generation")

        # Act
        document_service._execute_generation(job_id, "spec_123", sample_spec)

        # Assert
        job = document_service.job_manager.get_status(job_id)
        assert job.status == "failed"
        assert job.error == "Test error"

    @patch("vividoc.entrypoint.services.document_service.ExecutorWithProgress")
    def test_execute_generation_calls_evaluator(
        self, mock_executor_class, document_service, sample_spec
    ):
        """Test that _execute_generation calls the evaluator."""
        # Setup mock executor
        mock_executor = Mock()
        mock_generated_doc = Mock(spec=GeneratedDocument)
        mock_generated_doc.html_file_path = "/path/to/doc.html"
        mock_executor.run.return_value = mock_generated_doc
        mock_executor_class.return_value = mock_executor

        # Mock evaluator
        mock_eval_result = Mock(score=0.85, feedback="Well structured")
        document_service.evaluator.evaluate = Mock(return_value=mock_eval_result)

        # Create job
        job_id = document_service.job_manager.create_job("document_generation")

        # Act
        document_service._execute_generation(job_id, "spec_123", sample_spec)

        # Assert - evaluator was called
        document_service.evaluator.evaluate.assert_called_once_with(mock_generated_doc)

        # Assert - evaluation result stored
        job = document_service.job_manager.get_status(job_id)
        doc_id = job.result["document_id"]
        doc_metadata = document_service.documents[doc_id]
        assert "evaluation" in doc_metadata
        assert doc_metadata["evaluation"]["score"] == 0.85
        assert doc_metadata["evaluation"]["feedback"] == "Well structured"

    @patch("vividoc.entrypoint.services.document_service.ExecutorWithProgress")
    def test_execute_generation_handles_evaluator_errors(
        self, mock_executor_class, document_service, sample_spec
    ):
        """Test that _execute_generation handles evaluator errors gracefully."""
        # Setup mock executor
        mock_executor = Mock()
        mock_generated_doc = Mock(spec=GeneratedDocument)
        mock_generated_doc.html_file_path = "/path/to/doc.html"
        mock_executor.run.return_value = mock_generated_doc
        mock_executor_class.return_value = mock_executor

        # Mock evaluator to raise exception
        document_service.evaluator.evaluate = Mock(
            side_effect=Exception("Evaluation failed")
        )

        # Create job
        job_id = document_service.job_manager.create_job("document_generation")

        # Act
        document_service._execute_generation(job_id, "spec_123", sample_spec)

        # Assert - job should still complete (evaluation error doesn't fail the job)
        job = document_service.job_manager.get_status(job_id)
        assert job.status == "completed"

        # Assert - evaluation error stored
        doc_id = job.result["document_id"]
        doc_metadata = document_service.documents[doc_id]
        assert "evaluation" in doc_metadata
        assert "error" in doc_metadata["evaluation"]
        assert doc_metadata["evaluation"]["error"] == "Evaluation failed"


class TestDocumentServiceProgressCallback:
    """Tests for _progress_callback method."""

    def test_progress_callback_updates_ku_status(self, document_service):
        """Test that _progress_callback updates KU status."""
        # Setup
        job_id = document_service.job_manager.create_job("document_generation")
        ku_progress_list = [
            KUProgress(ku_id="ku1", title="KU 1", status="pending"),
            KUProgress(ku_id="ku2", title="KU 2", status="pending"),
        ]

        # Act
        document_service._progress_callback(
            job_id, "executing", "ku1", "stage1", ku_progress_list
        )

        # Assert
        assert ku_progress_list[0].status == "stage1"
        assert ku_progress_list[1].status == "pending"

    def test_progress_callback_calculates_overall_progress(self, document_service):
        """Test that _progress_callback calculates overall progress correctly."""
        # Setup
        job_id = document_service.job_manager.create_job("document_generation")
        ku_progress_list = [
            KUProgress(ku_id="ku1", title="KU 1", status="completed"),
            KUProgress(ku_id="ku2", title="KU 2", status="stage2"),
            KUProgress(ku_id="ku3", title="KU 3", status="stage1"),
            KUProgress(ku_id="ku4", title="KU 4", status="pending"),
        ]

        # Act
        document_service._progress_callback(
            job_id, "executing", "ku2", "stage2", ku_progress_list
        )

        # Assert
        job = document_service.job_manager.get_status(job_id)
        # Progress calculation: (1 completed + 0.75 stage2 + 0.25 stage1 + 0 pending) / 4 * 100
        # = (1 + 0.75 + 0.25 + 0) / 4 * 100 = 2 / 4 * 100 = 50.0
        assert job.progress.overall_percent == 50.0

    def test_progress_callback_updates_job_manager(self, document_service):
        """Test that _progress_callback updates JobManager with progress info."""
        # Setup
        job_id = document_service.job_manager.create_job("document_generation")
        ku_progress_list = [
            KUProgress(ku_id="ku1", title="KU 1", status="pending"),
            KUProgress(ku_id="ku2", title="KU 2", status="pending"),
        ]

        # Act
        document_service._progress_callback(
            job_id, "executing", "ku1", "stage1", ku_progress_list
        )

        # Assert
        job = document_service.job_manager.get_status(job_id)
        assert job.progress.phase == "executing"
        assert job.progress.current_ku == "ku1"
        assert job.progress.ku_stage == "stage1"
        assert job.progress.ku_progress == ku_progress_list

    def test_progress_callback_handles_completed_stage(self, document_service):
        """Test that _progress_callback handles 'completed' stage."""
        # Setup
        job_id = document_service.job_manager.create_job("document_generation")
        ku_progress_list = [
            KUProgress(ku_id="ku1", title="KU 1", status="stage2"),
            KUProgress(ku_id="ku2", title="KU 2", status="pending"),
        ]

        # Act
        document_service._progress_callback(
            job_id, "executing", "ku1", "completed", ku_progress_list
        )

        # Assert
        assert ku_progress_list[0].status == "completed"
        job = document_service.job_manager.get_status(job_id)
        # Progress: (1 completed + 0 pending) / 2 * 100 = 50.0
        assert job.progress.overall_percent == 50.0

    def test_progress_callback_handles_no_ku_id(self, document_service):
        """Test that _progress_callback handles None ku_id."""
        # Setup
        job_id = document_service.job_manager.create_job("document_generation")
        ku_progress_list = [KUProgress(ku_id="ku1", title="KU 1", status="pending")]

        # Act - should not raise exception
        document_service._progress_callback(
            job_id, "executing", None, None, ku_progress_list
        )

        # Assert
        job = document_service.job_manager.get_status(job_id)
        assert job.progress.phase == "executing"
        assert job.progress.current_ku is None
        assert job.progress.ku_stage is None

    def test_progress_callback_calculates_progress_with_all_completed(
        self, document_service
    ):
        """Test progress calculation when all KUs are completed."""
        # Setup
        job_id = document_service.job_manager.create_job("document_generation")
        ku_progress_list = [
            KUProgress(ku_id="ku1", title="KU 1", status="completed"),
            KUProgress(ku_id="ku2", title="KU 2", status="completed"),
        ]

        # Act
        document_service._progress_callback(
            job_id, "executing", "ku2", "completed", ku_progress_list
        )

        # Assert
        job = document_service.job_manager.get_status(job_id)
        assert job.progress.overall_percent == 100.0

    def test_progress_callback_calculates_progress_with_empty_list(
        self, document_service
    ):
        """Test progress calculation with empty KU list."""
        # Setup
        job_id = document_service.job_manager.create_job("document_generation")
        ku_progress_list = []

        # Act
        document_service._progress_callback(
            job_id, "executing", None, None, ku_progress_list
        )

        # Assert
        job = document_service.job_manager.get_status(job_id)
        assert job.progress.overall_percent == 0.0


class TestDocumentServiceGetDocument:
    """Tests for get_document method."""

    def test_get_document_returns_metadata(self, document_service):
        """Test that get_document returns document metadata."""
        # Setup
        doc_id = "doc_123"
        document_service.documents[doc_id] = {
            "document_id": doc_id,
            "created_at": "2024-01-01T00:00:00",
            "spec_id": "spec_123",
            "html_file_path": "/path/to/doc.html",
        }

        # Act
        metadata = document_service.get_document(doc_id)

        # Assert
        assert metadata["document_id"] == doc_id
        assert metadata["spec_id"] == "spec_123"
        assert metadata["html_file_path"] == "/path/to/doc.html"
        assert "created_at" in metadata

    def test_get_document_raises_keyerror_for_invalid_id(self, document_service):
        """Test that get_document raises KeyError for non-existent document."""
        # Act & Assert
        with pytest.raises(KeyError, match="Document not found"):
            document_service.get_document("invalid_id")


class TestDocumentServiceGetHtml:
    """Tests for get_html method."""

    def test_get_html_returns_content(self, document_service, tmp_path):
        """Test that get_html returns HTML content."""
        # Setup
        html_file = tmp_path / "test.html"
        html_content = "<html><body>Test content</body></html>"
        html_file.write_text(html_content, encoding="utf-8")

        doc_id = "doc_123"
        document_service.documents[doc_id] = {
            "document_id": doc_id,
            "html_file_path": str(html_file),
        }

        # Act
        result = document_service.get_html(doc_id)

        # Assert
        assert result == html_content

    def test_get_html_raises_keyerror_for_invalid_id(self, document_service):
        """Test that get_html raises KeyError for non-existent document."""
        # Act & Assert
        with pytest.raises(KeyError, match="Document not found"):
            document_service.get_html("invalid_id")

    def test_get_html_handles_file_read_errors(self, document_service):
        """Test that get_html propagates file read errors."""
        # Setup
        doc_id = "doc_123"
        document_service.documents[doc_id] = {
            "document_id": doc_id,
            "html_file_path": "/nonexistent/path/doc.html",
        }

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            document_service.get_html(doc_id)


class TestDocumentServiceIntegration:
    """Integration tests for DocumentService."""

    @patch("vividoc.entrypoint.services.document_service.ExecutorWithProgress")
    def test_full_document_generation_workflow(
        self, mock_executor_class, document_service, sample_spec, tmp_path
    ):
        """Test complete document generation workflow."""
        # Setup
        html_file = tmp_path / "document.html"
        html_content = "<html><body>Generated content</body></html>"
        html_file.write_text(html_content, encoding="utf-8")

        mock_executor = Mock()
        mock_generated_doc = Mock(spec=GeneratedDocument)
        mock_generated_doc.html_file_path = str(html_file)
        mock_executor.run.return_value = mock_generated_doc
        mock_executor_class.return_value = mock_executor

        # Mock evaluator
        document_service.evaluator.evaluate = Mock(
            return_value=Mock(score=0.9, feedback="Good")
        )

        # Act - Start generation
        job_id = document_service.generate_document("spec_123", sample_spec)

        # Wait for background task to complete (in real scenario, this would be async)
        import time

        time.sleep(0.1)

        # Assert - Check job status
        job = document_service.job_manager.get_status(job_id)
        assert job is not None
        assert job.status == "completed"
        assert "document_id" in job.result

        # Assert - Check document was stored
        doc_id = job.result["document_id"]
        metadata = document_service.get_document(doc_id)
        assert metadata["spec_id"] == "spec_123"

        # Assert - Check HTML can be retrieved
        html = document_service.get_html(doc_id)
        assert html == html_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
