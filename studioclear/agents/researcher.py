"""Researcher — a real google.adk Agent (sol.md §8, §25).

Given a clearance item, it calls the `parallel_search` tool to gather
source-cited evidence. The URLs are read from the tool response downstream, so
the agent never fabricates citations (sol.md E8.1).
"""

from __future__ import annotations

from studioclear.agents.tools import parallel_search
from studioclear.config import Config

RESEARCHER_INSTRUCTION = (
    "You are StudioClear's research agent. For the given clearance item, call "
    "parallel_search with a focused, factual query to find authoritative, "
    "independent sources. Prefer primary/official sources. After the tool "
    "returns, briefly summarize what the sources establish. Never write a URL "
    "yourself — only the tool provides sources."
)


def build_researcher():
    """Return the researcher ADK Agent (parallel_search tool attached)."""
    from google.adk.agents import Agent

    return Agent(
        name="researcher",
        model=Config.from_env().normalizer_model,  # gemini-2.5-flash
        instruction=RESEARCHER_INSTRUCTION,
        tools=[parallel_search],
    )
