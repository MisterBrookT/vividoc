"""Batch evaluation runner.

Scans outputs/{topic}/{method}/document.html and runs all evaluations.

Usage:
    cd codebase
    uv run python evals/run_eval.py
    uv run python evals/run_eval.py --topic "what_is_pi"
    uv run python evals/run_eval.py --method vividoc --method naive_agent
    uv run python evals/run_eval.py --judge-model openrouter/google/gemini-3-flash-preview
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from benchmark.evals.llm_judge import evaluate_document
from benchmark.evals.functional_eval import evaluate_functional
from vividoc.utils.llm.client import LLMClient

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
EVAL_RESULTS_DIR = Path(__file__).parent / "results"
DEFAULT_JUDGE_MODEL = "openrouter/google/gemini-3-flash-preview"

METHODS = ["vividoc", "naive_agent", "autogen", "camel", "metagpt"]


def find_documents(
    outputs_dir: Path,
    topic_filter: str | None = None,
    method_filter: list[str] | None = None,
) -> list[dict]:
    """Discover all document.html files in outputs/."""
    docs = []
    if not outputs_dir.exists():
        return docs

    for topic_dir in sorted(outputs_dir.iterdir()):
        if not topic_dir.is_dir():
            continue
        if topic_filter and topic_dir.name != topic_filter:
            continue

        for method_dir in sorted(topic_dir.iterdir()):
            if not method_dir.is_dir():
                continue
            if method_filter and method_dir.name not in method_filter:
                continue

            html_path = method_dir / "document.html"
            if html_path.exists():
                # Try to recover topic from meta.json
                meta_path = method_dir / "meta.json"
                topic_name = topic_dir.name
                if meta_path.exists():
                    try:
                        meta = json.loads(meta_path.read_text())
                        topic_name = meta.get("topic", topic_dir.name)
                    except (json.JSONDecodeError, KeyError):
                        pass

                docs.append(
                    {
                        "topic": topic_name,
                        "topic_dir": topic_dir.name,
                        "method": method_dir.name,
                        "html_path": str(html_path),
                    }
                )
    return docs


def evaluate_one(
    doc: dict, client: LLMClient | None, functional_only: bool = False
) -> dict:
    """Run evaluations on a single document."""
    html_path = doc["html_path"]
    topic = doc["topic"]
    method = doc["method"]

    print(f"  [{method}] Evaluating{'(functional only)' if functional_only else ''}...")

    # 1. Functional eval (Playwright) — also captures screenshot
    result_dir = EVAL_RESULTS_DIR / doc["topic_dir"] / method
    result_dir.mkdir(parents=True, exist_ok=True)

    func_result = evaluate_functional(html_path, screenshot_dir=str(result_dir))

    if functional_only:
        scores = {
            "topic": topic,
            "method": method,
            "render_correctness": func_result["render_correctness"],
            "interaction_functionality": func_result["interaction_functionality"],
        }
        # Merge with existing LLM scores if available
        existing_path = result_dir / "eval_result.json"
        if existing_path.exists():
            try:
                existing = json.loads(existing_path.read_text())
                old_scores = existing.get("scores", {})
                scores["content_richness"] = old_scores.get("content_richness", 0)
                scores["interaction_design"] = old_scores.get("interaction_design", 0)
                scores["visual_quality"] = old_scores.get("visual_quality", 0)
                # Update functional parts in existing result
                existing["scores"].update(
                    {
                        "render_correctness": scores["render_correctness"],
                        "interaction_functionality": scores[
                            "interaction_functionality"
                        ],
                    }
                )
                existing["functional"] = {
                    k: v for k, v in func_result.items() if k != "interaction_details"
                }
                existing["functional_details"] = func_result.get(
                    "interaction_details", []
                )
                existing_path.write_text(
                    json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8"
                )
            except (json.JSONDecodeError, KeyError):
                pass
        return scores

    # 2. LLM-as-Judge
    screenshot_path = func_result.get("screenshot_path")
    llm_result = evaluate_document(client, topic, html_path, screenshot_path)

    # Combine
    scores = {
        "topic": topic,
        "method": method,
        # LLM-as-Judge scores (1-5)
        "content_richness": llm_result["content_richness"]["score"],
        "interaction_design": llm_result["interaction_design"]["score"],
        "visual_quality": llm_result["visual_quality"]["score"],
        # Functional scores (0-1)
        "render_correctness": func_result["render_correctness"],
        "interaction_functionality": func_result["interaction_functionality"],
    }

    # Save detailed results
    detailed = {
        "scores": scores,
        "llm_judge": llm_result,
        "functional": {
            k: v
            for k, v in func_result.items()
            if k != "interaction_details"  # keep output small
        },
        "functional_details": func_result.get("interaction_details", []),
    }
    (result_dir / "eval_result.json").write_text(
        json.dumps(detailed, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return scores


def main():
    parser = argparse.ArgumentParser(
        description="Run evaluations on generated documents"
    )
    parser.add_argument("--topic", help="Evaluate only this topic dirname")
    parser.add_argument(
        "--method", action="append", help="Evaluate only these methods (repeatable)"
    )
    parser.add_argument(
        "--judge-model", default=DEFAULT_JUDGE_MODEL, help="LLM model for judge"
    )
    parser.add_argument("--outputs-dir", default=str(OUTPUTS_DIR))
    parser.add_argument(
        "--skip-existing", action="store_true", help="Skip if eval_result.json exists"
    )
    parser.add_argument(
        "--functional-only",
        action="store_true",
        help="Only run Playwright functional eval (RC + IF), skip LLM judge",
    )
    args = parser.parse_args()

    outputs_dir = Path(args.outputs_dir)
    docs = find_documents(outputs_dir, args.topic, args.method)

    if not docs:
        print("No documents found to evaluate.")
        return

    # Filter already evaluated
    if args.skip_existing:
        filtered = []
        for doc in docs:
            result_path = (
                EVAL_RESULTS_DIR / doc["topic_dir"] / doc["method"] / "eval_result.json"
            )
            if not result_path.exists():
                filtered.append(doc)
        docs = filtered

    print(
        f"Evaluating {len(docs)} documents{' (functional only)' if args.functional_only else ''} (judge: {args.judge_model})"
    )

    client = None if args.functional_only else LLMClient(args.judge_model)
    all_scores = []

    for doc in docs:
        topic_label = doc["topic_dir"]
        print(f"\n[{topic_label}]")
        try:
            scores = evaluate_one(doc, client, functional_only=args.functional_only)
            all_scores.append(scores)
            print(
                f"  [{doc['method']}] CR={scores['content_richness']} "
                f"ID={scores['interaction_design']} "
                f"VQ={scores['visual_quality']} "
                f"RC={scores['render_correctness']} "
                f"IF={scores['interaction_functionality']}"
            )
        except Exception as e:
            print(f"  [{doc['method']}] ERROR: {e}")
            all_scores.append(
                {
                    "topic": doc["topic"],
                    "method": doc["method"],
                    "error": str(e),
                }
            )

    # Save summary
    EVAL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = EVAL_RESULTS_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(all_scores, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nSummary saved to {summary_path}")

    # Print aggregate table
    _print_summary(all_scores)


def _print_summary(all_scores: list[dict]):
    """Print a quick aggregate table."""
    from collections import defaultdict

    by_method = defaultdict(list)
    for s in all_scores:
        if "error" not in s:
            by_method[s["method"]].append(s)

    if not by_method:
        return

    print(
        f"\n{'Method':<15} {'CR':>5} {'ID':>5} {'VQ':>5} {'RC':>5} {'IF':>5} {'N':>4}"
    )
    print("-" * 55)
    for method in METHODS:
        entries = by_method.get(method, [])
        if not entries:
            continue
        n = len(entries)
        cr = sum(e["content_richness"] for e in entries) / n
        iq = sum(e["interaction_design"] for e in entries) / n
        vq = sum(e["visual_quality"] for e in entries) / n
        rc = sum(e["render_correctness"] for e in entries) / n
        ifn = sum(e["interaction_functionality"] for e in entries) / n
        print(
            f"{method:<15} {cr:>5.2f} {iq:>5.2f} {vq:>5.2f} {rc:>5.2f} {ifn:>5.2f} {n:>4}"
        )


if __name__ == "__main__":
    main()
