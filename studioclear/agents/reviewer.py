"""Reviewer / Policy — a real google.adk Agent (sol.md §8, §25).

Applies the studio policy to an item's evidence by calling the deterministic
`apply_policy` tool, and explains the recommendation. It cannot grant final
legal clearance (sol.md §14) — that authority does not exist by design, and the
triage state comes from the tool (code), never the model.
"""

from __future__ import annotations

from studioclear.agents.tools import apply_policy
from studioclear.config import Config

REVIEWER_INSTRUCTION = (
    "You are StudioClear's reviewer. For each item, call apply_policy with the "
    "item type and its independent source count to get the deterministic triage "
    "state, then explain the recommendation and its policy basis in one sentence. "
    "You never issue legal clearance; humans decide."
)


def build_reviewer():
    """Return the reviewer ADK Agent (apply_policy tool attached)."""
    from google.adk.agents import Agent

    return Agent(
        name="reviewer",
        model=Config.from_env().normalizer_model,  # gemini-2.5-flash
        instruction=REVIEWER_INSTRUCTION,
        tools=[apply_policy],
    )
