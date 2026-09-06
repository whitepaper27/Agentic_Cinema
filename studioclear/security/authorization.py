"""StudioClear AuthZ (sol.md §15–§17).

Domain/tool decision: *can this agent use this capability for this run?*
Separate from Cloud IAM (which decides whether a service identity can reach a
resource). Authority only ever shrinks (sol.md §16):

    EffectiveAccess = User ∩ Script ∩ Agent ∩ Tool ∩ CloudIAM ∩ StudioPolicy

`decide()` is pure and unit-tested (tests/unit/test_authorization.py). The real
DENY path (sol.md §17) is: unapproved capability -> DENY -> audit row -> planner
replans with Parallel.
"""

from __future__ import annotations

from dataclasses import dataclass

from studioclear.models import Decision, ExecutionContext
from studioclear.security import tool_registry


@dataclass(frozen=True)
class AuthzResult:
    decision: Decision
    reason: str

    @property
    def allowed(self) -> bool:
        return self.decision is Decision.ALLOW


def decide(ctx: ExecutionContext, capability: str) -> AuthzResult:
    """Allow only if the capability is registry-approved AND the context carries
    the required permission. Pure — no side effects, deterministic."""

    if not tool_registry.is_approved(capability):
        return AuthzResult(Decision.DENY, "tool_not_authorized")

    needed = tool_registry.required_permission(capability)
    if needed is not None and needed not in ctx.permissions:
        return AuthzResult(Decision.DENY, "missing_permission")

    return AuthzResult(Decision.ALLOW, "approved")


def audit_event_for(ctx: ExecutionContext, capability: str, result: AuthzResult) -> dict:
    """Shape the audit row for an authorization decision (sol.md §17/§19)."""
    return {
        "run_id": ctx.run_id,
        "script_id": ctx.script_id,
        "agent_id": ctx.agent_id,
        "action": "authorize",
        "tool": capability,
        "decision": result.decision.value,
        "reason": result.reason,
    }
