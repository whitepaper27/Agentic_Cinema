"""Schema-v2 research pipeline (sol.md §6, §7, §13.1).

Runs research over confirmed items using mock providers and produces findings
with a research status and separate human routing — no source-count verdicts, no
confidence percentages. Gate: irrelevant/single/again sources cannot clear a
factual claim.
"""

from studioclear.providers.mock import build_mock_providers
from studioclear.research_pipeline import run_research


def _run():
    providers = build_mock_providers()
    items = providers.llm.extract_items([])  # mock returns the fixed 14
    return run_research(items, providers, run_id="run_test", scene_version=1)


def test_report_is_schema_v2_with_findings_and_no_confidence():
    rep = _run()
    assert rep["schema_version"] == 2
    assert len(rep["findings"]) == 14
    # Confidence percentages are deprecated in schema v2 (sol.md §7).
    assert "confidence" not in rep["findings"][0]


def test_primary_source_supports_a_historical_claim():
    rep = _run()
    f = {x["item_id"]: x for x in rep["findings"]}
    # Apollo 11 has a nasa.gov (primary) source → SUPPORTED.
    assert f["CLR-011"]["research_status"] == "SUPPORTED"


def test_single_secondary_source_does_not_clear():
    rep = _run()
    f = {x["item_id"]: x for x in rep["findings"]}
    # One Wikipedia page for a brand is below the corroboration bar → UNRESOLVED.
    assert f["CLR-001"]["research_status"] == "UNRESOLVED"


def test_no_sources_is_unresolved_not_safe():
    rep = _run()
    f = {x["item_id"]: x for x in rep["findings"]}
    # LunarFizz (fictional) returns no evidence → UNRESOLVED, never "clear"/"safe".
    assert f["CLR-014"]["research_status"] == "UNRESOLVED"
    assert f["CLR-014"]["routing"] == "NONE"


def test_living_person_routes_to_human_regardless_of_evidence():
    rep = _run()
    f = {x["item_id"]: x for x in rep["findings"]}
    assert f["CLR-004"]["routing"] == "ESCALATE"


def test_findings_only_cite_grounded_sources():
    rep = _run()
    # Every evidence passage on every finding must resolve to a registered source.
    source_ids = {s["source_id"] for s in rep["sources"]}
    for finding in rep["findings"]:
        for a in finding["evidence"]:
            assert a["source_id"] in source_ids


def test_audit_chain_verifies():
    rep = _run()
    assert rep["governance"]["audit_verified"] is True


def test_budget_marks_overflow_findings_not_researched():
    providers = build_mock_providers()
    items = providers.llm.extract_items([])
    rep = run_research(items, providers, run_id="run_budget", max_findings=3)
    statuses = [f["research_status"] for f in rep["findings"]]
    # First three researched; the remaining eleven are honestly NOT_RESEARCHED.
    assert statuses[3:] == ["NOT_RESEARCHED"] * (len(items) - 3)
    assert rep["findings"][5]["limitations"] == "run limit reached"
