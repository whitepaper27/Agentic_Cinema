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
    build_example_providers,
    build_mock_providers,
)

__all__ = [
    "LLMProvider",
    "SearchProvider",
    "Providers",
    "LiveKeysMissing",
    "build_mock_providers",
    "build_providers",
    "build_providers_for_mode",
    "describe_providers",
]


def build_providers(prefer_live: bool = True, use_adk: bool = False) -> Providers:
    """Use live adapters where a key exists, else deterministic mocks.

    Gemini extraction turns on with a Gemini key; search turns on with
    PARALLEL_API_KEY. With use_adk=True (and both keys), the search stage runs
    through the Researcher ADK agent, which calls the Parallel tool at runtime
    (sol.md §25) — same downstream integrity/policy. Missing a key falls back to
    the mock for that stage, so a partial-credential setup still runs.
    """
    cfg = Config.from_env()

    if prefer_live and cfg.gemini_api_key:
        from studioclear.providers.gemini import GeminiLLMProvider

        llm: LLMProvider = GeminiLLMProvider()
    else:
        llm = MockLLMProvider()

    if prefer_live and use_adk and cfg.gemini_api_key and cfg.parallel_api_key:
        from studioclear.providers.adk_search import ADKSearchProvider

        search: SearchProvider = ADKSearchProvider()
    elif prefer_live and cfg.parallel_api_key:
        from studioclear.providers.parallel import ParallelSearchProvider

        search = ParallelSearchProvider()
    else:
        search = MockSearchProvider()

    return Providers(llm=llm, search=search)


class LiveKeysMissing(RuntimeError):
    """Live mode requested but a required provider key is absent (sol.md §12).
    The caller must surface this, never silently fall back to mock fixtures."""


def build_providers_for_mode(mode: str, use_adk: bool = False) -> Providers:
    """Explicit provider selection with NO silent fallback (sol.md §10/§12).

    mode="example" → deterministic mocks (labeled Simulated example in the UI).
    mode="live"    → real Gemini + Parallel; raises LiveKeysMissing if a key is
    absent so user material is never quietly analyzed by fixtures.
    """
    if mode == "example":
        return build_example_providers()
    if mode == "live":
        cfg = Config.from_env()
        missing = [n for n, v in (("GEMINI_API_KEY", cfg.gemini_api_key),
                                  ("PARALLEL_API_KEY", cfg.parallel_api_key)) if not v]
        if missing:
            raise LiveKeysMissing(", ".join(missing))
        return build_providers(prefer_live=True, use_adk=use_adk)
    raise ValueError(f"unknown provider mode: {mode!r}")


def describe_providers(p: Providers) -> dict:
    """Human-readable which-is-live summary (for /healthz and CLI banners)."""
    return {
        "llm": type(p.llm).__name__,
        "search": type(p.search).__name__,
    }
