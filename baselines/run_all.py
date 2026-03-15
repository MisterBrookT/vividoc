"""Run all baselines for a given topic (or list of topics).

Usage:
    python baselines/run_all.py "Fourier Transform"
    python baselines/run_all.py --topics-file exps/sampled_topics.jsonl
    python baselines/run_all.py "Fourier Transform" --only naive_agent,autogen
"""

import argparse
import json
import subprocess
from pathlib import Path

BASELINES_DIR = Path(__file__).parent

# Each baseline: (name, directory, command template)
# Commands are run via `uv run` in each baseline's own directory.
BASELINES = [
    {
        "name": "vividoc",
        "cwd": BASELINES_DIR.parent,  # codebase/ root (uses vividoc's venv)
        "cmd": ["uv", "run", "python", "baselines/vividoc_wrapper.py"],
    },
    {
        "name": "naive_agent",
        "cwd": BASELINES_DIR.parent,  # codebase/ root (uses vividoc's venv)
        "cmd": ["uv", "run", "python", "-m", "baselines.naive_agent"],
    },
    {
        "name": "autogen",
        "cwd": BASELINES_DIR / "autogen_baseline",
        "cmd": ["uv", "run", "python", "runner.py"],
    },
    {
        "name": "camel",
        "cwd": BASELINES_DIR / "camel_baseline",
        "cmd": ["uv", "run", "python", "runner.py"],
    },
    {
        "name": "metagpt",
        "cwd": BASELINES_DIR / "metagpt_baseline",
        "cmd": ["uv", "run", "python", "runner.py"],
    },
]


def run_baseline(baseline: dict, topic: str) -> None:
    name = baseline["name"]
    cmd = baseline["cmd"] + [topic]
    cwd = baseline["cwd"]

    print(f"\n{'=' * 60}")
    print(f"[{name}] Running: {' '.join(cmd)}")
    print(f"[{name}] cwd: {cwd}")
    print(f"{'=' * 60}")

    try:
        subprocess.run(cmd, cwd=str(cwd), check=True)
    except subprocess.CalledProcessError as e:
        print(f"[{name}] FAILED with exit code {e.returncode}")
    except FileNotFoundError:
        print(f"[{name}] SKIPPED (uv not found or env not set up)")
        print(f"  → Run: cd {cwd} && uv sync")


def main():
    parser = argparse.ArgumentParser(description="Run all baselines")
    parser.add_argument("topic", nargs="?", help="Single topic")
    parser.add_argument("--topics-file", help="JSONL file with topics")
    parser.add_argument("--only", help="Comma-separated list of baselines to run")
    args = parser.parse_args()

    # Collect topics
    topics = []
    if args.topic:
        topics.append(args.topic)
    if args.topics_file:
        with open(args.topics_file, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    topics.append(data["topic"])

    if not topics:
        parser.error("Provide a topic or --topics-file")

    # Filter baselines
    active = BASELINES
    if args.only:
        names = set(args.only.split(","))
        active = [b for b in BASELINES if b["name"] in names]

    for topic in topics:
        print(f"\n{'#' * 60}")
        print(f"# Topic: {topic}")
        print(f"{'#' * 60}")
        for baseline in active:
            run_baseline(baseline, topic)


if __name__ == "__main__":
    main()
