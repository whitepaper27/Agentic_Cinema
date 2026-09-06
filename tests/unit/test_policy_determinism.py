"""Policy Determinism eval (sol.md §20 / E5.1): same input -> same state, and
the rule semantics are correct."""

from studioclear.contract.clearance_contract import load_policy
from studioclear.contract.policy_evaluator import evaluate
from studioclear.models import ClearanceState, ItemType

POLICY = load_policy()


def test_deterministic_same_input_same_state():
    results = {evaluate(ItemType.MEDICAL_CLAIM, 2, POLICY).state for _ in range(100)}
    assert results == {ClearanceState.CLEAR}


def test_brand_is_review():
    assert evaluate(ItemType.BRAND, 2, POLICY).state is ClearanceState.REVIEW


def test_living_person_escalates():
    assert evaluate(ItemType.LIVING_PERSON, 5, POLICY).state is ClearanceState.ESCALATE


def test_verify_needs_minimum_sources():
    assert evaluate(ItemType.HISTORICAL_CLAIM, 1, POLICY).state is (
        ClearanceState.INSUFFICIENT_EVIDENCE
    )
    assert evaluate(ItemType.HISTORICAL_CLAIM, 2, POLICY).state is ClearanceState.CLEAR


def test_fictional_brand_no_evidence_is_insufficient():
    # The LunarFizz honesty case (sol.md §4).
    assert evaluate(ItemType.FICTIONAL_BRAND, 0, POLICY).state is (
        ClearanceState.INSUFFICIENT_EVIDENCE
    )
