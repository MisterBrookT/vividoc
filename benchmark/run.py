"""Unified benchmark runner: generate + evaluate.

Usage (from codebase/):
    # Generate + evaluate all methods on first 5 topics
    uv run python benchmark/run.py --num 5

    # Generate only
    uv run python benchmark/run.py --num 5 --mode generate

    # Evaluate only (on existing outputs)
    uv run python benchmark/run.py --mode eval

    # Single topic, specific methods
    uv run python benchmark/run.py --topic "what is pi" --only vividoc,naive_agent

    # Custom topics file
    uv run python benchmark/run.py --topics-file benchmark/datasets/prepped/topics.jsonl --num 3
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

BENCHMARK_DIR = Path(__file__).parent
CODEBASE_DIR = BENCHMARK_DIR.parent
TOPICS_FILE = BENCHMARK_DIR / "datasets" / "prepped" / "topics.jsonl"


def load_topics(topics_file: Path, num: int | None = None) -> list[str]:
    topics = []
    with open(topics_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                topics.append(data["topic"])
    if num:
        topics = topics[:num]
    return topics


def run_generate(topics: list[str], only: str | None = None, force: bool = False):
    """Run baselines/run_all.py for each topic."""
    cmd = [
        sys.executable,
        str(BENCHMARK_DIR / "baselines" / "run_all.py"),
    ]
    if only:
        cmd += ["--only", only]
    if force:
        cmd += ["--force"]

    for topic in topics:
        print(f"\n{'#' * 60}")
        print(f"# Generating: {topic}")
        print(f"{'#' * 60}")
        subprocess.run(cmd + [topic], cwd=str(CODEBASE_DIR))


def run_eval(
    only: str | None = None,
    judge_model: str = "openrouter/google/gemini-3-flash-preview",
    force: bool = False,
):
    """Run evals/run_eval.py on all outputs."""
    cmd = [
        "uv",
        "run",
        "python",
        str(BENCHMARK_DIR / "evals" / "run_eval.py"),
        "--judge-model",
        judge_model,
    ]
    if only:
        for method in only.split(","):
            cmd += ["--method", method.strip()]
    if force:
        cmd += ["--force"]

    print(f"\n{'#' * 60}")
    print("# Running evaluation")
    print(f"{'#' * 60}")
    subprocess.run(cmd, cwd=str(CODEBASE_DIR))


def main():
    parser = argparse.ArgumentParser(description="ViviDoc Benchmark")
    parser.add_argument(
        "--mode",
        choices=["generate", "eval", "all"],
        default="all",
        help="generate, eval, or all (default: all)",
    )
    parser.add_argument("--topic", help="Single topic to run")
    parser.add_argument(
        "--topics-file", default=str(TOPICS_FILE), help="JSONL file with topics"
    )
    parser.add_argument("--num", type=int, help="Only run first N topics")
    parser.add_argument(
        "--only", help="Comma-separated methods (e.g. vividoc,naive_agent)"
    )
    parser.add_argument(
        "--judge-model", default="openrouter/google/gemini-3-flash-preview"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-generate and re-evaluate (no skipping)",
    )
    args = parser.parse_args()

    # Collect topics
    if args.topic:
        topics = [args.topic]
    else:
        topics = load_topics(Path(args.topics_file), args.num)

    print(
        f"Benchmark: mode={args.mode}, topics={len(topics)}, methods={args.only or 'all'}"
    )

    if args.mode in ("generate", "all"):
        run_generate(topics, args.only, args.force)

    if args.mode in ("eval", "all"):
        run_eval(args.only, args.judge_model, args.force)


if __name__ == "__main__":
    main()
