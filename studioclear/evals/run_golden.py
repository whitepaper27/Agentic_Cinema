"""Golden-eval CLI (sol.md E5.6 / E5.8).

Diffs a pipeline run against demo/expected_items.json and reports recall-first.
In CI it runs `--cached` against demo/cached_run.json (no live keys). Exits
non-zero on a recall regression so it can gate merges.

Usage:
    python -m studioclear.evals.run_golden --cached demo/cached_run.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from studioclear.evals.metrics import score_extraction

EXPECTED = Path("demo/expected_items.json")


def _detected_ids_from_run(run_path: Path) -> list[str]:
    if not run_path.exists():
        return []
    data = json.loads(run_path.read_text(encoding="utf-8"))
    return [item["item_id"] for item in data.get("items", [])]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cached", type=Path, default=None, help="path to cached_run.json")
    args = ap.parse_args(argv)

    if not EXPECTED.exists():
        print("no golden set yet (demo/expected_items.json) — skipping", flush=True)
        return 0

    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    expected_ids = [item["item_id"] for item in expected.get("items", [])]
    detected_ids = _detected_ids_from_run(args.cached) if args.cached else []

    score = score_extraction(expected_ids, detected_ids)
    print(f"Recall (missed clearance risks): {score.detected_true}/{score.expected} "
          f"(missed={score.missed})")
    print(f"Precision (spurious items):      {score.precision:.2f}")

    # Gate: any missed clearance risk is a regression once a real run exists.
    if args.cached and score.missed > 0:
        print("FAIL: missed clearance risks on the golden set", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
