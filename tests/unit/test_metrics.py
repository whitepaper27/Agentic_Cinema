"""Recall-first eval metrics (sol.md E5.6): a missed item is the costly error."""

from studioclear.evals.metrics import score_extraction


def test_perfect_recall():
    s = score_extraction(["CLR-001", "CLR-002"], ["CLR-001", "CLR-002"])
    assert s.recall == 1.0 and s.missed == 0


def test_missed_item_lowers_recall():
    s = score_extraction(["CLR-001", "CLR-002", "CLR-003"], ["CLR-001", "CLR-002"])
    assert s.missed == 1
    assert round(s.recall, 3) == 0.667


def test_spurious_item_lowers_precision_not_recall():
    s = score_extraction(["CLR-001"], ["CLR-001", "CLR-999"])
    assert s.recall == 1.0
    assert s.precision == 0.5
