"""Confidence is a pure, deterministic function of evidence (sol.md §20 / E5.1) —
not a model-guessed probability we can't defend."""

from studioclear.research.evidence_normalizer import deterministic_confidence


def test_deterministic():
    assert {deterministic_confidence(2) for _ in range(100)} == {deterministic_confidence(2)}


def test_monotonic_and_bounded():
    assert deterministic_confidence(0) == 0.4
    assert deterministic_confidence(1) < deterministic_confidence(3)
    assert deterministic_confidence(100) == 1.0  # capped
