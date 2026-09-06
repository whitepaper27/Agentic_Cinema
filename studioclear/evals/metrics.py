"""Eval metrics (sol.md §20 / E5.6) — recall-first.

For clearance, the dangerous error is a MISSED item, not a false positive, so
recall ("missed clearance risks") is the headline. Pure and tested.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractionScore:
    expected: int
    detected_true: int   # expected items that were found
    spurious: int        # detected items with no expected match
    missed: int          # expected items not found  == the costly failure

    @property
    def recall(self) -> float:
        return self.detected_true / self.expected if self.expected else 1.0

    @property
    def precision(self) -> float:
        total_detected = self.detected_true + self.spurious
        return self.detected_true / total_detected if total_detected else 1.0


def score_extraction(expected_ids: list[str], detected_ids: list[str]) -> ExtractionScore:
    """Compare expected vs detected clearance-item ids by set membership."""
    expected = set(expected_ids)
    detected = set(detected_ids)
    detected_true = len(expected & detected)
    return ExtractionScore(
        expected=len(expected),
        detected_true=detected_true,
        spurious=len(detected - expected),
        missed=len(expected - detected),
    )
