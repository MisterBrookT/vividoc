"""Video generation pipeline: DocumentSpec → Manim Python script → MP4.

Usage
-----
    from vividoc.core.video_codegen import VideoCodegen
    from vividoc.utils.llm.client import LLMClient

    client = LLMClient("openrouter/google/gemini-2.5-pro")
    codegen = VideoCodegen(llm_client=client)
    main_py = codegen.generate(doc_spec, output_dir=Path("outputs/my_topic"))
    # main_py -> Path("outputs/my_topic/video/main.py")
"""

from __future__ import annotations

import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Optional

from vividoc.core.models import DocumentSpec, KnowledgeUnitSpec
from vividoc.utils.llm.client import LLMClient
from vividoc.utils.logger import logger
from prompts.video_prompt import get_video_scene_prompt


# ---------------------------------------------------------------------------
# Boilerplate header prepended to every generated main.py
# ---------------------------------------------------------------------------
_MANIM_HEADER = textwrap.dedent(
    """\
    \"\"\"Auto-generated Manim script produced by ViviDoc video pipeline.

    Render with:
        manim render main.py --quality medium -a
        # -a renders all scenes; omit to render a specific scene class

    Requirements:
        pip install manim>=0.18.0
    \"\"\"
    from manim import *
    import numpy as np

    """
)


