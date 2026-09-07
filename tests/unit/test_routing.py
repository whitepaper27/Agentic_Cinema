"""Human-review routing is separate from research status (sol.md §7, §1).

Brand, music, and likeness questions route to a human; web search does not
resolve rights or a person's identity. A factually SUPPORTED item can still be
routed for review.
"""

from studioclear.contract.policy_evaluator import route_for_type
from studioclear.models import ItemType, Routing


def test_living_person_escalates_for_likeness_rights():
    assert route_for_type(ItemType.LIVING_PERSON) is Routing.ESCALATE


def test_brand_routes_to_review():
    assert route_for_type(ItemType.BRAND) is Routing.REVIEW


def test_song_routes_to_review():
    assert route_for_type(ItemType.SONG) is Routing.REVIEW


def test_organization_routes_to_review():
    assert route_for_type(ItemType.ORGANIZATION) is Routing.REVIEW


def test_historical_claim_needs_no_human_routing():
    assert route_for_type(ItemType.HISTORICAL_CLAIM) is Routing.NONE


def test_fictional_brand_needs_no_human_routing():
    assert route_for_type(ItemType.FICTIONAL_BRAND) is Routing.NONE
