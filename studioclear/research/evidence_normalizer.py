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

from urllib.parse import urlparse


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
