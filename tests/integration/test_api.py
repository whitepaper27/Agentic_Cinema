"""FastAPI endpoint tests (sol.md E3.2) — offline/deterministic (prefer_live=False).

Covers the producer workflow: upload -> run -> report -> human decision/override,
and that the audit chain stays verified after human action.
"""

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from app.api.main import app  # noqa: E402

client = TestClient(app)


def _upload():
    r = client.post("/upload", json={"prefer_live": False, "title": "Midnight Signal"})
    assert r.status_code == 200
    return r.json()


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_upload_runs_full_pipeline():
    data = _upload()
    assert data["summary"] == {"REVIEW": 6, "ESCALATE": 2, "CLEAR": 5,
                               "INSUFFICIENT_EVIDENCE": 1}
    assert data["governance"]["unauthorized_blocked"] == 1
    assert data["governance"]["audit_verified"] is True
    assert data["providers"]["llm"] == "MockLLMProvider"


def test_get_run_returns_items():
    run_id = _upload()["run_id"]
    r = client.get(f"/run/{run_id}")
    assert r.status_code == 200
    assert len(r.json()["items"]) == 14


def test_human_override_is_audited():
    run_id = _upload()["run_id"]
    r = client.post("/decision", json={
        "run_id": run_id, "item_id": "CLR-001",
        "action": "override", "reason": "Cleared after rights-holder email",
    })
    assert r.status_code == 200
    assert r.json()["item"]["human_decision"]["action"] == "override"

    audit = client.get(f"/audit/{run_id}").json()
    assert audit["verified"] is True
    assert any(e["body"].get("action") == "human_decision" for e in audit["chain"])


def test_override_requires_reason():
    run_id = _upload()["run_id"]
    r = client.post("/decision", json={
        "run_id": run_id, "item_id": "CLR-001", "action": "override", "reason": "",
    })
    assert r.status_code == 400


def test_unknown_run_404():
    assert client.get("/run/run_nope").status_code == 404


def test_run_includes_agents_and_iam():
    run_id = _upload()["run_id"]
    r = client.get(f"/run/{run_id}").json()
    models = {a["name"]: a["model"] for a in r["agents"]}
    assert models["research_planner"] == "gemini-2.5-pro"
    assert models["researcher"] == "gemini-2.5-flash"
    assert any(c["decision"] == "ALLOW" for c in r["iam_checks"])
    assert any(c["decision"] == "DENY" for c in r["iam_checks"])


def test_policy_endpoint_exposes_rules():
    r = client.get("/policy")
    assert r.status_code == 200
    body = r.json()
    assert body["policy_id"] == "demo_policy_v1"
    sp = body["studio_policy"]
    assert sp["historical_claim"]["minimum_independent_sources"] == 2
    assert sp["living_person"]["action"] == "ESCALATE"
    assert sp["fictional_brand_negative_context"]["insufficient_evidence_allowed"] is True
