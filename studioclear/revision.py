"""Revision and recheck loop (sol.md §8).

Layered on a saved run + scene. A proposal never mutates the scene; acceptance
creates a new immutable scene version, applies the edit to the canonical text
(and the affected claim), and marks prior findings stale; recheck re-researches
the changed version and reports claim lineage. Exact locks are enforced in code,
outside the model. The model returns text + source IDs only — it cannot cite a
URL or silently unlock protected text.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from studioclear.providers.base import Providers
from studioclear.research_pipeline import run_research


def _lineage_key(text: str) -> str:
    """Identity for claim lineage across an edit: the claim minus digits, so a
    year correction reads as a MODIFIED claim, not an unrelated new/removed one."""
    return re.sub(r"\s+", " ", re.sub(r"\d", " ", (text or "").lower())).strip()

_NO_EVIDENCE_STATUSES = {"UNRESOLVED", "NOT_RESEARCHED", "STALE"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _find(run: dict, finding_id: str) -> dict | None:
    return next((f for f in run.get("findings", []) if f["finding_id"] == finding_id), None)


def _scene_text_for(scene: dict, scene_no: int) -> str:
    version = scene["versions"][-1]
    for s in version["scenes"]:
        if s.get("scene") == scene_no and s.get("text"):
            return s["text"]
    # Fall back to the whole confirmed transcript if pages aren't per-scene text.
    return "\n\n".join(s.get("text", "") for s in version["scenes"])


def propose(run: dict, scene: dict, finding_id: str, providers: Providers) -> dict:
    """Build an evidence-backed proposal without mutating the scene (sol.md §8)."""
    finding = _find(run, finding_id)
    if finding is None:
        raise KeyError(finding_id)
    if finding["research_status"] in _NO_EVIDENCE_STATUSES:
        # Do not propose a factual correction when evidence is not applicable.
        raise ValueError("no_applicable_evidence")

    version = scene["versions"][-1]
    scene_text = _scene_text_for(scene, finding["scene"])
    raw = providers.llm.propose_revision(
        scene_text, finding["text_span"], finding.get("evidence", []),
        scene.get("instruction", ""), version.get("locks", []),
    )
    original = raw.get("original_text", "")
    proposed = raw.get("proposed_text", "")
    if not original or original not in scene_text:
        raise ValueError("original_not_in_scene")

    known_ids = {s["source_id"] for s in run.get("sources", [])}
    evidence_ids = [sid for sid in raw.get("evidence_source_ids", []) if sid in known_ids]
    # Evidence is referenced by (origin_run_id, source_id) so a later recheck can
    # never reinterpret a source id from a different run (sol.md §8).
    evidence_refs = [{"origin_run_id": run["run_id"], "source_id": sid}
                     for sid in evidence_ids]

    # Exact-lock enforcement (code, not the model): a locked span present in the
    # scene must still be present after the edit.
    result = scene_text.replace(original, proposed, 1)
    conflict = next((lk for lk in version.get("locks", [])
                     if lk and lk in scene_text and lk not in result), None)

    rev = {
        "revision_id": f"REV-{len(run.get('revisions', [])) + 1:03d}",
        "finding_id": finding_id,
        "item_id": finding["item_id"],
        "scene": finding["scene"],
        "base_scene_version": scene["current_version"],
        "original_text": original,
        "proposed_text": proposed,
        "rationale": raw.get("rationale", ""),
        "evidence_source_ids": evidence_ids,
        "evidence_refs": evidence_refs,
        "art_change": raw.get("art_change", ""),
        "status": "conflict" if conflict else "proposed",
        "conflict_span": conflict,
        "created_at": _now(),
    }
    run.setdefault("revisions", []).append(rev)
    return rev


def decide(
    run: dict, scene: dict, revision_id: str, action: str, *,
    expected_version: int | None = None, idempotency_key: str | None = None,
) -> dict:
    """Accept or reject a proposal (sol.md §8). Accept creates a new scene
    version, applies the edit, and marks prior findings stale."""
    rev = next((r for r in run.get("revisions", []) if r["revision_id"] == revision_id), None)
    if rev is None:
        raise KeyError(revision_id)

    if action == "reject":
        rev["status"] = "rejected"
        rev["decided_at"] = _now()
        return {"revision": rev}
    if action != "accept":
        raise ValueError(f"unknown action: {action}")

    # Idempotent replay: same key on an already-accepted revision → no new version.
    if rev["status"] == "accepted" and idempotency_key and \
            rev.get("idempotency_key") == idempotency_key:
        return {"revision": rev, "scene_version": rev["result_scene_version"]}

    if rev["status"] == "conflict":
        raise ValueError("lock_conflict")
    current = scene["current_version"]
    if expected_version is not None and expected_version != current:
        raise ValueError("stale_version")
    if rev["base_scene_version"] != current:
        raise ValueError("stale_version")

    base = scene["versions"][-1]
    original, proposed = rev["original_text"], rev["proposed_text"]

    new_scenes = [dict(s) for s in base["scenes"]]
    for s in new_scenes:
        if s.get("scene") == rev["scene"] and original in s.get("text", ""):
            s["text"] = s["text"].replace(original, proposed, 1)

    new_items = [dict(it) for it in base["items"]]
    for it in new_items:
        if it["item_id"] == rev["item_id"]:
            it["text_span"] = (it["text_span"].replace(original, proposed, 1)
                               if original in it["text_span"] else proposed)

    new_version = current + 1
    scene["versions"].append({
        "version": new_version,
        "parent_version": current,
        "created_at": _now(),
        "scenes": new_scenes,
        "items": new_items,
        "instruction": base["instruction"],
        "locks": base["locks"],
    })
    scene["current_version"] = new_version

    # Prior findings belong to the old version; mark them stale but keep the
    # pre-stale status so recheck can report before/after honestly.
    for f in run.get("findings", []):
        f.setdefault("prior_status", f["research_status"])
        f["research_status"] = "STALE"
    run["stale"] = True

    rev["status"] = "accepted"
    rev["decided_at"] = _now()
    rev["result_scene_version"] = new_version
    rev["idempotency_key"] = idempotency_key
    return {"revision": rev, "scene_version": new_version}


def recheck(scene: dict, providers: Providers, prior_run: dict, run_id: str,
            provider_mode: str = "mock") -> dict:
    """Re-EXTRACT the changed scene and re-research it, reporting claim lineage.

    Reusing the saved item list is not a recheck (sol.md §8): a claim added only to
    the canonical text must be discovered. Claims are matched to the prior run by a
    digit-stripped lineage key so a year correction reads as modified, and status is
    truthful — a skipped/failed claim keeps the recheck incomplete, never silently
    'complete'.
    """
    version = scene["versions"][-1]
    fresh_items = providers.llm.extract_items(version["scenes"])
    new_run = run_research(
        fresh_items, providers, run_id=run_id, scene_id=scene["scene_id"],
        scene_version=scene["current_version"], provider_mode=provider_mode,
    )

    prior_by_key: dict[str, dict] = {}
    for f in prior_run.get("findings", []):
        prior_by_key.setdefault(_lineage_key(f["text_span"]), f)

    matched, retained, modified, added, changes = set(), [], [], [], []
    for nf in new_run["findings"]:
        key = _lineage_key(nf["text_span"])
        pf = prior_by_key.get(key)
        if pf is None:
            added.append(nf["item_id"])
            continue
        matched.add(key)
        before = pf.get("prior_status", pf["research_status"])
        if nf["text_span"] != pf["text_span"] or nf["research_status"] != before:
            modified.append(nf["item_id"])
            changes.append({
                "item_id": nf["item_id"],
                "text_before": pf["text_span"], "text_after": nf["text_span"],
                "status_before": before, "status_after": nf["research_status"],
            })
        else:
            retained.append(nf["item_id"])
    removed = [pf["item_id"] for k, pf in prior_by_key.items() if k not in matched]
    skipped = [f["item_id"] for f in new_run["findings"]
               if f["research_status"] == "NOT_RESEARCHED"]

    # Carry the accepted-revision history forward so the handoff reflects the
    # decisions that produced this version (sol.md §10).
    new_run["revisions"] = prior_run.get("revisions", [])
    new_run["instruction"] = prior_run.get("instruction", "")
    new_run["recheck"] = {
        "before_run": prior_run["run_id"],
        "rechecked_version": scene["current_version"],
        "retained": retained, "modified": modified, "added": added,
        "removed": removed, "skipped": skipped, "changes": changes,
        # 'complete' means the operation finished; it never implies all supported.
        "status": "complete" if not skipped else "incomplete",
    }
    return new_run
