"""Schema-v2 scene/run API (sol.md §9, §10, §12).

Real input produces an editable extraction and, once confirmed, source-linked
findings. Live mode never silently falls back to fixtures.
"""

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

import studioclear.providers as P  # noqa: E402
from app.api.main import app  # noqa: E402

client = TestClient(app)

SCENE_TEXT = ("INT. HANGAR - DAY\n"
              "A pilot says the Apollo 11 Moon landing happened in 1969.")


def test_paste_scene_extracts_editable_draft():
    r = client.post("/scenes", json={
        "mode": "example", "source_type": "paste", "title": "Test scene",
        "instruction": "Check historical facts", "script_text": SCENE_TEXT})
    assert r.status_code == 200
    scene = r.json()
    assert scene["scene_id"].startswith("scene_")
    assert scene["current_version"] == 1
    assert scene["provider_mode"] == "example"
    assert scene["versions"][0]["items"]          # candidate claims to confirm
    assert scene["instruction"] == "Check historical facts"


def test_empty_paste_is_rejected():
    r = client.post("/scenes", json={
        "mode": "example", "source_type": "paste", "script_text": "   "})
    assert r.status_code == 422


def test_correction_creates_new_version():
    scene = client.post("/scenes", json={
        "mode": "example", "source_type": "paste", "script_text": SCENE_TEXT}).json()
    r = client.patch(f"/scenes/{scene['scene_id']}", json={
        "expected_version": 1, "instruction": "Only check the date"})
    assert r.status_code == 200
    assert r.json()["current_version"] == 2


def test_stale_version_correction_conflicts():
    scene = client.post("/scenes", json={
        "mode": "example", "source_type": "paste", "script_text": SCENE_TEXT}).json()
    r = client.patch(f"/scenes/{scene['scene_id']}", json={
        "expected_version": 99, "instruction": "x"})
    assert r.status_code == 409


def test_run_over_confirmed_scene_returns_findings():
    scene = client.post("/scenes", json={
        "mode": "example", "source_type": "paste", "script_text": SCENE_TEXT,
        "title": "T"}).json()
    r = client.post("/runs", json={"scene_id": scene["scene_id"], "mode": "example"})
    assert r.status_code == 200
    run = r.json()
    assert run["schema_version"] == 2
    assert run["findings"]
    got = client.get(f"/run/{run['run_id']}")
    assert got.status_code == 200 and got.json()["run_id"] == run["run_id"]


def test_too_many_pages_rejected():
    imgs = ["data:image/png;base64,AAAA"] * 4
    r = client.post("/scenes", json={
        "mode": "example", "source_type": "images", "images": imgs})
    assert r.status_code == 413


def test_unsupported_image_type_rejected():
    r = client.post("/scenes", json={
        "mode": "example", "source_type": "images",
        "images": ["data:image/gif;base64,AAAA"]})
    assert r.status_code == 422


def test_live_mode_without_keys_never_falls_back_to_mock(monkeypatch):
    class _NoKeys:
        gemini_api_key = ""
        parallel_api_key = ""
    monkeypatch.setattr(P.Config, "from_env", lambda: _NoKeys())
    with pytest.raises(P.LiveKeysMissing):
        P.build_providers_for_mode("live")


def _example_scene_run():
    # The labeled example fixture contains a deliberate Apollo-year mismatch.
    scene = client.post("/scenes", json={
        "mode": "example", "source_type": "paste",
        "script_text": "It was the Apollo 11 Moon landing in 1968 that changed everything.",
        "title": "Example"}).json()
    run = client.post("/runs", json={"scene_id": scene["scene_id"],
                                     "mode": "example"}).json()
    return scene, run


def test_full_revision_recheck_flow_over_api():
    scene, run = _example_scene_run()
    apollo = next(f for f in run["findings"] if f["item_id"] == "CLR-001")
    assert apollo["research_status"] == "CONTRADICTED"
    rev = client.post(f"/runs/{run['run_id']}/revisions",
                      json={"finding_id": apollo["finding_id"]})
    assert rev.status_code == 200
    revision_id = rev.json()["revision_id"]
    dec = client.post(f"/revisions/{revision_id}/decision",
                      json={"run_id": run["run_id"], "action": "accept",
                            "expected_version": 1, "idempotency_key": "k1"})
    assert dec.status_code == 200 and dec.json()["scene_version"] == 2
    rc = client.post(f"/scenes/{scene['scene_id']}/recheck",
                     json={"run_id": run["run_id"]})
    assert rc.status_code == 200
    body = rc.json()
    assert "CLR-001" in body["recheck"]["modified"]
    # The corrected claim now researches as supported — the observable flip.
    flipped = next(f for f in body["findings"] if f["item_id"] == "CLR-001")
    assert flipped["research_status"] == "SUPPORTED"


def test_revision_on_unresolved_finding_is_blocked():
    _scene, run = _example_scene_run()
    nikon = next((f for f in run["findings"] if f["research_status"] == "UNRESOLVED"), None)
    assert nikon is not None
    r = client.post(f"/runs/{run['run_id']}/revisions",
                    json={"finding_id": nikon["finding_id"]})
    assert r.status_code == 422
