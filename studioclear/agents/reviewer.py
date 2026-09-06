"""Reviewer / Policy — ADK agent (sol.md §8). Applies the deterministic policy
evaluator and checks evidence requirements. Cannot grant final legal clearance
(sol.md §14) — that authority does not exist by design."""

from __future__ import annotations

# from google.adk.agents import Agent
# from studioclear.contract.policy_evaluator import evaluate

REVIEWER_INSTRUCTION = (
    "For each item, apply the studio policy to the evidence and produce a "
    "CLEAR / REVIEW / ESCALATE / INSUFFICIENT_EVIDENCE recommendation with the "
    "policy basis. You never issue legal clearance; humans decide."
)


def build_reviewer():  # pragma: no cover - stub
    """STUB. Thin ADK wrapper that calls the pure evaluate() for determinism."""
    raise NotImplementedError("Wire the ADK reviewer agent on the Day-2 build.")
