"""Shoot comparison API (sol.md §6A / §9) — offline example mode."""

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from app.api.main import app  # noqa: E402

client = TestClient(app)

BRIEF = {"base_city": "Los Angeles", "base_country": "USA", "reporting_currency": "USD",
         "shoot_days": 5, "traveling_crew": 10, "local_crew": 12,
         "accommodation_nights": 7, "travel_region": "Ireland", "vfx_shots": 6}


def _scene():
    return client.post("/scenes", json={
        "mode": "example", "source_type": "paste", "title": "Gold Stone",
        "script_text": ("A discovered stone turns whatever it touches to gold "
                        "on the California coast."),
    }).json()


def test_create_and_read_comparison():
    scene = _scene()
    r = client.post(f"/scenes/{scene['scene_id']}/shoot-comparisons",
                    json={"mode": "example", "brief": BRIEF})
    assert r.status_code == 200
    comp = r.json()
    assert [o["slot"] for o in comp["options"]] == \
        ["NEARBY_PRACTICAL", "TRAVEL_PRACTICAL", "LOCAL_VFX"]
    got = client.get(f"/shoot-comparisons/{comp['comparison_id']}")
    assert got.status_code == 200 and got.json()["comparison_id"] == comp["comparison_id"]


def test_recalculation_creates_new_calculation_version():
    scene = _scene()
    c1 = client.post(f"/scenes/{scene['scene_id']}/shoot-comparisons",
                     json={"mode": "example", "brief": {**BRIEF, "traveling_crew": 6}}).json()
    c2 = client.post(f"/scenes/{scene['scene_id']}/shoot-comparisons",
                     json={"mode": "example", "brief": {**BRIEF, "traveling_crew": 20},
                           "parent_comparison_id": c1["comparison_id"]}).json()
    assert c2["calculation_version"] == 2
    assert c2["parent_comparison_id"] == c1["comparison_id"]


def test_select_option_persists_decision():
    scene = _scene()
    comp = client.post(f"/scenes/{scene['scene_id']}/shoot-comparisons",
                       json={"mode": "example", "brief": BRIEF}).json()
    r = client.post(f"/shoot-comparisons/{comp['comparison_id']}/decision",
                    json={"option_id": "NEARBY_PRACTICAL", "rationale": "closest to base"})
    assert r.status_code == 200 and r.json()["selected"] == "NEARBY_PRACTICAL"
    again = client.get(f"/shoot-comparisons/{comp['comparison_id']}").json()
    assert again["decision"]["option_id"] == "NEARBY_PRACTICAL"


def test_unknown_option_is_rejected():
    scene = _scene()
    comp = client.post(f"/scenes/{scene['scene_id']}/shoot-comparisons",
                       json={"mode": "example", "brief": BRIEF}).json()
    r = client.post(f"/shoot-comparisons/{comp['comparison_id']}/decision",
                    json={"option_id": "NOPE"})
    assert r.status_code == 422


def test_planning_brief_handoff_is_sanitized():
    scene = _scene()
    comp = client.post(f"/scenes/{scene['scene_id']}/shoot-comparisons",
                       json={"mode": "example", "brief": BRIEF}).json()
    h = client.get(f"/shoot-comparisons/{comp['comparison_id']}/handoff").json()
    assert h["schema"] == "studioclear.planning_brief.v1"
    assert "owner" not in h
    assert h["estimate_status"] in ("complete estimate", "incomplete estimate", "Stale comparison")
    assert len(h["options"]) == 3


def test_live_production_research_is_blocked_not_faked():
    scene = _scene()
    r = client.post(f"/scenes/{scene['scene_id']}/shoot-comparisons",
                    json={"mode": "live", "brief": BRIEF})
    assert r.status_code == 503     # never fabricate prices when live isn't wired
