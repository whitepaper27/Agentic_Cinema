"""Sanitized production handoff export (sol.md §9, sol_ui.md §10).

An allowlisted schema — NOT a dump of the internal run object. It carries the
deliverable (original + accepted scene text, decisions, evidence references, source
records, recheck lineage, unresolved work, pending art notes, expiry) and
EXCLUDES owner, session identifiers, cookies, internal authorization context, and
raw audit hashes. Evidence is referenced as {origin_run_id, source_id} so a later
recheck cannot reinterpret a source id from a different run.
"""

from __future__ import annotations

from datetime import datetime, timezone

_OPEN = {"CONTRADICTED", "MIXED", "UNRESOLVED", "STALE", "NOT_RESEARCHED"}


def _text(version: dict) -> str:
    return "\n\n".join(s.get("text", "") for s in version.get("scenes", []))


def build_comparison_handoff(comp: dict, scene: dict) -> dict:
    """Sanitized production planning brief (sol.md §9). Allowlisted — no owner or
    session. Estimate status is separate from scene review; a comparison against an
    older scene version is Stale."""
    versions = scene.get("versions", [])
    current = versions[-1]
    stale = comp.get("scene_version") != scene.get("current_version")
    status = ("Stale comparison" if stale else comp.get("estimate_status", "incomplete estimate"))
    decision = comp.get("decision")
    return {
        "schema": "studioclear.planning_brief.v1",
        "handoff_id": f"{comp['comparison_id']}:{scene.get('current_version')}",
        "comparison_id": comp["comparison_id"],
        "parent_comparison_id": comp.get("parent_comparison_id"),
        "calculation_version": comp.get("calculation_version"),
        "scene_id": scene.get("scene_id"),
        "scene_version": scene.get("current_version"),
        "comparison_scene_version": comp.get("scene_version"),
        "title": scene.get("title", ""),
        "provider_mode": comp.get("provider_mode"),
        "simulated": comp.get("provider_mode") == "example",
        "estimate_status": status,
        "stale": stale,
        "reporting_currency": comp.get("reporting_currency"),
        "brief": comp.get("brief", {}),
        "options": comp.get("options", []),
        "recommendation": comp.get("recommendation"),
        "selected": decision,
        "sources": comp.get("sources", []),
        "scene_text": "\n\n".join(s.get("text", "") for s in current.get("scenes", [])),
        "instruction": current.get("instruction", ""),
        "expires_at": scene.get("expires_at"),
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }


def build_handoff(run: dict, scene: dict,
                  historical_runs: dict[str, dict] | None = None) -> dict:
    """Return the sanitized, shareable handoff for a run + its scene.

    `historical_runs` maps run_id → run for earlier runs whose sources are cited by
    accepted revisions, so those citations still resolve after a recheck swapped the
    current run (sol.md §9). Every exported evidence reference is validated to
    resolve to exactly one included source."""
    versions = scene.get("versions", [])
    first, current = versions[0], versions[-1]
    origin = run.get("run_id")
    historical_runs = historical_runs or {}

    accepted = [r for r in run.get("revisions", []) if r.get("status") == "accepted"]
    accepted_changes = [{
        "revision_id": r["revision_id"],
        "item_id": r["item_id"],
        "scene": r["scene"],
        "original_text": r["original_text"],
        "proposed_text": r["proposed_text"],
        "rationale": r.get("rationale", ""),
        "evidence": r.get("evidence_refs", []),          # [{origin_run_id, source_id}]
        "art_change": r.get("art_change", ""),
    } for r in accepted]

    decisions = [{
        "finding_id": f["finding_id"], "item_id": f["item_id"],
        "action": f["human_decision"].get("action"),
        "note": f["human_decision"].get("note", ""),
        "at": f["human_decision"].get("at"),
    } for f in run.get("findings", []) if f.get("human_decision")]

    unresolved = [{
        "finding_id": f["finding_id"], "claim": f["text_span"],
        "scene": f["scene"], "research_status": f["research_status"],
    } for f in run.get("findings", []) if f["research_status"] in _OPEN]

    art_notes = [{"item_id": r["item_id"], "art_change": r["art_change"]}
                 for r in accepted if r.get("art_change")]

    # Union of current-run sources and every historical run cited by an accepted
    # revision, keyed by {origin_run_id, source_id} and de-duplicated.
    sources: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for oid, r in [(origin, run), *historical_runs.items()]:
        for s in r.get("sources", []):
            key = (oid, s["source_id"])
            if key in seen:
                continue
            seen.add(key)
            sources.append({
                "source_id": s["source_id"], "origin_run_id": oid,
                "url": s.get("url", ""), "title": s.get("title", ""),
                "passages": s.get("passages", []), "query": s.get("query", ""),
                "retrieved_at": s.get("retrieved_at", ""),
                "independence": s.get("independence", "unknown"),
            })

    # Validate every accepted-change evidence reference resolves to one source.
    resolvable = {(s["origin_run_id"], s["source_id"]) for s in sources}
    unresolved_refs = [ref for c in accepted_changes for ref in c["evidence"]
                       if (ref.get("origin_run_id"), ref.get("source_id")) not in resolvable]

    # Production handoff ONLY for a completed recheck of the CURRENT version. An
    # absent / pending / failed / stale-version recheck stays incomplete (sol.md §9).
    rc = run.get("recheck")
    if not accepted:
        label = "Research draft"
    elif (rc and rc.get("status") == "complete"
          and rc.get("rechecked_version") == scene.get("current_version")):
        label = "Production handoff"
    else:
        label = "Accepted revision - recheck incomplete"

    return {
        "schema": "studioclear.handoff.v1",
        "handoff_id": f"{origin}:{scene.get('current_version')}",
        "run_id": origin,
        "scene_id": scene.get("scene_id"),
        "scene_version": scene.get("current_version"),
        "label": label,
        "title": scene.get("title", ""),
        "provider_mode": run.get("provider_mode"),
        "simulated": run.get("provider_mode") == "example",
        "policy_version": run.get("policy_version"),
        "expires_at": scene.get("expires_at"),
        "instruction": current.get("instruction", ""),
        "protected_spans": current.get("locks", []),
        "scene": {
            "current_version": scene.get("current_version"),
            "original_text": _text(first),
            "accepted_text": _text(current),
            "version_lineage": [{"version": v["version"],
                                 "parent_version": v.get("parent_version"),
                                 "created_at": v.get("created_at")} for v in versions],
        },
        "accepted_changes": accepted_changes,
        "decisions": decisions,
        "recheck": run.get("recheck"),
        "unresolved": unresolved,
        "pending_art_notes": art_notes,
        "sources": sources,
        "references_resolved": not unresolved_refs,
        "unresolved_references": unresolved_refs,
        "exported_at": datetime.now(timezone.utc).isoformat(),  # actual server UTC
    }
