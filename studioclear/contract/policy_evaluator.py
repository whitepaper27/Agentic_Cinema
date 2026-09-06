"""Deterministic policy evaluation (sol.md §12).

The system does not decide legality. It maps (item type, evidence) through the
studio policy to a single triage state. Pure and deterministic: same structured
input -> same state (the "Policy Determinism" eval, sol.md §20 / E5.1). Final
production/legal decisions remain HUMAN-ONLY (sol.md §14).
"""

from __future__ import annotations

from dataclasses import dataclass

from studioclear.models import ClearanceState, ItemType

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
