"""Shoot comparison builder (sol.md §6A).

Assembles the three fixed approach slots from a producer brief using the cost
engine, responds to a changed constraint (traveling crew), and only recommends an
option when the evidence/costs support it.
"""

from decimal import Decimal

from studioclear.providers.mock import ExampleProductionProvider
from studioclear.shoot_comparison import build_comparison

BRIEF = {
    "base_city": "Los Angeles", "base_country": "USA", "reporting_currency": "USD",
    "shoot_days": 5, "prep_days": 2, "travel_days": 2,
    "traveling_crew": 10, "local_crew": 12, "accommodation_nights": 7,
    "travel_region": "Ireland", "vfx_shots": 6, "budget_ceiling": None,
}


def _cmp(brief):
    return build_comparison({"scene_id": "s1", "current_version": 1}, brief,
                            ExampleProductionProvider(), comparison_id="cmp_1")


def test_three_fixed_option_slots():
    c = _cmp(BRIEF)
    assert [o["slot"] for o in c["options"]] == \
        ["NEARBY_PRACTICAL", "TRAVEL_PRACTICAL", "LOCAL_VFX"]
    for o in c["options"]:
        assert "estimate" in o and "total" in o["estimate"]


def test_changing_traveling_crew_changes_travel_costs():
    small = _cmp({**BRIEF, "traveling_crew": 6})
    large = _cmp({**BRIEF, "traveling_crew": 20})

    def travel_total_high(c):
        t = next(o for o in c["options"] if o["slot"] == "TRAVEL_PRACTICAL")
        return Decimal(t["estimate"]["total"]["high"])
    assert travel_total_high(large) > travel_total_high(small)


def test_nearby_option_has_no_flights():
    c = _cmp(BRIEF)
    nearby = next(o for o in c["options"] if o["slot"] == "NEARBY_PRACTICAL")
    assert all(line["category"] != "travel" for line in nearby["cost_lines"])


def test_comparison_records_scene_version_and_calculation_version():
    c = _cmp(BRIEF)
    assert c["scene_version"] == 1
    assert c["calculation_version"] == 1
    assert c["comparison_id"] == "cmp_1"


def test_recommendation_is_honest_about_overlap():
    c = _cmp(BRIEF)
    # With overlapping ranges across approaches, no single option is declared the
    # confident winner; the recommendation reason is explicit.
    assert c["recommendation"]["reason"] in (
        "ranges_overlap", "upper_below_other_lower", "incomplete_coverage")
