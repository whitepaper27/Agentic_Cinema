"""Real search provider — Parallel (sol.md E1.3 / E3.1.4).

Drop-in for MockSearchProvider. The raw result it returns is the SOLE source of
citations (evidence-integrity invariant, sol.md E8.1): URLs come straight from
the Parallel API, never from a model. Gets the heaviest tests in live mode
(sol.md E5.2): retry/backoff (handled by the SDK), empty results, multi-source.
"""

from __future__ import annotations

from studioclear.config import Config
from studioclear.models import ClearanceItem


class ParallelSearchProvider:
    def __init__(self, api_key: str | None = None, max_results: int = 5):
        from parallel import Parallel

        cfg = Config.from_env()
        self.client = Parallel(api_key=api_key or cfg.parallel_api_key)
        self.max_results = max_results

    def search(self, query: str, item: ClearanceItem) -> list[dict]:
        res = self.client.search(
            objective=query,
            search_queries=[item.text_span, f"{item.text_span} {item.type.value}"],
            max_chars_total=3000,
        )
        out: list[dict] = []
        for r in (res.results or [])[: self.max_results]:
            excerpts = getattr(r, "excerpts", None) or []
            out.append({
                "source_url": r.url,
                "title": getattr(r, "title", "") or "",
                "excerpt": (excerpts[0] if excerpts else "")[:300],
            })
        return out
