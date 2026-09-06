"""Research Planner grouping (sol.md §9)."""

from studioclear.agents.research_planner import item_query, plan_batches
from studioclear.models import ClearanceItem, ItemType


def _item(iid, itype):
    return ClearanceItem(item_id=iid, scene=1, type=itype, text_span=iid)


def test_groups_related_types_and_skips_empty_batches():
    items = [
        _item("CLR-001", ItemType.BRAND),
        _item("CLR-002", ItemType.ORGANIZATION),
        _item("CLR-003", ItemType.HISTORICAL_CLAIM),
    ]
    batches = {b.name: b.item_ids for b in plan_batches(items)}
    assert batches["brands_and_orgs"] == ["CLR-001", "CLR-002"]
    assert batches["claims"] == ["CLR-003"]
    assert "people" not in batches  # no living-person items -> no empty batch


def test_non_research_items_excluded():
    it = _item("CLR-009", ItemType.LOCATION)
    it = it.model_copy(update={"research_required": False})
    assert plan_batches([it]) == []


def test_item_query_mentions_span_and_type():
    q = item_query(_item("CLR-001", ItemType.BRAND))
    assert "CLR-001" in q and "brand" in q
