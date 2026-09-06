"""ADK agents are real google.adk Agents (sol.md §25/§27) — no network.

Verifies the compliance-lock objects exist and are wired with the right tools.
Skipped where google-adk isn't installed (e.g. the minimal CI env). The live
tool-calling path is covered by scripts/smoke_adk.py and demo/adk_run.json.
"""

import os

import pytest

pytest.importorskip("google.adk")

# Building an Agent needs no network, but our builders read a model id from
# config; ensure a placeholder key so config is happy in a clean env.
os.environ.setdefault("GOOGLE_API_KEY", "test-key")

from google.adk.agents import Agent  # noqa: E402

from studioclear.agents.research_planner import build_planner  # noqa: E402
from studioclear.agents.researcher import build_researcher  # noqa: E402
from studioclear.agents.reviewer import build_reviewer  # noqa: E402


def test_three_agents_are_real_adk_agents():
    planner, researcher, reviewer = build_planner(), build_researcher(), build_reviewer()
    for a in (planner, researcher, reviewer):
        assert isinstance(a, Agent)
    assert planner.name == "research_planner"
    assert researcher.name == "researcher"
    assert reviewer.name == "reviewer"


def test_researcher_has_parallel_search_tool():
    researcher = build_researcher()
    tool_names = [getattr(t, "name", getattr(t, "__name__", "")) for t in researcher.tools]
    assert any("parallel_search" in n for n in tool_names)


def test_reviewer_has_apply_policy_tool():
    reviewer = build_reviewer()
    tool_names = [getattr(t, "name", getattr(t, "__name__", "")) for t in reviewer.tools]
    assert any("apply_policy" in n for n in tool_names)
