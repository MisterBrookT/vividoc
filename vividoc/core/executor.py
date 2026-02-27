"""Executor - Fragment-based HTML generation with context awareness."""

import json
from pathlib import Path
from bs4 import BeautifulSoup
from vividoc.utils.llm.client import LLMClient
from vividoc.core.models import DocumentSpec, GeneratedDocument, KnowledgeUnitState
from vividoc.core.config import RunnerConfig
from vividoc.utils.html.validator import HTMLValidator
from vividoc.utils.html.template import create_document_skeleton
from prompts.executor_prompt import (
    get_fragment_stage1_prompt,
    get_fragment_stage2_prompt,
)


class Executor:
    """Fragment-based executor with context awareness for style consistency."""

    def __init__(self, config: RunnerConfig):
        """Initialize executor with configuration."""
        self.config = config
        self.llm_client = LLMClient(config.llm_model)
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

    def _extract_completed_sections(self, html: str, current_scope_id: str) -> str:
        """Extract all completed sections before the current one for context."""
        soup = BeautifulSoup(html, "html.parser")
        sections = soup.find_all("section")

        completed = []
        for section in sections:
            section_id = section.get("id", "")
            if section_id == current_scope_id:
                break  # Stop at current section

            # Check if section has content
            text_div = section.find("div", class_="text-content")
            if text_div and text_div.get_text(strip=True):
                completed.append(str(section))

        if not completed:
            return "(This is the first section)"

        return "\n\n".join(completed)

    def _clean_fragment(self, fragment: str) -> str:
        """Clean LLM-generated fragment."""
        # Remove markdown code blocks
        if "```html" in fragment:
            fragment = fragment.split("```html")[1].split("```")[0]
        elif "```" in fragment:
            fragment = fragment.split("```")[1].split("```")[0]

        fragment = fragment.strip()

        # Remove outer div if LLM added it
        if fragment.startswith('<div class="text-content">'):
            fragment = fragment[len('<div class="text-content">') : -6]
        elif fragment.startswith('<div class="interactive-content">'):
            fragment = fragment[len('<div class="interactive-content">') : -6]

        return fragment.strip()

    def _insert_into_div(
        self, html: str, scope_id: str, class_name: str, content: str
    ) -> str:
        """Insert content into a specific div using BeautifulSoup."""
        soup = BeautifulSoup(html, "html.parser")

        # Find target section
        section = soup.find("section", id=scope_id)
        if not section:
            raise ValueError(f"Section {scope_id} not found in HTML")

        # Find target div
        target_div = section.find("div", class_=class_name)
        if not target_div:
            raise ValueError(
                f"Div with class '{class_name}' not found in section {scope_id}"
            )

        # Clear and insert new content
        target_div.clear()
        content_soup = BeautifulSoup(content, "html.parser")
        for element in content_soup:
            target_div.append(element)

        return str(soup)

    def process_stage1(self, html_path: str, ku_spec, scope_id: str, topic: str) -> str:
        """Stage 1: Generate and insert text content fragment."""
        from vividoc.utils.logger import logger

        html = self._read_html(html_path)

        # Extract completed sections for context
        completed_sections = self._extract_completed_sections(html, scope_id)

        # Try up to max_fix_attempts times
        for attempt in range(1, self.config.max_fix_attempts + 1):
            logger.info(
                f"  Stage 1: Generating text fragment... (attempt {attempt}/{self.config.max_fix_attempts})"
            )

            # Generate prompt with context
            prompt = get_fragment_stage1_prompt(
                topic=topic,
                completed_sections=completed_sections,
                scope_id=scope_id,
                unit_content=ku_spec.unit_content,
                text_description=ku_spec.text_description,
            )

            # Call LLM to generate fragment
            fragment = self.llm_client.call_text_generation(prompt=prompt)
            fragment = self._clean_fragment(fragment)

            # Validate fragment (basic check)
            if not fragment or len(fragment) < 10:
                logger.warning(
                    f"  ✗ Attempt {attempt}: Fragment too short, retrying..."
                )
                continue

            # Insert fragment into HTML
            try:
                updated_html = self._insert_into_div(
                    html, scope_id, "text-content", fragment
                )
                self._write_html(html_path, updated_html)

                if attempt > 1:
                    logger.info(f"  ✓ Stage 1 succeeded on attempt {attempt}")

                return updated_html

            except Exception as e:
                logger.warning(f"  ✗ Attempt {attempt}: Failed to insert - {e}")
                continue

        # All attempts failed
        logger.error(
            f"  Failed to generate valid fragment after {self.config.max_fix_attempts} attempts"
        )
        return html

    def process_stage2(self, html_path: str, ku_spec, scope_id: str, topic: str) -> str:
        """Stage 2: Generate and insert interactive content fragment."""
        from vividoc.utils.logger import logger

        html = self._read_html(html_path)

        # Extract completed sections (now includes current section's text)
        completed_sections = self._extract_completed_sections(html, scope_id)

        # Also extract current section's text content for reference
        soup = BeautifulSoup(html, "html.parser")
        current_section = soup.find("section", id=scope_id)
        current_text = ""
        if current_section:
            text_div = current_section.find("div", class_="text-content")
            if text_div:
                current_text = str(text_div)

        # Try up to max_fix_attempts times
        for attempt in range(1, self.config.max_fix_attempts + 1):
            logger.info(
                f"  Stage 2: Generating interactive fragment... (attempt {attempt}/{self.config.max_fix_attempts})"
            )

            # Generate prompt with context
            prompt = get_fragment_stage2_prompt(
                topic=topic,
                completed_sections=completed_sections,
                scope_id=scope_id,
                current_text_content=current_text,
                interaction_spec_text=json.dumps(
                    ku_spec.interaction_spec.model_dump(), indent=2
                ),
            )

            # Call LLM to generate fragment
            fragment = self.llm_client.call_text_generation(prompt=prompt)
            fragment = self._clean_fragment(fragment)

            # Validate fragment (basic check)
            if not fragment or len(fragment) < 10:
                logger.warning(
                    f"  ✗ Attempt {attempt}: Fragment too short, retrying..."
                )
                continue

            # Insert fragment into HTML
            try:
                updated_html = self._insert_into_div(
                    html, scope_id, "interactive-content", fragment
                )
                self._write_html(html_path, updated_html)

                if attempt > 1:
                    logger.info(f"  ✓ Stage 2 succeeded on attempt {attempt}")

                return updated_html

            except Exception as e:
                logger.warning(f"  ✗ Attempt {attempt}: Failed to insert - {e}")
                continue

        # All attempts failed
        logger.error(
            f"  Failed to generate valid fragment after {self.config.max_fix_attempts} attempts"
        )
        return html

    def validate_section(self, html_content: str, scope_id: str) -> tuple[bool, str]:
        """Validate a specific section in the HTML."""
        import re

        pattern = f'<section[^>]*id="{scope_id}"[^>]*>.*?</section>'
        match = re.search(pattern, html_content, re.DOTALL)

        if not match:
            return False, f"Section {scope_id} not found in HTML"

        section_html = match.group(0)
        return self.html_validator.validate(section_html)

    def process_knowledge_unit(
        self,
        html_path: str,
        states_dir: Path,
        ku_spec,
        scope_id: str,
        topic: str,
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
                final_html = self.process_stage2(html_path, ku_spec, scope_id, topic)
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

        # Stage 1: Generate text content fragment
        stage1_html = self.process_stage1(html_path, ku_spec, scope_id, topic)
        self._save_state(states_dir, scope_id, "stage1", stage1_html)
        ku_state.stage1_completed = True

        # Stage 2: Generate interactive content fragment
        final_html = self.process_stage2(html_path, ku_spec, scope_id, topic)
        self._save_state(states_dir, scope_id, "stage2", final_html)
        ku_state.stage2_completed = True

        # Validate
        is_valid, error = self.validate_section(final_html, scope_id)
        ku_state.validated = is_valid
        if not is_valid:
            logger.warning(f"  Validation warning: {error}")

        return ku_state

    def run(self, doc_spec: DocumentSpec) -> GeneratedDocument:
        """Execute the fragment-based HTML generation process."""
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
                topic=doc_spec.topic,
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
