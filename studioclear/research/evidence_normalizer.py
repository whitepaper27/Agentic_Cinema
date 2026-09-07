"""Evidence normalization — with the integrity invariant enforced in code.

THE most important enterprise property of a research product (sol.md E8.1):
the LLM can NEVER emit a citation. Source URLs are passed through verbatim from
the Parallel API response; the model may only classify/excerpt URLs that already
exist there. `enforce_grounded_sources` is the structural guard, and
`deterministic_confidence` keeps confidence an honest function of the evidence
(sol.md §20 — no fake scores). Both are pure and tested (tests/adversarial,
tests/unit).
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from studioclear.models import ClaimAssessment, Relation, Source, SourceType

_WS = re.compile(r"\s+")


def normalize_quote(text: str) -> str:
    """Documented whitespace/case normalization for quote matching (sol.md §7).
    Collapse runs of whitespace, strip, and lowercase so a model quote is matched
    against the retrieved passage without punctuation-free trickery."""
    return _WS.sub(" ", (text or "")).strip().lower()


def resolve_assessments(
    raw_assessments: list[dict], sources: list[Source]
) -> tuple[list[ClaimAssessment], list[dict]]:
    """Resolve model-selected references against stored sources (sol.md §7).

    The model returns dicts referencing a `source_id` and a `quote`. Code:
      * rejects unknown source ids (`unknown_source_id`),
      * rejects quotes that do not match a retrieved passage (`quote_not_grounded`),
      * sets the displayed `passage` to the STORED passage, not the model text,
      * fills `publisher` from the stored URL (never trusts a model-supplied URL).
    Returns (validated, dropped) where dropped rows carry a reason for the audit.
    """
    by_id = {s.source_id: s for s in sources}
    validated: list[ClaimAssessment] = []
    dropped: list[dict] = []

    for raw in raw_assessments:
        sid = raw.get("source_id")
        src = by_id.get(sid)
        if src is None:
            dropped.append({"source_id": sid, "reason": "unknown_source_id"})
            continue

        want = normalize_quote(raw.get("quote", ""))
        match = next((p for p in src.passages if normalize_quote(p) == want), None)
        if match is None:
            # Allow a substring match against a longer retrieved passage.
            match = next((p for p in src.passages if want and want in normalize_quote(p)), None)
        if match is None:
            dropped.append({"source_id": sid, "reason": "quote_not_grounded"})
            continue

        try:
            relation = Relation(raw.get("relation", "unclear"))
        except ValueError:
            relation = Relation.UNCLEAR
        try:
            source_type = SourceType(raw.get("source_type", "unknown"))
        except ValueError:
            source_type = SourceType.UNKNOWN

        validated.append(ClaimAssessment(
            source_id=src.source_id,
            relation=relation,
            applicable=bool(raw.get("applicable", False)),
            source_type=source_type,
            publisher=publisher_of(src.url),          # code-derived, never from model
            independence=src.independence,
            passage=match,                            # stored text, not model quote
            explanation=str(raw.get("explanation", "")),
            limitations=str(raw.get("limitations", "")),
        ))

    return validated, dropped


def publisher_of(url: str) -> str:
    """Registrable-ish host, used for the source-independence check (E5.7)."""
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def enforce_grounded_sources(
    candidate_urls: list[str], allowed_urls: list[str]
) -> tuple[list[str], list[str]]:
    """Keep only candidate URLs that provably came from Parallel.

    Returns (grounded, dropped). Any URL not in `allowed_urls` (the raw Parallel
    response set) is dropped and must be logged — it means something tried to
    introduce a citation the API never returned. Order and de-dup are stable.
    """
    allowed = set(allowed_urls)
    grounded: list[str] = []
    dropped: list[str] = []
    seen: set[str] = set()
    for url in candidate_urls:
        if url in seen:
            continue
        seen.add(url)
        (grounded if url in allowed else dropped).append(url)
    return grounded, dropped


def independent_source_count(urls: list[str]) -> int:
    """Count distinct publishers, not distinct URLs (guards against the same
    syndicated story under two links) — sol.md E5.7."""
    return len({publisher_of(u) for u in urls if u})


def deterministic_confidence(independent_sources: int) -> float:
    """Fixed function of independent-source count (sol.md E3.1.5). Never a
    model-guessed probability, so it is defensible and testable."""
    return min(1.0, 0.4 + 0.2 * max(0, independent_sources))


def normalize_evidence(raw_parallel_result: dict) -> dict:  # pragma: no cover - stub
    """STUB (sol.md E3.1.5): call gemini-2.5-flash to classify `supports` and
    write excerpts, but ONLY over URLs present in `raw_parallel_result`. Then run
    the output through enforce_grounded_sources before returning EvidenceRecords.
    """
    raise NotImplementedError("Wire gemini-2.5-flash normalization on the Day-1 build.")
