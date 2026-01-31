"""Executor workflow for vividoc pipeline - Iterative HTML generation."""

from dataclasses import dataclass
from pathlib import Path
from vividoc.utils.llm.client import LLMClient
from vividoc.models import DocumentSpec, GeneratedDocument, KnowledgeUnitState
from vividoc.utils.html.validator import HTMLValidator
from vividoc.utils.html.template import create_document_skeleton
from prompts.executor_prompt import get_stage1_prompt, get_stage2_prompt


@dataclass
class ExecutorConfig:
    """Configuration for execution phase."""

    llm_provider: str = "openrouter"
    llm_model: str = "google/gemini-2.5-pro"
    max_fix_attempts: int = 3
    output_dir: str = "output"
    resume: bool = False


class Executor:
    """Handles the execution phase with iterative HTML generation."""

    def __init__(self, config: ExecutorConfig):
        """Initialize executor with configuration."""
        self.config = config
        self.llm_client = LLMClient(config.llm_provider)
        self.html_validator = HTMLValidator()

    def _read_html(self, html_path: str) -> str:
        """Read HTML file."""
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()

    def _write_html(self, html_path: str, content: str) -> None:
        """Write HTML file."""
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _save_state(
        self, states_dir: Path, scope_id: str, stage: str, html_content: str
    ) -> None:
        """Save intermediate state."""
        state_file = states_dir / f"{scope_id}_{stage}.html"
        with open(state_file, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _load_state(self, states_dir: Path, scope_id: str, stage: str) -> str:
        """Load intermediate state."""
        state_file = states_dir / f"{scope_id}_{stage}.html"
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def process_stage1(self, html_path: str, ku_spec, scope_id: str) -> str:
        """Stage 1: Fill text content."""
        from vividoc.utils.logger import logger

        # Read current HTML
        current_html = self._read_html(html_path)

        # Try up to max_fix_attempts times
        for attempt in range(1, self.config.max_fix_attempts + 1):
            logger.info(
                f"  Stage 1: Generating text content... (attempt {attempt}/{self.config.max_fix_attempts})"
            )

            # Generate prompt
            prompt = get_stage1_prompt(
                current_html=current_html,
                scope_id=scope_id,
                text_description=ku_spec.text_description,
            )

            # Call LLM
            updated_html = self.llm_client.call_text_generation(
                model=self.config.llm_model, prompt=prompt
            )

            # Clean up markdown code blocks if present
            if "```html" in updated_html:
                updated_html = updated_html.split("```html")[1].split("```")[0].strip()
            elif "```" in updated_html:
                updated_html = updated_html.split("```")[1].split("```")[0].strip()

            # Validate: check if it's a complete HTML document
            if (
                updated_html.strip().startswith("<!DOCTYPE html")
                and "</html>" in updated_html
            ):
                # Write back
                self._write_html(html_path, updated_html)
                if attempt > 1:
                    logger.info(f"  ✓ Stage 1 succeeded on attempt {attempt}")
                return updated_html
            else:
                logger.warning(
                    f"  ✗ Attempt {attempt}/{self.config.max_fix_attempts}: Invalid HTML generated, retrying..."
                )

        # If all attempts failed, log error and return original
        logger.error(
            f"  Failed to generate valid HTML after {self.config.max_fix_attempts} attempts"
        )
        return current_html

    def process_stage2(self, html_path: str, ku_spec, scope_id: str) -> str:
        """Stage 2: Add interactive content."""
        from vividoc.utils.logger import logger

        # Read current HTML (with text content)
        current_html = self._read_html(html_path)

        # Try up to max_fix_attempts times
        for attempt in range(1, self.config.max_fix_attempts + 1):
            logger.info(
                f"  Stage 2: Adding interactive content... (attempt {attempt}/{self.config.max_fix_attempts})"
            )

            # Generate prompt
            prompt = get_stage2_prompt(
                current_html=current_html,
                scope_id=scope_id,
                interaction_description=ku_spec.interaction_description,
            )

            # Call LLM
            final_html = self.llm_client.call_text_generation(
                model=self.config.llm_model, prompt=prompt
            )

            # Clean up markdown code blocks if present
            if "```html" in final_html:
                final_html = final_html.split("```html")[1].split("```")[0].strip()
            elif "```" in final_html:
                final_html = final_html.split("```")[1].split("```")[0].strip()

            # Validate: check if it's a complete HTML document
            if (
                final_html.strip().startswith("<!DOCTYPE html")
                and "</html>" in final_html
            ):
                # Write back
                self._write_html(html_path, final_html)
                if attempt > 1:
                    logger.info(f"  ✓ Stage 2 succeeded on attempt {attempt}")
                return final_html
            else:
                logger.warning(
                    f"  ✗ Attempt {attempt}/{self.config.max_fix_attempts}: Invalid HTML generated, retrying from stage1..."
                )
                # Reload stage1 HTML for retry
                current_html = self._read_html(html_path)

        # If all attempts failed, log error but continue
        logger.error(
            f"  Failed to generate valid HTML after {self.config.max_fix_attempts} attempts"
        )
        # Keep the stage1 HTML
        return current_html

    def validate_section(self, html_content: str, scope_id: str) -> tuple[bool, str]:
        """Validate a specific section in the HTML."""
        # Extract the section
        import re

        pattern = f'<section[^>]*id="{scope_id}"[^>]*>.*?</section>'
        match = re.search(pattern, html_content, re.DOTALL)

        if not match:
            return False, f"Section {scope_id} not found in HTML"

        section_html = match.group(0)
        return self.html_validator.validate(section_html)

    def process_knowledge_unit(
        self, html_path: str, states_dir: Path, ku_spec, scope_id: str
    ) -> KnowledgeUnitState:
        """Process a single knowledge unit through both stages."""
        from vividoc.utils.logger import logger

        ku_state = KnowledgeUnitState(id=ku_spec.id, unit_content=ku_spec.unit_content)

        # Check if we can resume
        if self.config.resume:
            # Check Stage 2 completion
            stage2_html = self._load_state(states_dir, scope_id, "stage2")
            if stage2_html:
                logger.info(f"[{scope_id}] Resuming: Stage 2 already completed")
                self._write_html(html_path, stage2_html)
                ku_state.stage1_completed = True
                ku_state.stage2_completed = True
                ku_state.validated = True
                return ku_state

            # Check Stage 1 completion
            stage1_html = self._load_state(states_dir, scope_id, "stage1")
            if stage1_html:
                logger.info(f"[{scope_id}] Resuming: Starting from Stage 2")
                self._write_html(html_path, stage1_html)
                ku_state.stage1_completed = True

                # Process Stage 2 only
                final_html = self.process_stage2(html_path, ku_spec, scope_id)
                self._save_state(states_dir, scope_id, "stage2", final_html)
                ku_state.stage2_completed = True

                # Validate
                is_valid, error = self.validate_section(final_html, scope_id)
                ku_state.validated = is_valid
                if not is_valid:
                    logger.warning(f"  Validation warning: {error}")

                return ku_state

        # Process from scratch
        logger.info(f"[{scope_id}] Starting from Stage 1")

        # Stage 1
        stage1_html = self.process_stage1(html_path, ku_spec, scope_id)
        self._save_state(states_dir, scope_id, "stage1", stage1_html)
        ku_state.stage1_completed = True

        # Stage 2
        final_html = self.process_stage2(html_path, ku_spec, scope_id)
        self._save_state(states_dir, scope_id, "stage2", final_html)
        ku_state.stage2_completed = True

        # Validate
        is_valid, error = self.validate_section(final_html, scope_id)
        ku_state.validated = is_valid
        if not is_valid:
            logger.warning(f"  Validation warning: {error}")

        return ku_state

    def run(self, doc_spec: DocumentSpec) -> GeneratedDocument:
        """Execute the iterative HTML generation process."""
        from vividoc.utils.logger import logger
        from vividoc.utils.io import save_json

        # Setup paths
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

        # Process each knowledge unit
        knowledge_units = []
        total_units = len(doc_spec.knowledge_units)

        for idx, ku_spec in enumerate(doc_spec.knowledge_units, 1):
            scope_id = f"ku{idx}"
            logger.info(f"[{idx}/{total_units}] Processing {ku_spec.id} ({scope_id})")

            ku_state = self.process_knowledge_unit(
                html_path=str(html_path),
                states_dir=states_dir,
                ku_spec=ku_spec,
                scope_id=scope_id,
            )
            knowledge_units.append(ku_state)

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
