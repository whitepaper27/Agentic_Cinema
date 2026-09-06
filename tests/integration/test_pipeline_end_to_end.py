"""End-to-end spine test (sol.md E3.1 / E5.3).

Runs the full pipeline over the offline mock providers and asserts the sol.md
§20 targets: full recall, correct per-item states, evidence coverage, the real
DENY, and an intact audit chain. This is the Day-1 "done" gate.
"""

import json
from pathlib import Path

from studioclear.evals.metrics import score_extraction
from studioclear.pipeline import run_pipeline
from studioclear.providers import build_mock_providers

EXPECTED = json.loads(Path("demo/expected_items.json").read_text(encoding="utf-8"))


def _run():
    return run_pipeline("demo/demo_script.md", build_mock_providers())


def test_full_recall_no_missed_items():
    report = _run()
    expected_ids = [it["item_id"] for it in EXPECTED["items"]]
    detected_ids = [it["item_id"] for it in report["items"]]
    score = score_extraction(expected_ids, detected_ids)
    assert score.missed == 0
    assert score.recall == 1.0


def test_states_match_ground_truth_per_item():
    report = _run()
    got = {it["item_id"]: it["state"] for it in report["items"]}
    for it in EXPECTED["items"]:
        assert got[it["item_id"]] == it["expected_state"], it["item_id"]


def test_distribution_matches_expected():
    report = _run()
    assert report["summary"] == EXPECTED["expected_distribution"]


def test_evidence_and_multisource_coverage():
    report = _run()
    m = report["metrics"]
    assert m["references_detected"] == 14
    assert m["evidence_backed"] == 13          # all but the fictional LunarFizz
    assert m["multi_source_satisfied"] == m["multi_source_required"] == 3
    assert m["traceable"] == 14


def test_evidence_integrity_only_grounded_urls():
    report = _run()
    for it in report["items"]:
        for ev in it["evidence"]:
            assert ev["source_url"].startswith("http")
            assert ev["retrieved_at"]  # provenance timestamp present


def test_governance_deny_and_audit():
    report = _run()
    g = report["governance"]
    assert g["unauthorized_blocked"] == 1      # the real DENY happened
    assert g["audit_verified"] is True         # tamper-evident chain intact


def test_lunarfizz_is_insufficient_evidence():
    report = _run()
    lunar = next(it for it in report["items"] if it["item_id"] == "CLR-014")
    assert lunar["state"] == "INSUFFICIENT_EVIDENCE"
    assert lunar["source_count"] == 0
