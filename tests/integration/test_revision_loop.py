"""Revision + recheck loop (sol.md §8).

Propose never mutates the scene; accept creates a new version, enforces exact
locks, marks findings stale; recheck reports claim lineage. Uses mock providers.
"""

from collections import defaultdict

import pytest

from studioclear import revision
from studioclear.providers.mock import build_mock_providers
from studioclear.research_pipeline import run_research

APOLLO = "F-CLR-011"      # historical claim, SUPPORTED (nasa primary), contains "1969"
NIKON = "F-CLR-001"       # brand, UNRESOLVED (single secondary source)


def _scene_and_run(locks=None):
    providers = build_mock_providers()
    items = providers.llm.extract_items([])
    by_scene = defaultdict(list)
    for it in items:
        by_scene[it.scene].append(it.text_span)
    scenes = [{"scene": n, "text": " | ".join(spans), "source": "paste"}
              for n, spans in sorted(by_scene.items())]
    scene = {
        "scene_id": "scene_x", "owner": "o", "current_version": 1,
        "title": "T", "instruction": "Check the date; keep everything else.",
        "versions": [{
            "version": 1, "parent_version": None, "scenes": scenes,
            "items": [it.model_dump(mode="json") for it in items],
            "instruction": "Check the date; keep everything else.",
            "locks": locks or [],
        }],
    }
    run = run_research(items, providers, run_id="run_x")
    return providers, scene, run


def test_propose_does_not_mutate_scene():
    providers, scene, run = _scene_and_run()
    rev = revision.propose(run, scene, APOLLO, providers)
    assert rev["status"] == "proposed"
    assert rev["proposed_text"] != rev["original_text"]
    assert scene["current_version"] == 1                 # unchanged
    assert run["revisions"][0]["revision_id"] == rev["revision_id"]


def test_propose_blocked_when_evidence_unresolved():
    providers, scene, run = _scene_and_run()
    with pytest.raises(ValueError, match="no_applicable_evidence"):
        revision.propose(run, scene, NIKON, providers)


def test_accept_creates_version_and_marks_findings_stale():
    providers, scene, run = _scene_and_run()
    rev = revision.propose(run, scene, APOLLO, providers)
    out = revision.decide(run, scene, rev["revision_id"], "accept",
                          expected_version=1, idempotency_key="k1")
    assert out["scene_version"] == 2
    assert scene["current_version"] == 2
    assert all(f["research_status"] == "STALE" for f in run["findings"])
    # The canonical scene text actually changed.
    v2 = scene["versions"][-1]
    assert any("1968" in s["text"] for s in v2["scenes"])


def test_reject_keeps_scene_and_records_decision():
    providers, scene, run = _scene_and_run()
    rev = revision.propose(run, scene, APOLLO, providers)
    out = revision.decide(run, scene, rev["revision_id"], "reject")
    assert out["revision"]["status"] == "rejected"
    assert scene["current_version"] == 1


def test_locked_span_conflict_blocks_edit():
    # Lock the exact token the correction would change.
    providers, scene, run = _scene_and_run(locks=["1969"])
    rev = revision.propose(run, scene, APOLLO, providers)
    assert rev["status"] == "conflict"
    assert rev["conflict_span"] == "1969"
    with pytest.raises(ValueError, match="lock_conflict"):
        revision.decide(run, scene, rev["revision_id"], "accept", expected_version=1)


def test_stale_version_accept_conflicts():
    providers, scene, run = _scene_and_run()
    rev = revision.propose(run, scene, APOLLO, providers)
    scene["current_version"] = 5      # someone else advanced the scene
    with pytest.raises(ValueError, match="stale_version"):
        revision.decide(run, scene, rev["revision_id"], "accept", expected_version=5)


def test_idempotent_accept_creates_no_duplicate_version():
    providers, scene, run = _scene_and_run()
    rev = revision.propose(run, scene, APOLLO, providers)
    revision.decide(run, scene, rev["revision_id"], "accept",
                    expected_version=1, idempotency_key="k9")
    revision.decide(run, scene, rev["revision_id"], "accept",
                    expected_version=1, idempotency_key="k9")
    assert scene["current_version"] == 2      # not 3


def test_recheck_reports_modified_claim_lineage():
    providers, scene, run = _scene_and_run()
    rev = revision.propose(run, scene, APOLLO, providers)
    revision.decide(run, scene, rev["revision_id"], "accept", expected_version=1)
    new_run = revision.recheck(scene, providers, run, run_id="run_recheck")
    rc = new_run["recheck"]
    assert rc["status"] == "complete"
    assert "CLR-011" in rc["modified"]         # the corrected claim was rechecked
    assert "CLR-011" not in rc["retained"]
