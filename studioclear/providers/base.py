"""Provider Protocols + bundle (sol.md E3.1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from studioclear.models import ClearanceItem, Source


class LLMProvider(Protocol):
    """Extraction + claim assessment (gemini in live mode). All inputs are
    untrusted and handled as data, never instructions (sol.md §11)."""

    def extract_items(self, scenes: list[dict]) -> list[ClearanceItem]:
        ...

    def extract_items_from_images(self, images: list[dict]) -> list[ClearanceItem]:
        """Read uploaded comic/storyboard pages (sol.md §13.2). Each image is
        {"data": bytes, "mime_type": str}; `scene` is the 1-based page number.
        Visual references are candidates — identity/ownership is never inferred
        from a drawing."""
        ...

    def assess_claim(self, claim: str, sources: list[Source]) -> list[dict]:
        """Classify each retrieved passage against the claim (sol.md §7).

        Returns raw dicts referencing a stored `source_id` and a `quote`; the
        model NEVER supplies a URL. Code validates these against the stored
        sources via research.evidence_normalizer.resolve_assessments."""
        ...

    def suggest_locations(self, scene_text: str, instruction: str) -> list[dict]:
        """Suggest candidate alternative filming locations (sol.md §6A) as
        [{"name", "rationale"}]. These are leads to research and confirm — never an
        assertion of feasibility, permission, or cost. The producer picks one."""
        ...

    def propose_creative(self, scene_text: str, instruction: str, kind: str) -> dict:
        """Propose optional AI-authored scene text (sol.md §7) — an elaboration or a
        dialogue/action rewrite. Returns {original_text, proposed_text, rationale};
        NO citations (it is creative, not researched). `original_text` empty means an
        addition; otherwise a replacement. Preserves author fantasy premises."""
        ...

    def propose_revision(
        self, scene_text: str, claim: str, evidence: list[dict],
        instruction: str, locks: list[str],
    ) -> dict:
        """Propose the smallest supported text edit for a claim (sol.md §8).

        Returns {"original_text", "proposed_text", "rationale",
        "evidence_source_ids", "art_change"}. `original_text` must be a verbatim
        span of `scene_text`; edits must preserve every locked span. The model
        returns text + source_ids only — code validates locks and evidence refs."""
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
