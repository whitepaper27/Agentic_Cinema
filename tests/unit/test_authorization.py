"""StudioClear AuthZ + the real DENY path (sol.md §15 / §17)."""

from studioclear.models import Decision, ExecutionContext
from studioclear.security.authorization import audit_event_for, decide


def _ctx(perms, tool="parallel_search"):
    return ExecutionContext(
        subject_id="producer_123", script_id="demo_script_001",
        agent_id="research_agent", run_id="run_009", tool=tool, action="search",
        permissions=perms,
    )


def test_approved_tool_with_permission_allows():
    r = decide(_ctx(["parallel.search.public_web"]), "parallel.search.public_web")
    assert r.allowed and r.decision is Decision.ALLOW


def test_unapproved_tool_denies():
    # The real DENY demo: an unregistered legal database (sol.md §17).
    r = decide(_ctx(["parallel.search.public_web"]), "unapproved_legal_database.search")
    assert not r.allowed
    assert r.reason == "tool_not_authorized"


def test_missing_permission_denies():
    r = decide(_ctx([]), "parallel.search.public_web")
    assert r.decision is Decision.DENY and r.reason == "missing_permission"


def test_deny_produces_audit_row():
    ctx = _ctx(["parallel.search.public_web"])
    r = decide(ctx, "unapproved_legal_database.search")
    event = audit_event_for(ctx, "unapproved_legal_database.search", r)
    assert event["decision"] == "DENY"
    assert event["reason"] == "tool_not_authorized"
    assert event["run_id"] == "run_009"
