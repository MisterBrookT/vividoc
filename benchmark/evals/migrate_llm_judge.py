"""One-time migration: convert flat llm_judge to nested {model: {dims}} format.

Current eval_result.json files have:
  "llm_judge": {"content_richness": {...}, "interaction_design": {...}, "visual_quality": {...}}

After migration:
  "llm_judge": {"google/gemini-3.1-pro-preview": {"content_richness": {...}, ...}}

Usage:
    cd codebase
    uv run python benchmark/evals/migrate_llm_judge.py
"""

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
MODEL_NAME = "google/gemini-3.1-pro-preview"
DIM_KEYS = {"content_richness", "interaction_design", "visual_quality"}


def migrate():
    count = 0
    for result_path in sorted(RESULTS_DIR.rglob("eval_result.json")):
        data = json.loads(result_path.read_text())
        llm_judge = data.get("llm_judge", {})
        if not llm_judge:
            continue

        # Check if already nested (no dim keys at top level)
        if not any(k in llm_judge for k in DIM_KEYS):
            print(f"  SKIP (already nested): {result_path.relative_to(RESULTS_DIR)}")
            continue

        # Migrate: wrap under model name
        data["llm_judge"] = {MODEL_NAME: llm_judge}
        result_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        count += 1
        print(f"  OK: {result_path.relative_to(RESULTS_DIR)}")

    print(f"\nMigrated {count} files.")


if __name__ == "__main__":
    migrate()
