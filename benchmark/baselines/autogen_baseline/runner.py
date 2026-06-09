"""AutoGen (AG2) baseline: 3-agent GroupChat (Planner → Coder → Evaluator).

Usage:
    cd baselines/autogen_baseline
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

# Add baselines root for shared_prompts
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared_prompts import (
    CODER_SYSTEM,
    EVALUATOR_SYSTEM,
    PLANNER_SYSTEM,
    TASK_TEMPLATE,
)

BASELINE_NAME = "autogen"
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
    """Extract HTML from agent output."""
    m = re.search(r"(<!DOCTYPE html>.*?</html>)", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"(<html.*?</html>)", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1)
    return text


def run(topic: str, model: str, output_dir: str, force: bool = False) -> dict:
    from autogen import ConversableAgent, GroupChat, GroupChatManager, LLMConfig

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

    llm_config = LLMConfig(
        {
            "model": api_model,
            "api_key": os.environ.get("OPENROUTER_API_KEY", ""),
            "base_url": "https://openrouter.ai/api/v1",
        },
        temperature=0.0,
    )

    planner = ConversableAgent(
        name="Planner",
        system_message=PLANNER_SYSTEM,
        llm_config=llm_config,
    )
    coder = ConversableAgent(
        name="Coder",
        system_message=CODER_SYSTEM,
        llm_config=llm_config,
    )
    evaluator = ConversableAgent(
        name="Evaluator",
        system_message=EVALUATOR_SYSTEM,
        llm_config=llm_config,
    )

    group_chat = GroupChat(
        agents=[planner, coder, evaluator],
        messages=[],
        max_round=4,
        speaker_selection_method="round_robin",
    )

    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config=llm_config,
    )

    task = TASK_TEMPLATE.format(topic=topic)
    planner.initiate_chat(manager, message=task)

    # Extract final HTML from the last message containing HTML
    html = ""
    for msg in reversed(group_chat.messages):
        content = msg.get("content", "")
        if content and ("<!DOCTYPE" in content or "<html" in content):
            html = extract_html(content)
            break

    if not html:
        # Fallback: use last message
        html = group_chat.messages[-1].get("content", "") if group_chat.messages else ""

    html_path.write_text(html, encoding="utf-8")

    elapsed = time.time() - t0
    meta = {
        "topic": topic,
        "model": model,
        "baseline": BASELINE_NAME,
        "elapsed_sec": round(elapsed, 2),
        "html_length": len(html),
        "num_rounds": len(group_chat.messages),
        "timestamp": datetime.now().isoformat(),
    }
    (out / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"[{BASELINE_NAME}] Done {elapsed:.1f}s ({len(html)} chars)")
    return {**meta, "status": "ok"}


def main():
    parser = argparse.ArgumentParser(description="AutoGen baseline")
    parser.add_argument("topic", help="Topic for the document")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", default="../../outputs")
    parser.add_argument("--force", action="store_true", help="Force re-generate")
    args = parser.parse_args()

    result = run(args.topic, args.model, args.output_dir, args.force)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
