"""Executor extension with progress callback support."""

from typing import Callable, Optional

from vividoc.core.config import RunnerConfig
from vividoc.core.executor import Executor
from vividoc.core.models import DocumentSpec, GeneratedDocument


class ExecutorWithProgress(Executor):
    """
    Extends the existing Executor to support progress callbacks.

    This wrapper adds progress reporting capabilities to the standard Executor,
    allowing the JobManager to track document generation progress in real-time.
    """

    def __init__(
        self,
        config: RunnerConfig,
        progress_callback: Optional[
            Callable[[str, Optional[str], Optional[str]], None]
        ] = None,
        style_config=None,
        text_style_instructions: str = "",
        interaction_style_instructions: str = "",
    ):
        """
        Initialize executor with progress callback support.

        Args:
            config: RunnerConfig for the base Executor
            progress_callback: Optional callback function with signature:
                callback(phase: str, ku_id: Optional[str], stage: Optional[str])
                - phase: "planning" | "executing" | "evaluating"
                - ku_id: Knowledge unit identifier (e.g., "ku1", "ku2")
                - stage: "stage1" | "stage2" | "completed" | None
            style_config: Legacy StyleConfig (ignored if instructions provided)
            text_style_instructions: Style instructions for text generation (stage1)
            interaction_style_instructions: Style instructions for interaction generation (stage2)
        """
        super().__init__(
            config,
            style_config=style_config,
            text_style_instructions=text_style_instructions,
            interaction_style_instructions=interaction_style_instructions,
        )
        self.progress_callback = progress_callback

    def _report_progress(
        self, phase: str, ku_id: Optional[str] = None, stage: Optional[str] = None
    ):
        """
        Report progress via callback if available.

        Args:
            phase: Current phase ("planning" | "executing" | "evaluating")
            ku_id: Knowledge unit identifier (e.g., "ku1", "ku2")
            stage: Current stage ("stage1" | "stage2" | "completed" | None)
        """
        if self.progress_callback:
            self.progress_callback(phase, ku_id, stage)

    def run(self, doc_spec: DocumentSpec) -> GeneratedDocument:
        """
        Execute the iterative HTML generation process with progress reporting.

        This method overrides the base Executor.run() to add progress callbacks
        at key points during document generation.

        Args:
            doc_spec: Document specification to generate from

        Returns:
            GeneratedDocument with HTML file path and metadata
        """
        from pathlib import Path

        from vividoc.utils.html.template import create_document_skeleton
        from vividoc.utils.io import save_json
        from vividoc.utils.logger import logger

        # Report start of execution phase
        self._report_progress("executing", None, None)

        # Setup paths (same as base Executor)
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        html_path = output_dir / "document.html"
        states_dir = output_dir / "states"
        states_dir.mkdir(exist_ok=True)

        # Create HTML skeleton if not resuming or file doesn't exist
        if not self.config.resume or not html_path.exists():
            logger.info("Creating HTML document skeleton...")
            create_document_skeleton(doc_spec, str(html_path))
        else:
            logger.info("Resuming from existing HTML document...")

        # Process each knowledge unit with progress reporting
        knowledge_units = []
        total_units = len(doc_spec.knowledge_units)

        for idx, ku_spec in enumerate(doc_spec.knowledge_units, 1):
            scope_id = f"ku{idx}"
            logger.info(f"[{idx}/{total_units}] Processing {ku_spec.id} ({scope_id})")

            # Report Stage 1 start
            self._report_progress("executing", scope_id, "stage1")

            # Process Stage 1 (text generation)
            stage1_html = self.process_stage1(
                str(html_path), ku_spec, scope_id, doc_spec.topic
            )
            self._save_state(states_dir, scope_id, "stage1", stage1_html)

            # Report Stage 2 start
            self._report_progress("executing", scope_id, "stage2")

            # Process Stage 2 (interactive content)
            final_html = self.process_stage2(
                str(html_path), ku_spec, scope_id, doc_spec.topic
            )
            self._save_state(states_dir, scope_id, "stage2", final_html)

            # Validate
            is_valid, error = self.validate_section(final_html, scope_id)
            if not is_valid:
                logger.warning(f"  Validation warning: {error}")

            # Create KU state
            from vividoc.core.models import KnowledgeUnitState

            ku_state = KnowledgeUnitState(
                id=ku_spec.id,
                unit_content=ku_spec.unit_content,
                stage1_completed=True,
                stage2_completed=True,
                validated=is_valid,
            )
            knowledge_units.append(ku_state)

            # Report KU completion
            self._report_progress("executing", scope_id, "completed")

            logger.info(f"[{idx}/{total_units}] {ku_spec.id} completed ✓")

        # Create result
        result = GeneratedDocument(
            topic=doc_spec.topic,
            html_file_path=str(html_path),
            knowledge_units=knowledge_units,
        )

        # Save metadata
        metadata_path = output_dir / "generated_doc.json"
        save_json(result, str(metadata_path))

        logger.info(f"HTML document saved to {html_path}")

        return result
