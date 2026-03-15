"""Thin CLI wrapper to run ViviDoc pipeline for a single topic.

Usage (from codebase/):
    uv run python baselines/vividoc_wrapper.py "Fourier Transform"
"""

import argparse
import json
import sys
import time
from pathlib import Path

DEFAULT_MODEL = "openrouter/google/gemini-3-flash-preview"


def main():
    # Lazy import: add project root so we can import vividoc
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from vividoc.core.runner import Runner  # noqa: E402
    from vividoc.core.config import RunnerConfig  # noqa: E402

    parser = argparse.ArgumentParser(description="ViviDoc single-topic runner")
    parser.add_argument("topic", help="Topic for the document")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    print(f"[vividoc] Generating: {args.topic[:60]}")
    t0 = time.time()

    config = RunnerConfig(
        llm_model=args.model,
        output_dir=args.output_dir,
        resume=True,
    )
    runner = Runner(config)
    doc = runner.run(args.topic)

    elapsed = time.time() - t0
    meta = {
        "topic": args.topic,
        "model": args.model,
        "baseline": "vividoc",
        "elapsed_sec": round(elapsed, 2),
        "html_file": doc.html_file_path,
        "num_kus": len(doc.knowledge_units),
    }
    print(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"[vividoc] Done {elapsed:.1f}s, {len(doc.knowledge_units)} KUs")


if __name__ == "__main__":
    main()
