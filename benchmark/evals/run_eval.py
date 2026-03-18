"""Batch evaluation runner.

Scans outputs/{topic}/{method}/document.html and runs all evaluations.

Usage:
    cd codebase
    uv run python benchmark/evals/run_eval.py
    uv run python benchmark/evals/run_eval.py --topic the_definition_of_pi_as_the_ratio_of_circumference_to_diameter
    uv run python benchmark/evals/run_eval.py --method vividoc --method naive_agent
    uv run python benchmark/evals/run_eval.py --force                          # re-evaluate all
    uv run python benchmark/evals/run_eval.py --dimension ID --force           # re-run ID only
    uv run python benchmark/evals/run_eval.py --dimension ID --dimension VQ --force
    uv run python benchmark/evals/run_eval.py --llm-only --force               # re-run CR+ID+VQ
    uv run python benchmark/evals/run_eval.py --functional-only --force        # re-run RC+IF
    uv run python benchmark/evals/run_eval.py --version v3 --force --llm-only  # new prompt version
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from benchmark.evals.llm_judge import (
    evaluate_content_richness,
    evaluate_interaction_design,
    evaluate_visual_quality,
    extract_text_content,
    _parse_score,
)
from benchmark.evals.prompts import VISUAL_QUALITY_PROMPT
from benchmark.evals.functional_eval import evaluate_functional
from vividoc.utils.llm.client import LLMClient

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
EVAL_RESULTS_DIR = Path(__file__).parent / "results"
DEFAULT_JUDGE_MODEL = "openrouter/google/gemini-3-flash-preview"

METHODS = ["vividoc", "naive_agent", "autogen", "camel", "metagpt"]


def _discover_methods() -> list[str]:
    """Discover all method names from outputs and eval results directories."""
    methods = set()
    for base_dir in (OUTPUTS_DIR, EVAL_RESULTS_DIR):
        if not base_dir.exists():
            continue
        for topic_dir in base_dir.iterdir():
            if not topic_dir.is_dir():
                continue
            for method_dir in topic_dir.iterdir():
                if method_dir.is_dir() and method_dir.name != ".DS_Store":
                    methods.add(method_dir.name)
    # Sort: known base methods first (grouped), then alphabetical
    BASE_ORDER = ["vividoc", "naive_agent", "autogen", "camel", "metagpt"]

    def sort_key(m):
        # Extract base method name (before _model suffix)
        for i, base in enumerate(BASE_ORDER):
            if m == base or m.startswith(base + "_"):
                return (i, m)
        return (len(BASE_ORDER), m)

    return sorted(methods, key=sort_key)


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


# Mapping from short dimension names to internal keys
DIM_ALIASES = {
    "CR": "content_richness",
    "ID": "interaction_design",
    "VQ": "visual_quality",
    "RC": "render_correctness",
    "IF": "interaction_functionality",
}
LLM_DIMS = {"content_richness", "interaction_design", "visual_quality"}
FUNC_DIMS = {"render_correctness", "interaction_functionality"}


DEFAULT_PROMPT_VERSION = "v2"


def _normalize_model_name(judge_model: str, version: str = "") -> str:
    """Build storage key: 'model@version'. Strip 'openrouter/' prefix."""
    name = judge_model
    if name.startswith("openrouter/"):
        name = name[len("openrouter/") :]
    if version:
        name = f"{name}@{version}"
    return name


def _migrate_llm_judge(
    existing: dict, fallback_model: str = "google/gemini-3.1-pro-preview"
) -> dict:
    """Migrate old flat llm_judge format to nested {model: {dims}} format.

    Old format:  llm_judge: {content_richness: {score, reason}, ...}
    New format:  llm_judge: {model_name: {content_richness: {score, reason}, ...}}
    """
    llm_judge = existing.get("llm_judge", {})
    if not llm_judge:
        return llm_judge
    # Detect old flat format: keys are dimension names, not model names
    if any(
        k in llm_judge
        for k in ("content_richness", "interaction_design", "visual_quality")
    ):
        # Old format — wrap under fallback model
        migrated = {fallback_model: llm_judge}
        return migrated
    return llm_judge


def evaluate_one(
    doc: dict,
    client: LLMClient | None,
    dimensions: set[str] | None = None,
    model_name: str = "",
) -> dict:
    """Run evaluations on a single document.

    Args:
        dimensions: Set of dimension keys to evaluate. None means all.
            LLM dims: content_richness, interaction_design, visual_quality
            Functional dims: render_correctness, interaction_functionality
        model_name: Clean model name (e.g. "google/gemini-3-flash-preview")
            for storing LLM judge results under llm_judge[model_name].
    """
    html_path = doc["html_path"]
    topic = doc["topic"]
    method = doc["method"]

    result_dir = EVAL_RESULTS_DIR / doc["topic_dir"] / method
    result_dir.mkdir(parents=True, exist_ok=True)
    existing_path = result_dir / "eval_result.json"

    # Load existing results to merge with
    existing = {}
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text())
        except (json.JSONDecodeError, KeyError):
            existing = {}

    old_scores = existing.get("scores", {})

    # Migrate llm_judge to nested format if needed
    llm_judge_all = _migrate_llm_judge(existing)

    # Determine what to run
    if dimensions is None:
        need_llm = True
        need_func = True
    else:
        need_llm = bool(dimensions & LLM_DIMS)
        need_func = bool(dimensions & FUNC_DIMS)

    mode_parts = []
    if need_func and not need_llm:
        mode_parts.append("functional only")
    elif need_llm and not need_func:
        mode_parts.append("LLM only")
    if dimensions:
        dim_short = [k for k, v in DIM_ALIASES.items() if v in dimensions]
        mode_parts.append(",".join(dim_short))
    mode_label = f" ({'; '.join(mode_parts)})" if mode_parts else ""
    print(f"  [{method}] Evaluating{mode_label}...")

    # --- Functional eval ---
    func_result = existing.get("functional", {})
    if need_func:
        func_result = evaluate_functional(html_path, screenshot_dir=str(result_dir))
        existing["functional"] = {
            k: v for k, v in func_result.items() if k != "interaction_details"
        }
        existing["functional_details"] = func_result.get("interaction_details", [])
    else:
        # Restore interaction_details for LLM prompt
        func_result["interaction_details"] = existing.get("functional_details", [])

    # --- LLM-as-Judge ---
    model_judge = llm_judge_all.get(model_name, {}) if model_name else {}
    if need_llm:
        html = Path(html_path).read_text(encoding="utf-8")
        text_content = extract_text_content(html)

        screenshot_path = str(result_dir / "screenshot.png")
        if not Path(screenshot_path).exists():
            screenshot_path = func_result.get("screenshot_path")

        run_cr = dimensions is None or "content_richness" in dimensions
        run_id = dimensions is None or "interaction_design" in dimensions
        run_vq = dimensions is None or "visual_quality" in dimensions

        if run_cr:
            cr = evaluate_content_richness(client, topic, text_content)
            model_judge["content_richness"] = {"score": cr.score, "reason": cr.reason}

        if run_id:
            iq = evaluate_interaction_design(client, topic, html)
            model_judge["interaction_design"] = {"score": iq.score, "reason": iq.reason}

        if run_vq:
            if screenshot_path and Path(screenshot_path).exists():
                vq = evaluate_visual_quality(client, topic, html, screenshot_path)
            else:
                prompt = VISUAL_QUALITY_PROMPT.format(topic=topic, html=html)
                response = client.call_text_generation(prompt)
                vq = _parse_score(response)
            model_judge["visual_quality"] = {"score": vq.score, "reason": vq.reason}

        llm_judge_all[model_name] = model_judge
        existing["llm_judge"] = llm_judge_all

    # --- Build final scores (reflects the current model) ---
    # Pick the current model's scores, or fall back to any available model
    active_judge = model_judge if model_name else {}
    if not active_judge:
        # Fall back to first available model
        for m in llm_judge_all.values():
            if isinstance(m, dict) and "content_richness" in m:
                active_judge = m
                break

    # interaction_quality = LLM interaction_design score × IF
    id_raw = active_judge.get("interaction_design", {}).get(
        "score", old_scores.get("interaction_design", 0)
    )
    if_score = func_result.get(
        "interaction_functionality",
        old_scores.get("interaction_functionality", 0),
    )
    iq_combined = round(id_raw * if_score, 2)

    scores = {
        "topic": topic,
        "method": method,
        "content_richness": active_judge.get("content_richness", {}).get(
            "score", old_scores.get("content_richness", 0)
        ),
        "interaction_design": id_raw,
        "interaction_quality": iq_combined,
        "visual_quality": active_judge.get("visual_quality", {}).get(
            "score", old_scores.get("visual_quality", 0)
        ),
        "render_correctness": func_result.get(
            "render_correctness", old_scores.get("render_correctness", 0)
        ),
        "interaction_functionality": if_score,
    }
    existing["scores"] = scores
    existing_path.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8"
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
    parser.add_argument(
        "--version",
        default=DEFAULT_PROMPT_VERSION,
        help="Prompt version tag (stored as model@version in results). Default: "
        + DEFAULT_PROMPT_VERSION,
    )
    parser.add_argument("--outputs-dir", default=str(OUTPUTS_DIR))
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-evaluate even if eval_result.json exists (default: skip existing)",
    )
    parser.add_argument(
        "--dimension",
        action="append",
        help="Only evaluate specific dimensions (repeatable). "
        "Values: CR, ID, VQ, RC, IF. E.g. --dimension ID --dimension VQ",
    )

    # Keep legacy flags as shortcuts
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--functional-only",
        action="store_true",
        help="Shortcut for --dimension RC --dimension IF",
    )
    mode_group.add_argument(
        "--llm-only",
        action="store_true",
        help="Shortcut for --dimension CR --dimension ID --dimension VQ",
    )
    args = parser.parse_args()

    # Resolve dimensions
    dimensions = None  # None = all
    if args.dimension:
        dimensions = set()
        for d in args.dimension:
            key = DIM_ALIASES.get(d.upper())
            if not key:
                parser.error(f"Unknown dimension: {d}. Valid: {', '.join(DIM_ALIASES)}")
            dimensions.add(key)
    elif args.functional_only:
        dimensions = FUNC_DIMS.copy()
    elif args.llm_only:
        dimensions = LLM_DIMS.copy()

    outputs_dir = Path(args.outputs_dir)
    docs = find_documents(outputs_dir, args.topic, args.method)

    if not docs:
        print("No documents found to evaluate.")
        return

    # Filter already evaluated (default: skip existing unless --force)
    # Smart skip: check if the requested model@version + dimensions already exist
    to_eval = []
    skipped = 0
    model_name = _normalize_model_name(args.judge_model, args.version)

    for doc in docs:
        result_path = (
            EVAL_RESULTS_DIR / doc["topic_dir"] / doc["method"] / "eval_result.json"
        )
        if result_path.exists() and not args.force:
            # Check if the specific model@version has the requested dims
            try:
                data = json.loads(result_path.read_text())
                llm_judge = data.get("llm_judge", {})
                model_data = llm_judge.get(model_name, {})

                need_run = False
                requested_llm = (dimensions or LLM_DIMS) & LLM_DIMS
                requested_func = (dimensions or FUNC_DIMS) & FUNC_DIMS

                # Check LLM dims for this model@version
                for dim in requested_llm:
                    if dim not in model_data:
                        need_run = True
                        break

                # Check functional dims
                if not need_run and requested_func:
                    func = data.get("functional", {})
                    for dim in requested_func:
                        if dim not in func:
                            need_run = True
                            break

                if need_run:
                    to_eval.append(doc)
                else:
                    skipped += 1
            except (json.JSONDecodeError, KeyError):
                to_eval.append(doc)
        else:
            to_eval.append(doc)

    if skipped:
        print(f"Skipping {skipped} already-evaluated documents (use --force to re-run)")

    if to_eval:
        need_llm = dimensions is None or bool(dimensions & LLM_DIMS)
        client = LLMClient(args.judge_model) if need_llm else None

        dim_label = ""
        if dimensions:
            shorts = [k for k, v in DIM_ALIASES.items() if v in dimensions]
            dim_label = f" dims=[{','.join(shorts)}]"
        print(
            f"Evaluating {len(to_eval)} documents{dim_label}"
            f" (judge: {args.judge_model} → {model_name})"
        )

        for doc in to_eval:
            topic_label = doc["topic_dir"]
            print(f"\n[{topic_label}]")
            try:
                scores = evaluate_one(
                    doc, client, dimensions=dimensions, model_name=model_name
                )
                print(
                    f"  [{doc['method']}] CR={scores.get('content_richness', '-')} "
                    f"ID={scores.get('interaction_design', '-')} "
                    f"IQ={scores.get('interaction_quality', '-')} "
                    f"VQ={scores.get('visual_quality', '-')} "
                    f"RC={scores.get('render_correctness', '-')} "
                    f"IF={scores.get('interaction_functionality', '-')}"
                )
            except Exception as e:
                print(f"  [{doc['method']}] ERROR: {e}")
    else:
        print("All documents already evaluated.")

    # Always aggregate summary from ALL existing results
    all_scores = _collect_all_results()
    EVAL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Build per-model summary for JSON output
    from collections import defaultdict

    models_summary = defaultdict(list)
    for s in all_scores:
        entry = {k: v for k, v in s.items() if k != "_model"}
        models_summary[s.get("_model", "unknown")].append(entry)

    summary_path = EVAL_RESULTS_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(dict(models_summary), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    total = len(all_scores)
    n_models = len(models_summary)
    print(f"\nSummary saved to {summary_path} ({total} results, {n_models} model(s))")
    _print_summary(all_scores)


def _print_summary(all_scores: list[dict]):
    """Print a quick aggregate table per model."""
    from collections import defaultdict

    # Group by model
    models_data = defaultdict(lambda: defaultdict(list))
    for s in all_scores:
        model = s.get("_model", "unknown")
        if "error" not in s:
            models_data[model][s["method"]].append(s)

    if not models_data:
        return

    for model, by_method in sorted(models_data.items()):
        print(f"\n=== Judge: {model} ===")
        print(
            f"{'Method':<15} {'CR':>5} {'ID':>5} {'IQ':>5} {'VQ':>5} {'RC':>5} {'IF':>5} {'N':>4}"
        )
        print("-" * 62)
        all_methods = _discover_methods()
        for method in all_methods:
            entries = by_method.get(method, [])
            if not entries:
                continue
            n = len(entries)
            cr = sum(e["content_richness"] for e in entries) / n
            iq_raw = sum(e.get("interaction_design", 0) for e in entries) / n
            iq = sum(e.get("interaction_quality", 0) for e in entries) / n
            vq = sum(e["visual_quality"] for e in entries) / n
            rc = sum(e["render_correctness"] for e in entries) / n
            ifn = sum(e["interaction_functionality"] for e in entries) / n
            print(
                f"{method:<15} {cr:>5.2f} {iq_raw:>5.2f} {iq:>5.2f} {vq:>5.2f} {rc:>5.2f} {ifn:>5.2f} {n:>4}"
            )


def _collect_all_results() -> list[dict]:
    """Collect scores from all existing eval_result.json files.

    Returns one entry per (topic, method, model@version) combination.
    Each entry has a '_model' key indicating the judge model@version.

    For partial runs (e.g. only ID was re-evaluated in v2), missing LLM
    dimensions are filled from the same base model's other versions
    (preferring the highest version).
    """
    all_scores = []
    if not EVAL_RESULTS_DIR.exists():
        return all_scores
    for topic_dir in sorted(EVAL_RESULTS_DIR.iterdir()):
        if not topic_dir.is_dir():
            continue
        for method_dir in sorted(topic_dir.iterdir()):
            if not method_dir.is_dir():
                continue
            result_path = method_dir / "eval_result.json"
            if not result_path.exists():
                continue
            try:
                data = json.loads(result_path.read_text())
                llm_judge = data.get("llm_judge", {})
                func = data.get("functional", {})
                scores_base = data.get("scores", {})
                topic = scores_base.get("topic", topic_dir.name)
                method = scores_base.get("method", method_dir.name)

                # Detect format: nested (model-keyed) vs flat (legacy)
                llm_judge = _migrate_llm_judge(data)

                if not llm_judge:
                    entry = {
                        "topic": topic,
                        "method": method,
                        "_model": "unknown",
                        "content_richness": 0,
                        "interaction_design": 0,
                        "interaction_quality": 0,
                        "visual_quality": 0,
                        "render_correctness": func.get("render_correctness", 0),
                        "interaction_functionality": func.get(
                            "interaction_functionality", 0
                        ),
                    }
                    all_scores.append(entry)
                    continue

                if_val = func.get(
                    "interaction_functionality",
                    scores_base.get("interaction_functionality", 0),
                )

                # Group model keys by base model (strip @version)
                # so we can fallback missing dims across versions
                base_groups = {}  # base_model -> {version: model_scores}
                for model_key, model_scores in llm_judge.items():
                    if not isinstance(model_scores, dict):
                        continue
                    if "@" in model_key:
                        base, ver = model_key.rsplit("@", 1)
                    else:
                        base, ver = model_key, ""
                    base_groups.setdefault(base, {})[ver] = (model_key, model_scores)

                for base, versions in base_groups.items():
                    # Sort versions descending so we can fallback
                    sorted_vers = sorted(versions.keys(), reverse=True)

                    for ver in sorted_vers:
                        model_key, model_scores = versions[ver]
                        # Get dims from this version, fallback to other versions
                        cr = model_scores.get("content_richness", {}).get("score", 0)
                        id_raw = model_scores.get("interaction_design", {}).get(
                            "score", 0
                        )
                        vq = model_scores.get("visual_quality", {}).get("score", 0)

                        # Fallback missing dims from other versions of same base model
                        for fallback_ver in sorted_vers:
                            if fallback_ver == ver:
                                continue
                            _, fb_scores = versions[fallback_ver]
                            if cr == 0 and "content_richness" in fb_scores:
                                cr = fb_scores["content_richness"].get("score", 0)
                            if id_raw == 0 and "interaction_design" in fb_scores:
                                id_raw = fb_scores["interaction_design"].get("score", 0)
                            if vq == 0 and "visual_quality" in fb_scores:
                                vq = fb_scores["visual_quality"].get("score", 0)

                        entry = {
                            "topic": topic,
                            "method": method,
                            "_model": model_key,
                            "content_richness": cr,
                            "interaction_design": id_raw,
                            "interaction_quality": round(id_raw * if_val, 2),
                            "visual_quality": vq,
                            "render_correctness": func.get(
                                "render_correctness",
                                scores_base.get("render_correctness", 0),
                            ),
                            "interaction_functionality": if_val,
                        }
                        all_scores.append(entry)
            except (json.JSONDecodeError, KeyError):
                continue
    return all_scores


if __name__ == "__main__":
    main()
