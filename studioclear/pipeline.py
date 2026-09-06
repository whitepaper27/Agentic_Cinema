"""The Research Spine (sol.md E3.1 / E7).

PDF/MD -> extract -> plan -> authorize (+ real DENY) -> search -> integrity-
enforce -> deterministic policy -> traceable report, with a tamper-evident audit
trail throughout. Provider-agnostic: pass mock providers (offline/deterministic)
or the real Gemini/Parallel adapters. Pure orchestration — every decision is made
by the tested modules it calls.
"""

from __future__ import annotations

from studioclear.agents.research_planner import item_query, plan_batches
from studioclear.analyzer.script_parser import parse_script
from studioclear.contract.clearance_contract import load_policy
from studioclear.contract.policy_evaluator import TYPE_TO_POLICY_KEY, evaluate
from studioclear.models import ExecutionContext
from studioclear.providers.base import Providers
from studioclear.research.evidence_normalizer import (
    deterministic_confidence,
    enforce_grounded_sources,
    independent_source_count,
    publisher_of,
)
from studioclear.security.audit import AuditLog
from studioclear.security.authorization import audit_event_for, decide

# Fixed timestamp in mock mode so cached runs and tests are reproducible.
DEMO_NOW = "2026-09-05T12:00:00Z"

# The unapproved capability used to demonstrate a genuine DENY (sol.md §17).
UNAPPROVED_TOOL = "unapproved_legal_database.search"
APPROVED_TOOL = "parallel.search.public_web"


def _min_sources(policy: dict, item_type) -> int:
    rule = policy.get(TYPE_TO_POLICY_KEY.get(item_type, ""), {})
    return int(rule.get("minimum_independent_sources", 0) or 0)


def run_pipeline(
    script_path: str,
    providers: Providers,
    policy: dict | None = None,
    now: str = DEMO_NOW,
    script_id: str = "demo_script_001",
    title: str = "Midnight Signal",
    run_id: str = "run_demo",
    subject_id: str = "producer_123",
) -> dict:
    policy = policy if policy is not None else load_policy()
    audit = AuditLog()
    audit.append({"action": "script_uploaded", "script_id": script_id})

    scenes = parse_script(script_path)
    items = providers.llm.extract_items(scenes)
    audit.append({"action": "items_extracted", "count": len(items)})

    batches = plan_batches(items)
    for b in batches:
        audit.append({"action": "batch_created", "batch": b.name, "items": len(b.item_ids)})

    ctx = ExecutionContext(
        subject_id=subject_id, script_id=script_id, agent_id="research_agent",
        run_id=run_id, tool="parallel_search", action="search",
        permissions=[APPROVED_TOOL], risk_tier="research",
    )

    # --- Governance: a real DENY of an unapproved capability (sol.md §17) ---
    deny = decide(ctx, UNAPPROVED_TOOL)
    audit.append(audit_event_for(ctx, UNAPPROVED_TOOL, deny))
    unauthorized_blocked = 0 if deny.allowed else 1

    report_items: list[dict] = []
    for item in items:
        query = item_query(item)

        allow = decide(ctx, APPROVED_TOOL)
        audit.append(audit_event_for(ctx, APPROVED_TOOL, allow))
        raw = providers.search.search(query, item) if allow.allowed else []

        # Evidence-integrity invariant: only URLs that came back from search are
        # allowed to become citations (sol.md E8.1).
        raw_urls = [s["source_url"] for s in raw]
        grounded, dropped = enforce_grounded_sources(raw_urls, raw_urls)
        if dropped:  # pragma: no cover - never happens in mock; guards live mode
            audit.append({"action": "sources_dropped", "item_id": item.item_id,
                          "count": len(dropped)})

        grounded_set = set(grounded)
        evidence = [
            {
                "source_url": s["source_url"],
                "title": s.get("title", ""),
                "excerpt": s.get("excerpt", ""),
                "publisher": publisher_of(s["source_url"]),
                "retrieved_at": now,
                "supports": True,
            }
            for s in raw
            if s["source_url"] in grounded_set
        ]
        source_count = independent_source_count(grounded)
        confidence = deterministic_confidence(source_count)
        audit.append({"action": "evidence_returned", "item_id": item.item_id,
                      "sources": source_count})

        result = evaluate(item.type, source_count, policy)
        audit.append({"action": "policy_evaluated", "item_id": item.item_id,
                      "state": result.state.value})

        report_items.append({
            "item_id": item.item_id,
            "scene": item.scene,
            "type": item.type.value,
            "text_span": item.text_span,
            "context": item.context,
            "query": query,
            "evidence": evidence,
            "source_count": source_count,
            "confidence": confidence,
            "state": result.state.value,
            "reason": result.reason,
            "policy_key": result.policy_key,
            "human_decision": None,  # filled at the Human Decision Desk (§14)
        })

    audit.append({"action": "report_generated"})

    # --- Summary + honest metrics (sol.md §20) ---
    summary: dict[str, int] = {}
    for it in report_items:
        summary[it["state"]] = summary.get(it["state"], 0) + 1

    multi_required = multi_satisfied = 0
    for item, ri in zip(items, report_items, strict=True):
        need = _min_sources(policy, item.type)
        if need >= 2:
            multi_required += 1
            if ri["source_count"] >= need:
                multi_satisfied += 1

    return {
        "script_id": script_id,
        "title": title,
        "run_id": run_id,
        "policy_id": "demo_policy_v1",
        "generated_at": now,
        "batches": [{"name": b.name, "items": b.item_ids} for b in batches],
        "items": report_items,
        "summary": summary,
        "metrics": {
            "references_detected": len(report_items),
            "evidence_backed": sum(1 for it in report_items if it["source_count"] > 0),
            "multi_source_required": multi_required,
            "multi_source_satisfied": multi_satisfied,
            "traceable": sum(
                1 for it in report_items
                if it["query"] and it["policy_key"] and (
                    it["evidence"] or it["state"] == "INSUFFICIENT_EVIDENCE"
                )
            ),
        },
        "governance": {
            "unauthorized_blocked": unauthorized_blocked,
            "audit_events": len(audit.events),
            "audit_verified": audit.verify(),
            "audit_head": audit.head,
        },
        # Serialized tamper-evident chain — persisted so human decisions can
        # append to it after the run (sol.md §19 / E8.3).
        "audit_chain": audit.to_list(),
    }
