"""CAMEL baseline: RolePlaying (Planner↔Coder) + ChatAgent Evaluator.

Uses CAMEL's native RolePlaying mode — two agents negotiate via dialogue.
After the conversation, an Evaluator ChatAgent reviews the result.

Usage:
    cd baselines/camel_baseline
    uv sync
    uv run python runner.py "Fourier Transform"
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared_prompts import EVALUATOR_SYSTEM, TASK_TEMPLATE

BASELINE_NAME = "camel"
DEFAULT_MODEL = "google/gemini-3-flash-preview"


def topic_to_dirname(topic: str) -> str:
    name = topic.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_]+", "_", name)
    return name[:120]


def _model_suffix(model: str) -> str:
    """Extract short model name for directory suffix."""
    name = model.split("/")[-1]
    name = re.sub(r"-(preview|latest)$", "", name)
    return name


def extract_html(text: str) -> str:
    """Extract the best HTML block from text."""
    m = re.search(r"(<!DOCTYPE html>.*?</html>)", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"(<html.*?</html>)", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1)
    return text


def extract_best_html_from_messages(messages: list[str]) -> str:
    """Find the longest valid HTML block across all messages."""
    best = ""
    for msg in messages:
        if not msg:
            continue
        candidate = extract_html(msg)
        if ("<!DOCTYPE" in candidate or "<html" in candidate) and len(candidate) > len(
            best
        ):
            best = candidate
    return best


def run(topic: str, model: str, output_dir: str, force: bool = False) -> dict:
    from camel.agents import ChatAgent
    from camel.configs import ChatGPTConfig
    from camel.models import ModelFactory
    from camel.societies import RolePlaying
    from camel.types import ModelPlatformType

    # Strip "openrouter/" prefix — OpenRouter API expects e.g. "google/gemini-3-flash-preview"
    api_model = model.removeprefix("openrouter/")

    dirname = topic_to_dirname(topic)
    method_name = f"{BASELINE_NAME}_{_model_suffix(model)}"
    out = Path(output_dir) / dirname / method_name
    html_path = out / "document.html"

    if not force and html_path.exists():
        print(f"[{BASELINE_NAME}] Skip (exists): {topic[:60]}")
        return {"topic": topic, "status": "skipped"}

    out.mkdir(parents=True, exist_ok=True)
    print(f"[{BASELINE_NAME}] Generating: {topic[:60]}")
    t0 = time.time()

    camel_model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
        model_type=api_model,
        url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        model_config_dict=ChatGPTConfig(temperature=0.0).as_dict(),
    )

    task = TASK_TEMPLATE.format(topic=topic)

    # Phase 1: RolePlaying — Planner (user) ↔ Coder (assistant)
    society = RolePlaying(
        task_prompt=task,
        with_task_specify=False,
        user_role_name="Educational Content Planner",
        user_agent_kwargs={"model": camel_model},
        assistant_role_name="Interactive Web Developer",
        assistant_agent_kwargs={"model": camel_model},
    )

    input_msg = society.init_chat()
    all_messages = []
    for round_i in range(6):
        assistant_response, user_response = society.step(input_msg)
        a_content = assistant_response.msg.content or ""
        u_content = user_response.msg.content or ""
        all_messages.append(a_content)
        all_messages.append(u_content)
        print(
            f"  [Round {round_i + 1}] assistant={len(a_content)} chars, user={len(u_content)} chars"
        )
        if assistant_response.terminated or user_response.terminated:
            break
        if "CAMEL_TASK_DONE" in u_content:
            break
        input_msg = assistant_response.msg

    # Extract the longest/best HTML from the conversation
    html = extract_best_html_from_messages(all_messages)

    # Phase 2: Evaluator reviews (only if we got HTML)
    if html and len(html) > 200:
        evaluator = ChatAgent(system_message=EVALUATOR_SYSTEM, model=camel_model)
        eval_response = evaluator.step(f"Review this HTML document:\n\n{html}")
        eval_content = eval_response.msg.content or ""
        if "<!DOCTYPE" in eval_content or "<html" in eval_content:
            corrected = extract_html(eval_content)
            if len(corrected) > len(html) * 0.5:
                html = corrected

    html_path.write_text(html, encoding="utf-8")

    elapsed = time.time() - t0
    meta = {
        "topic": topic,
        "model": model,
        "baseline": BASELINE_NAME,
        "elapsed_sec": round(elapsed, 2),
        "html_length": len(html),
        "num_messages": len(all_messages),
        "timestamp": datetime.now().isoformat(),
    }
    (out / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"[{BASELINE_NAME}] Done {elapsed:.1f}s ({len(html)} chars)")
    return {**meta, "status": "ok"}


def main():
    parser = argparse.ArgumentParser(description="CAMEL baseline")
    parser.add_argument("topic", help="Topic for the document")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", default="../../outputs")
    parser.add_argument("--force", action="store_true", help="Force re-generate")
    args = parser.parse_args()

    result = run(args.topic, args.model, args.output_dir, args.force)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
