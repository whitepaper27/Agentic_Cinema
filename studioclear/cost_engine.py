"""Deterministic production-cost engine (sol.md §6A).

All arithmetic is Decimal and lives in CODE, never the model. The engine is
honest about coverage: a line with an unknown rate is excluded and the option is
marked incomplete (never silently zero); a shared expense counts once; contingency
is applied once to the eligible subtotal; and a comparison only calls one option
cheaper when its high is below the other's low AND both have complete coverage —
otherwise the ranges overlap or the comparison is incomplete.
"""

from __future__ import annotations

from decimal import Decimal

Range = dict  # {"low": Decimal, "high": Decimal}


def _d(v) -> Decimal:
    return Decimal(str(v))


def line_range(line: dict) -> Range | None:
    """Reporting-currency low/high for one cost line, or None if the rate is
    unknown (which keeps the option incomplete rather than zero)."""
    lo, hi = line.get("low_rate"), line.get("high_rate")
    if lo is None or hi is None or line.get("provenance") == "unknown":
        return None
    qty = _d(line.get("quantity", 1))
    factor = (_d(line.get("conversion_rate", 1))
              if line.get("original_currency") != line.get("reporting_currency")
              else Decimal(1))
    return {"low": _d(lo) * qty * factor, "high": _d(hi) * qty * factor}


def option_estimate(option: dict) -> dict:
    """Subtotal, contingency, total, and coverage for one option (sol.md §6A).

    Shared expenses (same shared_expense_id) are counted once. Missing rates are
    reported as missing categories and never added as zero."""
    seen_shared: set[str] = set()
    sub_lo = sub_hi = Decimal(0)
    missing: list[str] = []
    for line in option.get("cost_lines", []):
        sid = line.get("shared_expense_id")
        if sid and sid in seen_shared:
            continue                                  # count a shared expense once
        r = line_range(line)
        if r is None:
            missing.append(line.get("category", "unknown"))
            continue
        if sid:
            seen_shared.add(sid)
        sub_lo += r["low"]
        sub_hi += r["high"]

    pct = _d(option.get("contingency_pct", 0))
    cont_lo = sub_lo * pct / 100
    cont_hi = sub_hi * pct / 100
    return {
        "currency": option.get("reporting_currency", "USD"),
        "subtotal": {"low": sub_lo, "high": sub_hi},
        "contingency": {"low": cont_lo, "high": cont_hi},
        "total": {"low": sub_lo + cont_lo, "high": sub_hi + cont_hi},
        "coverage": "incomplete" if missing else "complete",
        "missing_categories": sorted(set(missing)),
    }


def compare_options(a: dict, b: dict) -> dict:
    """Overlap-aware comparison (sol.md §6A). Only names a cheaper option when the
    ranges do not overlap and both options have complete coverage."""
    ea, eb = option_estimate(a), option_estimate(b)
    if ea["coverage"] != "complete" or eb["coverage"] != "complete":
        return {"cheaper": None, "reason": "incomplete_coverage"}
    if ea["total"]["high"] < eb["total"]["low"]:
        return {"cheaper": a.get("option_id"), "reason": "upper_below_other_lower"}
    if eb["total"]["high"] < ea["total"]["low"]:
        return {"cheaper": b.get("option_id"), "reason": "upper_below_other_lower"}
    return {"cheaper": None, "reason": "ranges_overlap"}


def incentive_scenario(eligible_subtotal: Decimal, incentive: dict) -> dict:
    """A conditional incentive value — ONLY when an official source and explicit
    qualifying assumptions are present (sol.md §6A). Otherwise not calculated."""
    if (not incentive.get("official_source")
            or incentive.get("rate_basis") is None
            or incentive.get("qualifying_spend") is None):
        return {"status": "not_calculated", "reason": "eligibility information needed"}
    rate = _d(incentive["rate_basis"])
    qualifying = _d(incentive["qualifying_spend"])
    return {
        "status": "conditional",
        "potential_value": qualifying * rate / 100,
        "currency": incentive.get("currency"),
        "conditions": incentive.get("conditions", ""),
        "official_source": incentive["official_source"],
        "note": "sourced planning scenario, not an eligibility determination",
    }


def serialize(value):
    """Recursively convert Decimals to strings for JSON output (no float error)."""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize(v) for v in value]
    return value
