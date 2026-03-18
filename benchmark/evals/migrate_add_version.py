"""One-time migration: add @v1 suffix to existing llm_judge model keys.

Before: "google/gemini-3.1-pro-preview": {...}
After:  "google/gemini-3.1-pro-preview@v1": {...}

Usage:
    cd codebase
    uv run python benchmark/evals/migrate_add_version.py
"""

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"


def migrate():
    count = 0
    for result_path in sorted(RESULTS_DIR.rglob("eval_result.json")):
        data = json.loads(result_path.read_text())
        llm_judge = data.get("llm_judge", {})
        if not llm_judge:
            continue

        new_judge = {}
        changed = False
        for key, val in llm_judge.items():
            if "@" not in key:
                new_key = f"{key}@v1"
                changed = True
            else:
                new_key = key
            new_judge[new_key] = val

        if changed:
            data["llm_judge"] = new_judge
            result_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            count += 1
            print(f"  OK: {result_path.relative_to(RESULTS_DIR)}")
        else:
            print(f"  SKIP: {result_path.relative_to(RESULTS_DIR)}")

    print(f"\nMigrated {count} files.")


if __name__ == "__main__":
    migrate()
