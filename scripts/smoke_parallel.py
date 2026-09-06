"""Parallel smoke test (sol.md E1.5 #2): prove Parallel authenticates and returns
REAL source URLs.

    python scripts/smoke_parallel.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from studioclear.models import ClearanceItem, ItemType
from studioclear.providers.parallel import ParallelSearchProvider


def main() -> int:
    item = ClearanceItem(
        item_id="CLR-001", scene=1, type=ItemType.HISTORICAL_CLAIM,
        text_span="the Apollo 11 Moon landing in 1969",
    )
    sources = ParallelSearchProvider().search(
        "When did the Apollo 11 Moon landing occur?", item
    )
    print(f"Parallel returned {len(sources)} sources:")
    for s in sources:
        print(" ", s["source_url"])
    assert sources and all(s["source_url"].startswith("http") for s in sources)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
