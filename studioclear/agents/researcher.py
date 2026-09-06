"""Researcher — ADK agent (sol.md §8). Calls the approved parallel_search tool
and returns normalized, source-cited evidence. Never invents sources (E8.1)."""

from __future__ import annotations

# from google.adk.agents import Agent
# from studioclear.research.parallel_client import parallel_search

RESEARCHER_INSTRUCTION = (
    "Given clearance items, call parallel_search and return normalized, "
    "source-cited evidence. Every source_url must come from the tool result; "
    "never write a URL yourself."
)


def build_researcher():  # pragma: no cover - stub
    """STUB. return Agent(name='researcher', model='gemini-2.5-flash',
    instruction=RESEARCHER_INSTRUCTION, tools=[parallel_search])."""
    raise NotImplementedError("Wire the ADK researcher agent on the Day-1 build.")
