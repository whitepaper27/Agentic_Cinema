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


PLANNER_INSTRUCTION = (
    "You are StudioClear's research planner. Group unresolved clearance items "
    "into 3-4 efficient research batches (brands+orgs, people, historical+medical "
    "claims, places+media). If a capability is denied, replan using only "
    "approved tools (parallel.search.public_web)."
)


def build_planner():
    """Return the planner ADK Agent. Batch grouping itself stays deterministic
    via plan_batches(); the agent narrates/sequences the plan (sol.md §9)."""
    from google.adk.agents import Agent

    from studioclear.config import Config

    return Agent(
        name="research_planner",
        model=Config.from_env().extraction_model,  # gemini-2.5-pro
        instruction=PLANNER_INSTRUCTION,
    )
