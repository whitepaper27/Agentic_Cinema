"""Deterministic offline providers (sol.md E2.5).

MockLLMProvider replays a fixture of "what the extractor would return" and
MockSearchProvider replays fixture evidence with real-looking source URLs. These
let the ENTIRE spine (planner, authz, integrity, policy, report, audit) run and
be tested with zero credentials and zero API weather. The fixtures are separate
from the eval ground truth (demo/expected_items.json) — they are simulated model
output, not the answer key.
"""

from __future__ import annotations

import json
from pathlib import Path

from studioclear.models import ClearanceItem
from studioclear.providers.base import Providers

DEMO = Path("demo")


class MockLLMProvider:
    def __init__(self, extraction_path: Path = DEMO / "mock_extraction.json"):
        self._items = json.loads(extraction_path.read_text(encoding="utf-8"))["items"]

    def extract_items(self, scenes: list[dict]) -> list[ClearanceItem]:
        # `scenes` is accepted (and produced by the real parser) but the mock
        # returns fixed simulated output for determinism.
        return [ClearanceItem(**it) for it in self._items]


class MockSearchProvider:
    def __init__(self, evidence_path: Path = DEMO / "mock_evidence.json"):
        self._by_item: dict[str, list[dict]] = json.loads(
            evidence_path.read_text(encoding="utf-8")
        )

    def search(self, query: str, item: ClearanceItem) -> list[dict]:
        # Keyed by item id in the mock; the real Parallel adapter keys on `query`.
        return list(self._by_item.get(item.item_id, []))


def build_mock_providers() -> Providers:
    return Providers(llm=MockLLMProvider(), search=MockSearchProvider())
