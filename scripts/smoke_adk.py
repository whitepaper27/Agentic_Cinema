"""Live ADK smoke test (sol.md §25).

Proves the Researcher is a real google.adk Agent that calls the parallel_search
tool at runtime and returns genuine sources.

    python scripts/smoke_adk.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from studioclear.models import ClearanceItem, ItemType
from studioclear.providers.adk_search import ADKSearchProvider


def main() -> int:
    item = ClearanceItem(
        item_id="CLR-011", scene=6, type=ItemType.HISTORICAL_CLAIM,
        text_span="the Apollo 11 Moon landing in 1969",
    )
    sources = ADKSearchProvider().search(
        "authoritative sources on the Apollo 11 Moon landing in 1969", item
    )
    print(f"ADK researcher agent -> parallel_search returned {len(sources)} sources:")
    for s in sources:
        print("  ", s["source_url"])
    assert sources and all(s["source_url"].startswith("http") for s in sources)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
