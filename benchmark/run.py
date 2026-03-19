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

    # Multiple models
    uv run python benchmark/run.py --model openrouter/google/gemini-3-flash-preview --model openrouter/mistralai/mistral-small-2603

    # Parallel topics (default 5)
    uv run python benchmark/run.py --num 20 --parallel 10
"""

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BENCHMARK_DIR = Path(__file__).parent
CODEBASE_DIR = BENCHMARK_DIR.parent
TOPICS_FILE = BENCHMARK_DIR / "datasets" / "prepped" / "topics.jsonl"

DEFAULT_MODELS = ["openrouter/google/gemini-3-flash-preview"]


def _model_suffix(model: str) -> str:
    """Extract short model name for method suffix."""
    name = model.split("/")[-1]
    name = re.sub(r"-(preview|latest)$", "", name)
    return name


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


def _build_gen_cmd(only: str | None, model: str, force: bool, topic: str) -> list[str]:
    cmd = [
        sys.executable,
        str(BENCHMARK_DIR / "baselines" / "run_all.py"),
        "--model",
        model,
    ]
    if only:
        cmd += ["--only", only]
    if force:
        cmd += ["--force"]
    cmd.append(topic)
    return cmd


def run_generate(
    topics: list[str],
    only: str | None = None,
    models: list[str] | None = None,
    force: bool = False,
    parallel: int = 5,
):
    """Run baselines/run_all.py for each topic × model, parallel by topic."""
    models = models or DEFAULT_MODELS

    tasks = [(t, m) for t in topics for m in models]
    total = len(tasks)
    print(
        f"Generating: {len(topics)} topics × {len(models)} model(s) = {total} tasks, parallel={parallel}"
    )

    def _run_one(topic, model):
        cmd = _build_gen_cmd(only, model, force, topic)
        subprocess.run(cmd, cwd=str(CODEBASE_DIR))

    if parallel <= 1:
        for i, (topic, model) in enumerate(tasks, 1):
            suffix = _model_suffix(model)
            print(f"\n({'#' * 60})")
            print(f"# ({i}/{total}) {topic} ({suffix})")
            print(f"{'#' * 60}")
            _run_one(topic, model)
    else:
        with ThreadPoolExecutor(max_workers=parallel) as pool:
            futures = {
                pool.submit(_run_one, topic, model): (topic, model)
                for topic, model in tasks
            }
            for future in as_completed(futures):
                future.result()  # propagate exceptions

    print(f"\nGeneration complete: {total} tasks")


def run_eval(
    only: str | None = None,
    judge_model: str = "openrouter/google/gemini-3.1-pro-preview",
    force: bool = False,
    parallel: int = 5,
):
    """Run evals/run_eval.py on all outputs."""
    cmd = [
        "uv",
        "run",
        "python",
        str(BENCHMARK_DIR / "evals" / "run_eval.py"),
        "--judge-model",
        judge_model,
        "--parallel",
        str(parallel),
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
        "--model",
        action="append",
        dest="models",
        help="LLM model(s) for generation (repeatable). Default: gemini-3-flash-preview",
    )
    parser.add_argument(
        "--judge-model", default="openrouter/google/gemini-3.1-pro-preview"
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel workers (default: 5)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-generate and re-evaluate (no skipping)",
    )
    args = parser.parse_args()

    models = args.models or DEFAULT_MODELS

    # Collect topics
    if args.topic:
        topics = [args.topic]
    else:
        topics = load_topics(Path(args.topics_file), args.num)

    model_names = ", ".join(_model_suffix(m) for m in models)
    print(
        f"Benchmark: mode={args.mode}, topics={len(topics)}, "
        f"methods={args.only or 'all'}, models=[{model_names}], parallel={args.parallel}"
    )

    if args.mode in ("generate", "all"):
        run_generate(topics, args.only, models, args.force, args.parallel)

    if args.mode in ("eval", "all"):
        if args.mode == "all" and args.only:
            # Translate baseline names to full method names with model suffix
            # for each model
            parts = []
            for model in models:
                suffix = _model_suffix(model)
                for b in args.only.split(","):
                    parts.append(f"{b.strip()}_{suffix}")
            eval_only = ",".join(parts)
        elif args.mode == "eval":
            eval_only = args.only
        else:
            eval_only = None
        run_eval(eval_only, args.judge_model, args.force, args.parallel)


if __name__ == "__main__":
    main()
