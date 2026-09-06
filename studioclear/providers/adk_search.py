"""ADK-driven search provider (sol.md §8, §25 / E8.1).

Implements the SearchProvider protocol by running the Researcher ADK agent,
which calls the `parallel_search` tool at runtime. Evidence URLs are pulled from
the tool-response events — not the agent's free text — so the integrity
invariant holds. This is how the pipeline runs "agentically" (ADK orchestrates
the real Parallel call) with no change to downstream policy/integrity code.
"""

from __future__ import annotations

from studioclear.agents.adk_runtime import (
    bootstrap_adk_env,
    extract_tool_responses,
    run_agent_sync,
)
from studioclear.agents.researcher import build_researcher
from studioclear.models import ClearanceItem


class ADKSearchProvider:
    def __init__(self):
        bootstrap_adk_env()
        self.agent = build_researcher()

    def search(self, query: str, item: ClearanceItem) -> list[dict]:
        message = (
            f"Research this clearance item and call parallel_search to find "
            f"authoritative, independent sources: '{item.text_span}' "
            f"({item.type.value})."
        )
        events = run_agent_sync(self.agent, message)
        sources: list[dict] = []
        for resp in extract_tool_responses(events, "parallel_search"):
            if isinstance(resp, dict):
                sources.extend(resp.get("sources", []))
        return sources
