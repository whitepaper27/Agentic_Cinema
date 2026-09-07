"""Schema-v2 research pipeline (sol.md §6, §7, §13).

Research a confirmed scene's items into findings: authorize each tool call, run
Parallel search, register raw sources with immutable server-side IDs, have the
model classify passages against the exact claim, then let CODE resolve the
references and deterministically map them to a research status. Human routing is
a separate field. No source-count verdicts, no confidence percentages.

Additive to the legacy `pipeline.run_pipeline`, which is retained for the labeled
legacy demo (sol.md §9).
"""

from __future__ import annotations

from studioclear.agents.research_planner import item_query, plan_batches
from studioclear.contract.policy_evaluator import (
    assess_research_status,
    route_for_type,
)
from studioclear.models import ClearanceItem, ExecutionContext, ResearchStatus, Source
from studioclear.providers.base import Providers
from studioclear.research.evidence_normalizer import resolve_assessments
from studioclear.security.audit import AuditLog
from studioclear.security.authorization import audit_event_for, decide

# The unapproved capability used for the authorization self-test (sol.md §11).
UNAPPROVED_TOOL = "unapproved_legal_database.search"
APPROVED_TOOL = "parallel.search.public_web"

# Default studio research policy: corroboration needs two independent sources.
DEFAULT_RESEARCH_POLICY = {"factual": {"minimum_corroborating_sources": 2}}


def run_research(
    items: list[ClearanceItem],
    providers: Providers,
    policy: dict | None = None,
    now: str = "2026-09-05T12:00:00Z",
    run_id: str = "run_demo",
    scene_id: str = "scene_demo",
    scene_version: int = 1,
    subject_id: str = "producer_123",
    max_findings: int | None = None,
    provider_mode: str = "mock",
) -> dict:
    """Produce a schema-v2 research report over already-confirmed items."""
    policy = policy or DEFAULT_RESEARCH_POLICY
    audit = AuditLog()
    audit.append({"action": "research_started", "scene_id": scene_id,
                  "scene_version": scene_version, "items": len(items)})

    batches = plan_batches(items)
    for b in batches:
        audit.append({"action": "batch_created", "batch": b.name, "items": len(b.item_ids)})

    ctx = ExecutionContext(
        subject_id=subject_id, script_id=scene_id, agent_id="research_agent",
        run_id=run_id, tool="parallel_search", action="search",
        permissions=[APPROVED_TOOL], risk_tier="research",
    )

    # Authorization self-test: a deliberately unapproved capability is denied at
    # the tool boundary. Labeled as a self-test, excluded from incident counts.
    self_test = decide(ctx, UNAPPROVED_TOOL)
    ev = audit_event_for(ctx, UNAPPROVED_TOOL, self_test)
    ev["self_test"] = True
    audit.append(ev)

    sources_registry: list[dict] = []
    findings: list[dict] = []
    sid_counter = 0

    for idx, item in enumerate(items):
        query = item_query(item)

        researched = max_findings is None or idx < max_findings
        if not researched:
            findings.append(_finding(item, query, ResearchStatus.NOT_RESEARCHED,
                                     [], [], reason="run limit reached"))
            audit.append({"action": "research_skipped", "item_id": item.item_id,
                          "reason": "budget"})
            continue

        allow = decide(ctx, APPROVED_TOOL)
        audit.append(audit_event_for(ctx, APPROVED_TOOL, allow))
        raw = providers.search.search(query, item) if allow.allowed else []

        # Register raw sources with immutable server-side IDs (sol.md §7).
        item_sources: list[Source] = []
        for r in raw:
            sid_counter += 1
            src = Source(
                source_id=f"S{sid_counter:03d}",
                url=r.get("source_url", ""),
                title=r.get("title", ""),
                passages=[r["excerpt"]] if r.get("excerpt") else [],
                query=query,
                retrieved_at=now,
                operation_id=run_id,
                independence="unknown",   # honest default; not proven from hostnames
            )
            item_sources.append(src)
        sources_registry.extend(s.model_dump() for s in item_sources)
        audit.append({"action": "sources_registered", "item_id": item.item_id,
                      "count": len(item_sources)})

        # The model classifies passages; CODE resolves and grades them.
        raw_assessments = providers.llm.assess_claim(item.text_span, item_sources)
        validated, dropped = resolve_assessments(raw_assessments, item_sources)
        if dropped:
            audit.append({"action": "assessments_dropped", "item_id": item.item_id,
                          "count": len(dropped)})
        status = assess_research_status(validated, policy)
        audit.append({"action": "claim_assessed", "item_id": item.item_id,
                      "status": status.value})

        findings.append(_finding(item, query, status, validated,
                                 [s.source_id for s in item_sources]))

    audit.append({"action": "report_generated"})

    summary: dict[str, int] = {}
    for f in findings:
        summary[f["research_status"]] = summary.get(f["research_status"], 0) + 1

    return {
        "schema_version": 2,
        "run_id": run_id,
        "scene_id": scene_id,
        "scene_version": scene_version,
        "policy_version": "demo_research_policy_v1",
        "provider_mode": provider_mode,
        "generated_at": now,
        "batches": [{"name": b.name, "items": b.item_ids} for b in batches],
        "findings": findings,
        "sources": sources_registry,
        "summary": summary,
        "governance": {
            "unauthorized_blocked": 0,          # the denial is a self-test, not an incident
            "self_test_denied": not self_test.allowed,
            "audit_events": len(audit.events),
            "audit_verified": audit.verify(),
            "audit_head": audit.head,
        },
        "audit_chain": audit.to_list(),
    }


def _finding(item, query, status, validated, source_ids, reason: str = ""):
    return {
        "finding_id": f"F-{item.item_id}",
        "item_id": item.item_id,
        "scene": item.scene,
        "type": item.type.value,
        "text_span": item.text_span,
        "context": item.context,
        "query": query,
        "research_status": status.value,
        "routing": route_for_type(item.type).value,
        "evidence": [a.model_dump() for a in validated],
        "source_ids": source_ids,
        "limitations": reason,
        "human_decision": None,
    }
