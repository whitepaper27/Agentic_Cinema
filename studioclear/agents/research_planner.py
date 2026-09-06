"""Research Planner (sol.md §8, §9).

The GROUPING logic — bundle unresolved items into a few efficient research
batches — is pure, deterministic, and tested. The ADK-agent wrapper around it is
a stub for the live build (planner replans when a tool is DENIED, sol.md §17).
"""

from __future__ import annotations

from dataclasses import dataclass

from studioclear.models import ClearanceItem, ItemType

# Efficient research batches (sol.md §9): related types researched together.
BATCH_DEFS: list[tuple[str, set[ItemType]]] = [
    ("brands_and_orgs", {ItemType.BRAND, ItemType.ORGANIZATION, ItemType.FICTIONAL_BRAND}),
    ("people", {ItemType.LIVING_PERSON}),
    ("claims", {ItemType.HISTORICAL_CLAIM, ItemType.MEDICAL_CLAIM}),
    ("places_and_media", {ItemType.LOCATION, ItemType.SONG}),
]


@dataclass(frozen=True)
class Batch:
    name: str
    item_ids: list[str]


def plan_batches(items: list[ClearanceItem]) -> list[Batch]:
    """Group research-required items into non-empty batches, deterministically."""
    todo = [it for it in items if it.research_required]
    batches: list[Batch] = []
    for name, types in BATCH_DEFS:
        ids = [it.item_id for it in todo if it.type in types]
        if ids:
            batches.append(Batch(name=name, item_ids=ids))
    return batches


def item_query(item: ClearanceItem) -> str:
    """The research question sent to the search engine for one item (sol.md §10)."""
    return (
        f"Provide authoritative, independent sources about "
        f"'{item.text_span}' ({item.type.value})."
    )


def build_planner():  # pragma: no cover - stub
    """STUB: ADK Agent wrapping plan_batches; replans on DENY (sol.md §17)."""
    raise NotImplementedError("Wire the ADK planner agent on the Day-1/2 build.")
