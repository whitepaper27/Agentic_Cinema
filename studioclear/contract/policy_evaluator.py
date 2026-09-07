"""Deterministic policy evaluation (sol.md §12).

The system does not decide legality. It maps (item type, evidence) through the
studio policy to a single triage state. Pure and deterministic: same structured
input -> same state (the "Policy Determinism" eval, sol.md §20 / E5.1). Final
production/legal decisions remain HUMAN-ONLY (sol.md §14).
"""

from __future__ import annotations

from dataclasses import dataclass

from studioclear.models import (
    ClaimAssessment,
    ClearanceState,
    ItemType,
    Relation,
    ResearchStatus,
    Routing,
)

# Human-review routing by item type (sol.md §7/§1). Rights and likeness are not
# resolved by web search, so they always route to a person regardless of what the
# factual research finds. Factual claims carry their answer in ResearchStatus.
_ROUTE_BY_TYPE: dict[ItemType, Routing] = {
    ItemType.LIVING_PERSON: Routing.ESCALATE,   # likeness / personality rights
    ItemType.BRAND: Routing.REVIEW,             # trademark / rights review
    ItemType.ORGANIZATION: Routing.REVIEW,
    ItemType.SONG: Routing.REVIEW,              # music licensing
}


def route_for_type(item_type: ItemType) -> Routing:
    """Return the human-review routing for an item type, independent of evidence."""
    return _ROUTE_BY_TYPE.get(item_type, Routing.NONE)

# Map each item type to a key in the studio_policy YAML. `fictional_brand` maps
# to the negative-context rule (our LunarFizz honesty case, sol.md §4).
TYPE_TO_POLICY_KEY: dict[ItemType, str] = {
    ItemType.BRAND: "brand_reference",
    ItemType.LIVING_PERSON: "living_person",
    ItemType.ORGANIZATION: "organization",
    ItemType.LOCATION: "location",
    ItemType.SONG: "music_reference",
    ItemType.HISTORICAL_CLAIM: "historical_claim",
    ItemType.MEDICAL_CLAIM: "medical_claim",
    ItemType.FICTIONAL_BRAND: "fictional_brand_negative_context",
}


@dataclass(frozen=True)
class PolicyResult:
    state: ClearanceState
    reason: str
    policy_key: str


def assess_research_status(
    assessments: list[ClaimAssessment], policy: dict
) -> ResearchStatus:
    """Map validated claim assessments to a single research status (sol.md §7).

    Deterministic and pure — the model's job is to produce the assessments; this
    code decides the status. Only *applicable* passages count. The factual
    threshold is met by one applicable primary source, OR by corroboration from
    N sources with documented independence and distinct publishers (default 2).
    An applicable contradiction can never be cleared away by weak support:
    support-meets + contradiction -> MIXED; contradiction alone -> CONTRADICTED.
    """
    factual = policy.get("factual", {}) if isinstance(policy, dict) else {}
    min_corroboration = int(factual.get("minimum_corroborating_sources", 2))

    applicable = [a for a in assessments if a.applicable]
    supports = [a for a in applicable if a.relation is Relation.SUPPORTS]
    contradicts = [a for a in applicable if a.relation is Relation.CONTRADICTS]

    has_primary_support = any(a.source_type.value == "primary" for a in supports)
    independent_pubs = {
        a.publisher
        for a in supports
        if a.independence == "documented" and a.publisher
    }
    support_meets = has_primary_support or len(independent_pubs) >= min_corroboration
    has_contradiction = len(contradicts) >= 1

    if support_meets and has_contradiction:
        return ResearchStatus.MIXED
    if support_meets:
        return ResearchStatus.SUPPORTED
    if has_contradiction:
        return ResearchStatus.CONTRADICTED
    return ResearchStatus.UNRESOLVED


def evaluate(item_type: ItemType, source_count: int, policy: dict) -> PolicyResult:
    """Return the triage state for an item given its evidence and the policy.

    Rules:
      VERIFY   -> CLEAR if source_count >= minimum_independent_sources,
                  else INSUFFICIENT_EVIDENCE
      REVIEW   -> REVIEW
      ESCALATE -> ESCALATE; but if evidence_required and none found and the rule
                  allows it, INSUFFICIENT_EVIDENCE (the LunarFizz path)
    """
    key = TYPE_TO_POLICY_KEY.get(item_type)
    rule = policy.get(key, {}) if key else {}
    action = rule.get("action", "REVIEW")

    if action == "VERIFY":
        needed = int(rule.get("minimum_independent_sources", 1))
        if source_count >= needed:
            return PolicyResult(ClearanceState.CLEAR, "verified_for_research", key)
        return PolicyResult(
            ClearanceState.INSUFFICIENT_EVIDENCE, "below_min_sources", key
        )

    if action == "ESCALATE":
        if rule.get("evidence_required") and source_count == 0 and rule.get(
            "insufficient_evidence_allowed"
        ):
            return PolicyResult(
                ClearanceState.INSUFFICIENT_EVIDENCE, "no_authoritative_match", key
            )
        return PolicyResult(ClearanceState.ESCALATE, "human_review_required", key)

    # default / REVIEW
    return PolicyResult(ClearanceState.REVIEW, "studio_review_required", key or "default")
