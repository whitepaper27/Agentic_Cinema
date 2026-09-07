"""Live production provider (sol.md §6A) — offline with a fake search.

Runs real search queries (here a fake), attaches the returned leads, and NEVER
fabricates rates: with no brief rate assumptions every rate is 'quote needed'
(unknown provenance); supplying a rate makes it a producer estimate.
"""

from decimal import Decimal

from studioclear.cost_engine import option_estimate
from studioclear.providers.production import LiveProductionProvider

BRIEF = {"base_city": "LA", "travel_region": "Ireland", "reporting_currency": "USD",
         "shoot_days": 5, "traveling_crew": 10, "local_crew": 12, "accommodation_nights": 7}


class _FakeSearch:
    def __init__(self):
        self.queries = []

    def search(self, query, item):
        self.queries.append(query)
        return [{"source_url": "https://example.gov/rates", "title": "Rate lead",
                 "excerpt": "Regional film rate information."}]


def test_runs_searches_and_attaches_leads():
    fs = _FakeSearch()
    res = LiveProductionProvider(fs).research_options({}, BRIEF)
    assert len(fs.queries) == 4                     # real searches were issued
    assert res["sources"] and all(s["provenance"] == "sourced_lead" for s in res["sources"])
    assert [o["slot"] for o in res["options"]] == \
        ["NEARBY_PRACTICAL", "TRAVEL_PRACTICAL", "LOCAL_VFX"]


def test_no_brief_rates_means_quote_needed_not_fabricated():
    res = LiveProductionProvider(_FakeSearch()).research_options({}, BRIEF)
    nearby = res["options"][0]
    assert all(line["low_rate"] is None for line in nearby["cost_lines"])
    est = option_estimate({"reporting_currency": "USD", "cost_lines": nearby["cost_lines"],
                           "contingency_pct": nearby["contingency_pct"]})
    assert est["coverage"] == "incomplete"          # honest: nothing was priced


def test_brief_rate_becomes_a_producer_estimate():
    brief = {**BRIEF, "day_rate_low": 400, "day_rate_high": 600}
    res = LiveProductionProvider(_FakeSearch()).research_options({}, brief)
    labor = res["options"][0]["cost_lines"][0]
    assert labor["category"] == "labor"
    assert labor["provenance"] == "estimate"
    assert labor["low_rate"] == 400
    est = option_estimate({"reporting_currency": "USD",
                           "cost_lines": [labor], "contingency_pct": 0})
    assert est["subtotal"]["low"] == Decimal("400") * (12 * 5)
