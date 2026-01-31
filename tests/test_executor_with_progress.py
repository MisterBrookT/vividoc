"""Unit tests for ExecutorWithProgress."""

from unittest.mock import Mock, MagicMock, patch
from vividoc.entrypoint.services.executor_with_progress import ExecutorWithProgress
from vividoc.core.config import RunnerConfig
from vividoc.core.models import DocumentSpec, KnowledgeUnitSpec


class TestExecutorWithProgress:
    """Test suite for ExecutorWithProgress class."""

    def test_init_with_callback(self):
        """Test initialization with progress callback."""
        config = RunnerConfig()
        callback = Mock()

        executor = ExecutorWithProgress(config, progress_callback=callback)

        assert executor.config == config
        assert executor.progress_callback == callback

    def test_init_without_callback(self):
        """Test initialization without progress callback."""
        config = RunnerConfig()

        executor = ExecutorWithProgress(config)

        assert executor.config == config
        assert executor.progress_callback is None

    def test_report_progress_with_callback(self):
        """Test that _report_progress invokes callback when available."""
        config = RunnerConfig()
        callback = Mock()

        executor = ExecutorWithProgress(config, progress_callback=callback)
        executor._report_progress("executing", "ku1", "stage1")

        callback.assert_called_once_with("executing", "ku1", "stage1")

    def test_report_progress_without_callback(self):
        """Test that _report_progress doesn't fail when callback is None."""
        config = RunnerConfig()

        executor = ExecutorWithProgress(config)
        # Should not raise an exception
        executor._report_progress("executing", "ku1", "stage1")

    @patch("vividoc.utils.html.template.create_document_skeleton")
    @patch("vividoc.utils.io.save_json")
    @patch("pathlib.Path")
    def test_run_invokes_callback_at_key_points(
        self, mock_path, mock_save_json, mock_create_skeleton
    ):
        """Test that run() invokes progress callback at key points."""
        # Setup
        config = RunnerConfig(output_dir="test_output")
        callback = Mock()

        # Create a simple spec with one KU
        ku = KnowledgeUnitSpec(
            id="test_ku",
            unit_content="Test content",
            text_description="Test text",
            interaction_description="Test interaction",
        )
        spec = DocumentSpec(topic="Test Topic", knowledge_units=[ku])

        # Mock the Path operations
        mock_output_dir = MagicMock()
        mock_html_path = MagicMock()
        mock_states_dir = MagicMock()
        mock_metadata_path = MagicMock()

        mock_path.return_value = mock_output_dir
        # Need 3 calls: document.html, states, generated_doc.json
        mock_output_dir.__truediv__ = Mock(
            side_effect=[mock_html_path, mock_states_dir, mock_metadata_path]
        )
        mock_html_path.exists.return_value = False

        executor = ExecutorWithProgress(config, progress_callback=callback)

        # Mock the processing methods
        executor.process_stage1 = Mock(return_value="<html>stage1</html>")
        executor.process_stage2 = Mock(return_value="<html>stage2</html>")
        executor.validate_section = Mock(return_value=(True, ""))
        executor._save_state = Mock()

        # Execute
        _ = executor.run(spec)

        # Verify callback was invoked at key points
        # Should be called: start, stage1, stage2, completed
        assert callback.call_count >= 4

        # Verify the sequence of calls
        calls = callback.call_args_list

        # First call: start of execution
        assert calls[0][0] == ("executing", None, None)

        # Second call: stage1 for ku1
        assert calls[1][0] == ("executing", "ku1", "stage1")

        # Third call: stage2 for ku1
        assert calls[2][0] == ("executing", "ku1", "stage2")

        # Fourth call: completed for ku1
        assert calls[3][0] == ("executing", "ku1", "completed")

    @patch("vividoc.utils.html.template.create_document_skeleton")
    @patch("vividoc.utils.io.save_json")
    @patch("pathlib.Path")
    def test_run_reports_progress_for_multiple_kus(
        self, mock_path, mock_save_json, mock_create_skeleton
    ):
        """Test that run() reports progress for each KU."""
        # Setup
        config = RunnerConfig(output_dir="test_output")
        callback = Mock()

        # Create a spec with multiple KUs
        ku1 = KnowledgeUnitSpec(
            id="test_ku1",
            unit_content="Test content 1",
            text_description="Test text 1",
            interaction_description="Test interaction 1",
        )
        ku2 = KnowledgeUnitSpec(
            id="test_ku2",
            unit_content="Test content 2",
            text_description="Test text 2",
            interaction_description="Test interaction 2",
        )
        spec = DocumentSpec(topic="Test Topic", knowledge_units=[ku1, ku2])

        # Mock the Path operations
        mock_output_dir = MagicMock()
        mock_html_path = MagicMock()
        mock_states_dir = MagicMock()
        mock_metadata_path = MagicMock()

        mock_path.return_value = mock_output_dir
        # Need 3 calls: document.html, states, generated_doc.json
        mock_output_dir.__truediv__ = Mock(
            side_effect=[mock_html_path, mock_states_dir, mock_metadata_path]
        )
        mock_html_path.exists.return_value = False

        executor = ExecutorWithProgress(config, progress_callback=callback)

        # Mock the processing methods
        executor.process_stage1 = Mock(return_value="<html>stage1</html>")
        executor.process_stage2 = Mock(return_value="<html>stage2</html>")
        executor.validate_section = Mock(return_value=(True, ""))
        executor._save_state = Mock()

        # Execute
        _ = executor.run(spec)

        # Verify callback was invoked for both KUs
        # Should be called: start, ku1_stage1, ku1_stage2, ku1_completed, ku2_stage1, ku2_stage2, ku2_completed
        assert callback.call_count >= 7

        # Verify calls for ku1
        calls = callback.call_args_list
        assert any(call[0] == ("executing", "ku1", "stage1") for call in calls)
        assert any(call[0] == ("executing", "ku1", "stage2") for call in calls)
        assert any(call[0] == ("executing", "ku1", "completed") for call in calls)

        # Verify calls for ku2
        assert any(call[0] == ("executing", "ku2", "stage1") for call in calls)
        assert any(call[0] == ("executing", "ku2", "stage2") for call in calls)
        assert any(call[0] == ("executing", "ku2", "completed") for call in calls)

    def test_inherits_from_executor(self):
        """Test that ExecutorWithProgress inherits from Executor."""
        from vividoc.core.executor import Executor

        config = RunnerConfig()
        executor = ExecutorWithProgress(config)

        assert isinstance(executor, Executor)

    def test_has_all_executor_methods(self):
        """Test that ExecutorWithProgress has all base Executor methods."""
        config = RunnerConfig()
        executor = ExecutorWithProgress(config)

        # Verify key methods exist
        assert hasattr(executor, "process_stage1")
        assert hasattr(executor, "process_stage2")
        assert hasattr(executor, "validate_section")
        assert hasattr(executor, "process_knowledge_unit")
        assert hasattr(executor, "run")
