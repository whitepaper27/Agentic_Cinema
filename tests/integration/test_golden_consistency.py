"""The golden fixture is self-consistent: valid types/states, 14 items, and the
declared distribution matches the items (sol.md E2.3)."""

import json
from collections import Counter
from pathlib import Path

from studioclear.models import ClearanceState, ItemType

GOLDEN = Path("demo/expected_items.json")


def test_golden_is_valid_and_consistent():
    data = json.loads(GOLDEN.read_text(encoding="utf-8"))
    items = data["items"]
    assert len(items) == 14

    for it in items:
        ItemType(it["type"])                 # raises if invalid
        ClearanceState(it["expected_state"])  # raises if invalid

    dist = Counter(it["expected_state"] for it in items)
    assert dict(dist) == data["expected_distribution"]
