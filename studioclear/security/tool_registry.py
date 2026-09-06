"""Approved Tool Registry (sol.md §15 / §17).

The allow-list of capabilities StudioClear agents may use. Anything not listed
is denied by StudioClear AuthZ. `parallel.search.public_web` is approved;
`unapproved_legal_database.search` is deliberately NOT — that gap is the real
DENY demo (sol.md §17).
"""

from __future__ import annotations

# capability -> the permission an ExecutionContext must carry to use it
APPROVED_TOOLS: dict[str, str] = {
    "parallel.search.public_web": "parallel.search.public_web",
    "evidence.read": "evidence.read",
    "policy.evaluate": "policy.evaluate",
}


def is_approved(capability: str) -> bool:
    return capability in APPROVED_TOOLS


def required_permission(capability: str) -> str | None:
    return APPROVED_TOOLS.get(capability)
