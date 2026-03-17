"""MetaGPT baseline: SOP pipeline with custom Roles (Planner → Coder → Evaluator).

Usage:
    cd baselines/metagpt_baseline
    uv sync
    uv run python runner.py "Fourier Transform"
"""

import os
import re
import sys
import json
import time
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared_prompts import (
    PLANNER_SYSTEM,
    CODER_SYSTEM,
    EVALUATOR_SYSTEM,
    TASK_TEMPLATE,
)

BASELINE_NAME = "metagpt"
DEFAULT_MODEL = "google/gemini-3-flash-preview"


def topic_to_dirname(topic: str) -> str:
    name = topic.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_]+", "_", name)
    return name[:120]


def extract_html(text: str) -> str:
    """Extract the last (best) HTML block from text."""
    # findall returns all matches; take the last one (likely from Evaluator)
    matches = re.findall(
        r"(<!DOCTYPE html>.*?</html>)", text, re.DOTALL | re.IGNORECASE
    )
    if matches:
        return matches[-1]
    matches = re.findall(r"(<html.*?</html>)", text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[-1]
    return text


def _write_config(model: str):
    """Write config/config2.yaml with actual API key before MetaGPT import."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable is not set")

    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(exist_ok=True)
    config_path = config_dir / "config2.yaml"
    config_path.write_text(
        f"""\
llm:
  api_type: 'openai'
  base_url: 'https://openrouter.ai/api/v1'
  model: '{model}'
  api_key: '{api_key}'
""",
        encoding="utf-8",
    )


async def run_async(
    topic: str, model: str, output_dir: str, force: bool = False
) -> dict:
    # Write config BEFORE any metagpt import — MetaGPT loads config at import time
    _write_config(model)

    from metagpt.actions import Action
    from metagpt.roles import Role
    from metagpt.team import Team
    from metagpt.schema import Message

    # --- Action definitions ---

    class PlanDocument(Action):
        name: str = "PlanDocument"

        async def run(self, instruction: str) -> str:
            prompt = f"{PLANNER_SYSTEM}\n\nTopic: {instruction}"
            return await self._aask(prompt)

    class WriteDocument(Action):
        name: str = "WriteDocument"

        async def run(self, plan: str) -> str:
            prompt = (
                f"{CODER_SYSTEM}\n\n"
                f"Here is the plan:\n{plan}\n\n"
                f"Generate the complete HTML document."
            )
            return await self._aask(prompt)

    class ReviewDocument(Action):
        name: str = "ReviewDocument"

        async def run(self, html: str) -> str:
            prompt = f"{EVALUATOR_SYSTEM}\n\nHTML document:\n{html}"
            return await self._aask(prompt)

    # --- Role definitions ---

    class Planner(Role):
        name: str = "Planner"
        profile: str = "Educational Content Planner"
        goal: str = "Decompose a topic into structured knowledge units"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.set_actions([PlanDocument])

        async def _act(self) -> Message:
            todo = self.rc.todo
            msg = self.get_memories(k=1)[0]
            result = await todo.run(msg.content)
            return Message(content=result, role=self.profile, cause_by=type(todo))

    class Coder(Role):
        name: str = "Coder"
        profile: str = "Web Developer"
        goal: str = "Generate interactive HTML document from plan"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.set_actions([WriteDocument])
            self._watch([PlanDocument])

        async def _act(self) -> Message:
            todo = self.rc.todo
            msg = self.get_memories(k=1)[0]
            result = await todo.run(msg.content)
            return Message(content=result, role=self.profile, cause_by=type(todo))

    class Evaluator(Role):
        name: str = "Evaluator"
        profile: str = "Quality Reviewer"
        goal: str = "Review and improve the HTML document"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.set_actions([ReviewDocument])
            self._watch([WriteDocument])

        async def _act(self) -> Message:
            todo = self.rc.todo
            msg = self.get_memories(k=1)[0]
            result = await todo.run(msg.content)
            return Message(content=result, role=self.profile, cause_by=type(todo))

    # --- Run pipeline ---

    dirname = topic_to_dirname(topic)
    out = Path(output_dir) / dirname / BASELINE_NAME
    html_path = out / "document.html"

    if not force and html_path.exists():
        print(f"[{BASELINE_NAME}] Skip (exists): {topic[:60]}")
        return {"topic": topic, "status": "skipped"}

    out.mkdir(parents=True, exist_ok=True)
    print(f"[{BASELINE_NAME}] Generating: {topic[:60]}")
    t0 = time.time()

    planner = Planner()
    coder = Coder()
    evaluator = Evaluator()

    team = Team()
    team.hire([planner, coder, evaluator])
    team.run_project(TASK_TEMPLATE.format(topic=topic))
    await team.run(n_round=3)

    # Extract HTML from role memories (prefer Evaluator > Coder)
    html = ""
    for role in [evaluator, coder]:
        for msg in reversed(role.get_memories()):
            content = msg.content if hasattr(msg, "content") else str(msg)
            if "<!DOCTYPE" in content or "<html" in content:
                html = extract_html(content)
                break
        if html:
            break

    html_path.write_text(html, encoding="utf-8")

    elapsed = time.time() - t0
    meta = {
        "topic": topic,
        "model": model,
        "baseline": BASELINE_NAME,
        "elapsed_sec": round(elapsed, 2),
        "html_length": len(html),
        "timestamp": datetime.now().isoformat(),
    }
    (out / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"[{BASELINE_NAME}] Done {elapsed:.1f}s ({len(html)} chars)")
    return {**meta, "status": "ok"}


def run(topic: str, model: str, output_dir: str, force: bool = False) -> dict:
    return asyncio.run(run_async(topic, model, output_dir, force))


def main():
    parser = argparse.ArgumentParser(description="MetaGPT baseline")
    parser.add_argument("topic", help="Topic for the document")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", default="../../outputs")
    parser.add_argument("--force", action="store_true", help="Force re-generate")
    args = parser.parse_args()

    result = run(args.topic, args.model, args.output_dir, args.force)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
