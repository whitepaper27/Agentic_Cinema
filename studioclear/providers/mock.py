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
import re
from pathlib import Path

from studioclear.models import ClearanceItem, Source
from studioclear.providers.base import Providers
from studioclear.research.evidence_normalizer import publisher_of

DEMO = Path("demo")

# Authoritative primary-source hosts for the deterministic mock assessment. Real
# primary/secondary judgement is the live model's job (sol.md §7); the mock just
# needs a stable, defensible rule so offline runs show honest variety.
_PRIMARY_SUFFIXES = (".gov", ".int", ".mil", ".edu")
_YEAR = re.compile(r"\b(1[6-9]\d\d|20\d\d)\b")


def _mock_source_type(url: str) -> str:
    return "primary" if publisher_of(url).endswith(_PRIMARY_SUFFIXES) else "secondary"


def _years(text: str) -> list[str]:
    return _YEAR.findall(text or "")


class MockLLMProvider:
    def __init__(self, extraction_path: Path = DEMO / "mock_extraction.json"):
        self._items = json.loads(extraction_path.read_text(encoding="utf-8"))["items"]

    def extract_items(self, scenes: list[dict]) -> list[ClearanceItem]:
        # `scenes` is accepted (and produced by the real parser) but the mock
        # returns fixed simulated output for determinism.
        return [ClearanceItem(**it) for it in self._items]

    def extract_items_from_images(self, images: list[dict]) -> list[ClearanceItem]:
        # Simulated vision output for offline runs; ignores pixels. Real vision is
        # the live provider's job — the API must never use this for a live upload.
        return [ClearanceItem(**it) for it in self._items]

    def propose_revision(self, scene_text, claim, evidence, instruction, locks):
        # Deterministic offline stand-in for a revision proposal. Correct the
        # claim's year to the year stated in the evidence; if none differs, make a
        # small visible edit. Only the claim span is touched.
        original = claim
        claim_years = _years(claim)
        ev_years = [y for e in evidence for y in _years(e.get("passage", ""))]
        proposed = original
        if claim_years:
            cy = claim_years[0]
            corrected = next((y for y in ev_years if y != cy), None)
            proposed = original.replace(cy, corrected or str(int(cy) - 1), 1)
        if proposed == original:
            proposed = original + " (reviewed)"
        return {
            "original_text": original,
            "proposed_text": proposed,
            "rationale": "mock: aligned the detail to the retrieved sources",
            "evidence_source_ids": [e.get("source_id") for e in evidence
                                    if e.get("source_id")][:2],
            "art_change": "",
        }

    def assess_claim(self, claim: str, sources: list[Source]) -> list[dict]:
        # Deterministic offline stand-in for gemini-2.5-flash passage grading. A
        # passage supports the claim unless it states a DIFFERENT year than the
        # claim (a researchable factual mismatch) — then it contradicts. Quotes
        # are copied verbatim so they always ground. Real grading is live Gemini.
        out: list[dict] = []
        cyears = set(_years(claim))
        for s in sources:
            passage = s.passages[0] if s.passages else ""
            pyears = set(_years(passage))
            if cyears and pyears and not (cyears & pyears):
                relation, why = "contradicts", "mock: source states a different year"
            else:
                relation, why = "supports", "mock: passage restates the claim"
            out.append({
                "source_id": s.source_id,
                "relation": relation,
                "quote": passage,
                "applicable": True,
                "source_type": _mock_source_type(s.url),
                "explanation": why,
            })
        return out


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


def build_example_providers() -> Providers:
    """Simulated providers for the labeled 'Try an example' showcase — a fixture
    with one factual mismatch that a revision can correct and a recheck can flip
    (sol.md §14). Clearly a Simulated example; never presented as a live run."""
    return Providers(
        llm=MockLLMProvider(DEMO / "example_extraction.json"),
        search=MockSearchProvider(DEMO / "example_evidence.json"),
    )