class VideoCodegen:
    """Generates a multi-scene Manim Python script from a DocumentSpec.

    Parameters
    ----------
    llm_client:
        Configured :class:`~vividoc.utils.llm.client.LLMClient` instance.
    style_instructions:
        Optional free-text style guidance injected into each scene prompt.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        style_instructions: str = "",
    ) -> None:
        self.llm_client = llm_client
        self.style_instructions = style_instructions

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        spec: DocumentSpec,
        output_dir: Path,
        *,
        render: bool = False,
        render_quality: str = "medium",
    ) -> Path:
        """Generate a Manim ``main.py`` from *spec* and write it to *output_dir*.

        Parameters
        ----------
        spec:
            The :class:`~vividoc.core.models.DocumentSpec` produced by the Planner.
        output_dir:
            Directory where ``video/main.py`` (and rendered output) will be written.
        render:
            If *True* and ``manim`` is found on PATH, render the script immediately.
        render_quality:
            Manim quality flag: ``"low"``, ``"medium"``, ``"high"``, ``"production"``.
            Only used when *render=True*.

        Returns
        -------
        Path
            Absolute path to the generated ``main.py``.
        """
        video_dir = Path(output_dir) / "video"
        video_dir.mkdir(parents=True, exist_ok=True)

        scene_blocks = []
        scene_class_names = []

        for ku in spec.knowledge_units:
            logger.info(f"Generating Manim scene for knowledge unit: {ku.id}")
            code_block = self._generate_scene(spec.topic, ku)
            scene_blocks.append(code_block)

            # Extract the class name so we can build a summary comment at the top
            class_name = self._extract_class_name(code_block, ku.id)
            scene_class_names.append(class_name)

        main_py = self._assemble(
            topic=spec.topic,
            scene_blocks=scene_blocks,
            scene_class_names=scene_class_names,
            output_file=video_dir / "main.py",
        )

        logger.info(f"Manim script written to: {main_py}")

        if render:
            self._render(main_py, render_quality)

        return main_py

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _generate_scene(
        self,
        topic: str,
        ku: KnowledgeUnitSpec,
    ) -> str:
        """Call LLM and return the Manim Scene class source code for *ku*."""
        prompt = get_video_scene_prompt(
            topic=topic,
            unit_id=ku.id,
            unit_content=ku.unit_content,
            text_description=ku.text_description,
            interaction_spec=ku.interaction_spec,
        )
        raw = self.llm_client.call_text_generation(prompt)
        # Strip any residual markdown code fences the LLM might emit
        code = self._strip_code_fences(raw)
        # Validate that we got at least one class definition
        if "class Scene_" not in code and "class " not in code:
            logger.warning(
                f"LLM output for unit '{ku.id}' does not contain a class definition; "
                "using fallback placeholder scene."
            )
            code = self._fallback_scene(ku)
        return code

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        """Remove ```python / ``` wrappers if present."""
        text = text.strip()
        # Remove opening fence
        text = re.sub(r"^```(?:python)?\s*\n?", "", text)
        # Remove closing fence
        text = re.sub(r"\n?```\s*$", "", text)
        return text.strip()

    @staticmethod
    def _extract_class_name(code: str, fallback_id: str) -> str:
        """Return the first ``class Foo(Scene):`` name found in *code*."""
        match = re.search(r"class\s+(\w+)\s*\(", code)
        if match:
            return match.group(1)
        # Fallback: sanitize the unit id
        return "Scene_" + re.sub(r"[^a-zA-Z0-9]", "_", fallback_id)

    @staticmethod
    def _fallback_scene(ku: KnowledgeUnitSpec) -> str:
        """Return a minimal placeholder Scene when LLM generation fails."""
        class_name = "Scene_" + re.sub(r"[^a-zA-Z0-9]", "_", ku.id)
        title_escaped = ku.unit_content.replace('"', '\\"')
        return textwrap.dedent(
            f"""\
            class {class_name}(Scene):
                \"\"\"Placeholder scene for: {title_escaped}\"\"\"

                def construct(self):
                    title = Text({repr(ku.unit_content)}, font_size=36)
                    self.play(Write(title))
                    self.wait(2)
                    subtitle = Text({repr(ku.unit_content)}, font_size=24, color=GREY)
                    subtitle.next_to(title, DOWN)
                    self.play(FadeIn(subtitle))
                    self.wait(3)
            """
        )

    @staticmethod
    def _assemble(
        topic: str,
        scene_blocks: list[str],
        scene_class_names: list[str],
        output_file: Path,
    ) -> Path:
        """Assemble all scene blocks into a single main.py and write it."""
        scene_list_comment = "# Scenes in this file:\n" + "\n".join(
            f"#   {name}" for name in scene_class_names
        )
        separator = "\n\n# " + "-" * 76 + "\n\n"
        body = separator.join(scene_blocks)

        content = _MANIM_HEADER + scene_list_comment + "\n\n" + body + "\n"
        output_file.write_text(content, encoding="utf-8")
        return output_file

    @staticmethod
    def _render(
        main_py: Path,
        quality: str = "medium",
    ) -> Optional[int]:
        """Render *main_py* using the ``manim`` CLI.

        Returns the subprocess return code, or ``None`` if manim is not found.
        """
        manim_bin = _find_manim()
        if manim_bin is None:
            logger.error(
                "manim not found on PATH. "
                "Install with: pip install manim>=0.18.0  (or: uv add manim)"
            )
            return None

        quality_flag = {
            "low": "-ql",
            "medium": "-qm",
            "high": "-qh",
            "production": "-qp",
        }.get(quality, "-qm")

        cmd = [manim_bin, "render", str(main_py), quality_flag, "-a"]
        logger.info(f"Rendering: {' '.join(cmd)}")

        result = subprocess.run(cmd, cwd=str(main_py.parent))
        if result.returncode != 0:
            logger.error(f"Manim render failed with exit code {result.returncode}")
        else:
            logger.info("Manim render completed successfully.")
        return result.returncode


# ---------------------------------------------------------------------------
# Helper: locate manim binary
# ---------------------------------------------------------------------------


def _find_manim() -> Optional[str]:
    """Return the path to the ``manim`` executable, or None if not installed."""
    import shutil

    # Check shutil first (respects PATH and virtual envs)
    path = shutil.which("manim")
    if path:
        return path

    # Try the current Python environment's Scripts / bin directory
    candidate = Path(sys.executable).parent / "manim"
    if candidate.exists():
        return str(candidate)

    return None


def manim_is_available() -> bool:
    """Return True if manim is installed and importable."""
    return _find_manim() is not None
