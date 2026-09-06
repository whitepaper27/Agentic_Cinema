"""Parallel Search wrapper (sol.md §9 / E3.1.4).

The load-bearing runtime research engine. This module gets the most tests
(sol.md E5.2): retry/backoff, empty-result handling, multi-source assertion,
latency budget. Kept thin so the raw response (the source of truth for URLs, per
the E8.1 integrity invariant) flows straight through.
"""

from __future__ import annotations

# from parallel import Parallel   # sol.md E1.3 — client = Parallel() reads PARALLEL_API_KEY


def parallel_search(query: str) -> dict:  # pragma: no cover - stub
    """STUB. Run one real Parallel search and return the raw result unchanged.

    Day-1 build (sol.md E3.1):
        from parallel import Parallel
        client = Parallel()
        return client.search(...)   # confirm method/params against docs.parallel.ai

    The caller extracts source URLs from THIS raw result; the LLM never sees a
    chance to invent one (E8.1).
    """
    raise NotImplementedError("Wire the parallel-web SDK on the Day-1 build.")
