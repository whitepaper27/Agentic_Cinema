"""Deterministic cost engine (sol.md §6A).

Decimal arithmetic; honest coverage. Unknown rates stay incomplete (never zero),
a shared expense is counted once, contingency is applied once on the eligible
subtotal, and one option is only 'cheaper' when its high is below the other's low
AND both have comparable (complete) coverage — otherwise ranges overlap.
"""

from decimal import Decimal

from studioclear.cost_engine import (
    compare_options,
    incentive_scenario,
    line_range,
    option_estimate,
)


def _line(cat, qty, lo, hi, prov="estimate", **kw):
    return dict(category=cat, quantity=qty, low_rate=lo, high_rate=hi,
                provenance=prov, original_currency="USD", reporting_currency="USD", **kw)


def test_line_range_is_quantity_times_rate():
    r = line_range(_line("labor", 5, 100, 150))
    assert r == {"low": Decimal("500"), "high": Decimal("750")}


def test_currency_conversion_uses_line_rate():
    r = line_range(dict(category="equipment", quantity=2, low_rate=100, high_rate=100,
                        provenance="quote", original_currency="GBP",
                        reporting_currency="USD", conversion_rate="1.25"))
    assert r == {"low": Decimal("250.00"), "high": Decimal("250.00")}


def test_unknown_rate_is_none_not_zero():
    assert line_range(_line("vfx", 1, None, None, prov="unknown")) is None


def test_option_subtotal_sums_known_lines_and_flags_missing():
    opt = {"reporting_currency": "USD", "cost_lines": [
        _line("labor", 10, 200, 300),
        _line("vfx", 1, None, None, prov="unknown"),
    ]}
    est = option_estimate(opt)
    assert est["subtotal"] == {"low": Decimal("2000"), "high": Decimal("3000")}
    assert est["coverage"] == "incomplete"
    assert "vfx" in est["missing_categories"]


def test_contingency_applied_once_on_subtotal():
    opt = {"reporting_currency": "USD", "contingency_pct": 10,
           "cost_lines": [_line("labor", 1, 1000, 1000)]}
    est = option_estimate(opt)
    assert est["contingency"] == {"low": Decimal("100.0"), "high": Decimal("100.0")}
    assert est["total"] == {"low": Decimal("1100.0"), "high": Decimal("1100.0")}


def test_shared_expense_counted_once():
    opt = {"reporting_currency": "USD", "cost_lines": [
        dict(_line("travel", 1, 500, 500), shared_expense_id="flight-1"),
        dict(_line("travel", 1, 500, 500), shared_expense_id="flight-1"),  # same flight
    ]}
    est = option_estimate(opt)
    assert est["subtotal"] == {"low": Decimal("500"), "high": Decimal("500")}


def test_compare_declares_cheaper_only_when_ranges_do_not_overlap():
    a = {"option_id": "A", "reporting_currency": "USD",
         "cost_lines": [_line("labor", 1, 1000, 1200)]}
    b = {"option_id": "B", "reporting_currency": "USD",
         "cost_lines": [_line("labor", 1, 1500, 1800)]}
    assert compare_options(a, b) == {"cheaper": "A", "reason": "upper_below_other_lower"}


def test_compare_reports_overlap_when_ranges_intersect():
    a = {"option_id": "A", "reporting_currency": "USD",
         "cost_lines": [_line("labor", 1, 1000, 1600)]}
    b = {"option_id": "B", "reporting_currency": "USD",
         "cost_lines": [_line("labor", 1, 1500, 1800)]}
    assert compare_options(a, b)["reason"] == "ranges_overlap"
    assert compare_options(a, b)["cheaper"] is None


def test_compare_refuses_when_coverage_incomplete():
    a = {"option_id": "A", "reporting_currency": "USD",
         "cost_lines": [_line("labor", 1, 100, 100), _line("vfx", 1, None, None, prov="unknown")]}
    b = {"option_id": "B", "reporting_currency": "USD",
         "cost_lines": [_line("labor", 1, 5000, 5000)]}
    assert compare_options(a, b) == {"cheaper": None, "reason": "incomplete_coverage"}


def test_incentive_not_calculated_without_official_source_and_assumptions():
    out = incentive_scenario(Decimal("100000"),
                             {"rate_basis": 25, "qualifying_spend": 80000})  # no official_source
    assert out["status"] == "not_calculated"


def test_incentive_conditional_value_when_supported():
    out = incentive_scenario(Decimal("100000"), {
        "official_source": "https://www.bfi.org.uk/...", "rate_basis": 25,
        "qualifying_spend": 80000, "currency": "GBP",
        "conditions": "cultural test; min spend"})
    assert out["status"] == "conditional"
    assert out["potential_value"] == Decimal("20000")   # 25% of 80,000
