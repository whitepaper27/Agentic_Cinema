"""Task selection + creative proposals (sol.md §5, §7).

'Improve this scene' works without a factual contradiction: a creative proposal
needs no evidence, is AI-labeled, requires acceptance, and preserves the premise.
"""

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from app.api.main import app  # noqa: E402

client = TestClient(app)

FANTASY = ("A discovered stone turns whatever it touches to gold. "
           "Mara stares at her golden hand on the California coast.")


def _scene(task="improve"):
    return client.post("/scenes", json={
        "mode": "example", "source_type": "paste", "title": "Gold Stone",
        "task": task, "script_text": FANTASY}).json()


def test_scene_records_the_selected_task():
    scene = _scene(task="plan")
    assert scene["task"] == "plan"


def test_creative_proposal_needs_no_finding_and_carries_no_evidence():
    scene = _scene()
    r = client.post(f"/scenes/{scene['scene_id']}/creative-proposals",
                    json={"instruction": "Add one atmospheric beat.", "kind": "elaborate"})
    assert r.status_code == 200
    prop = r.json()
    assert prop["proposal_kind"] == "creative_edit"
    assert "evidence_refs" not in prop and "evidence_source_ids" not in prop


def test_creative_proposal_accept_creates_new_version():
    scene = _scene()
    prop = client.post(f"/scenes/{scene['scene_id']}/creative-proposals",
                       json={"instruction": "Add a beat.", "kind": "elaborate"}).json()
    r = client.post(
        f"/scenes/{scene['scene_id']}/creative-proposals/{prop['proposal_id']}/decision",
        json={"action": "accept", "expected_version": 1})
    assert r.status_code == 200 and r.json()["scene_version"] == 2
    # The original fantasy premise text is preserved (addition, not a rewrite).
    got = client.get(f"/scenes/{scene['scene_id']}").json()
    assert "turns whatever it touches to gold" in got["versions"][-1]["scenes"][0]["text"]


def test_creative_proposal_reject_keeps_version():
    scene = _scene()
    prop = client.post(f"/scenes/{scene['scene_id']}/creative-proposals",
                       json={"instruction": "Add a beat."}).json()
    r = client.post(
        f"/scenes/{scene['scene_id']}/creative-proposals/{prop['proposal_id']}/decision",
        json={"action": "reject"})
    assert r.status_code == 200
    got = client.get(f"/scenes/{scene['scene_id']}").json()
    assert got["current_version"] == 1
