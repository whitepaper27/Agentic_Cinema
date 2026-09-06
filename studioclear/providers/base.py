"""Provider Protocols + bundle (sol.md E3.1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from studioclear.models import ClearanceItem


class LLMProvider(Protocol):
    """Extraction (gemini-2.5-pro in live mode). Script text is untrusted input
    and must be handled as data, never instructions (sol.md E8.2)."""

    def extract_items(self, scenes: list[dict]) -> list[ClearanceItem]:
        ...


class SearchProvider(Protocol):
    """Runtime research (Parallel in live mode). Returns RAW source dicts; the
    URLs in the return value are the ONLY citations allowed downstream — the
    evidence-integrity invariant (sol.md E8.1)."""

    def search(self, query: str, item: ClearanceItem) -> list[dict]:
        ...


@dataclass(frozen=True)
class Providers:
    llm: LLMProvider
    search: SearchProvider
