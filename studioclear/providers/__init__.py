"""Provider abstraction (sol.md E2.5 / E3.1).

The spine depends on two external capabilities — an LLM (extraction) and a
search engine (evidence). Both sit behind Protocols so the pipeline runs
fully offline/deterministic in MOCK mode, and swaps to the real Gemini /
Parallel adapters when credentials are present. No product logic changes.
"""

from __future__ import annotations

from studioclear.config import Config
from studioclear.providers.base import LLMProvider, Providers, SearchProvider
from studioclear.providers.mock import (
    MockLLMProvider,
    MockSearchProvider,
    build_mock_providers,
)

__all__ = [
    "LLMProvider",
    "SearchProvider",
    "Providers",
    "build_mock_providers",
    "build_providers",
    "describe_providers",
]


def build_providers(prefer_live: bool = True) -> Providers:
    """Use live adapters where a key exists, else deterministic mocks.

    Gemini extraction turns on with a Gemini key; Parallel search turns on with
    PARALLEL_API_KEY. Missing either just falls back to the mock for that stage,
    so a partial-credential setup still produces a full, honest run.
    """
    cfg = Config.from_env()

    if prefer_live and cfg.gemini_api_key:
        from studioclear.providers.gemini import GeminiLLMProvider

        llm: LLMProvider = GeminiLLMProvider()
    else:
        llm = MockLLMProvider()

    if prefer_live and cfg.parallel_api_key:
        from studioclear.providers.parallel import ParallelSearchProvider

        search: SearchProvider = ParallelSearchProvider()
    else:
        search = MockSearchProvider()

    return Providers(llm=llm, search=search)


def describe_providers(p: Providers) -> dict:
    """Human-readable which-is-live summary (for /healthz and CLI banners)."""
    return {
        "llm": type(p.llm).__name__,
        "search": type(p.search).__name__,
    }
