"""Live production-research provider (sol.md §6A).

Runs REAL Parallel searches for location/rate/permit leads and attaches them, but
NEVER fabricates prices: a cost line's rate comes from the producer's brief
(provenance 'estimate') or stays empty ('quote needed', provenance 'unknown').
The deterministic cost engine does all arithmetic. Real search events demonstrate
live integration; honest coverage reflects what was actually sourced vs assumed.
"""

from __future__ import annotations

from studioclear.models import ClearanceItem, ItemType


class LiveProductionProvider:
    def __init__(self, search):
        self.search = search  # a SearchProvider (Parallel in live mode)

    def _search(self, query: str) -> list[dict]:
        item = ClearanceItem(item_id="q", scene=1, type=ItemType.LOCATION,
                             text_span=query)
        try:
            return self.search.search(query, item) or []
        except Exception:  # pragma: no cover - a live search failure is not fatal
            return []

    def research_options(self, scene: dict, brief: dict) -> dict:
        rc = brief.get("reporting_currency", "USD")
        base = brief.get("base_city") or "the base city"
        region = brief.get("travel_region") or "the alternative region"
        shoot = int(brief.get("shoot_days", 5) or 5)
        tcrew = int(brief.get("traveling_crew", 10) or 0)
        lcrew = int(brief.get("local_crew", 10) or 0)
        nights = int(brief.get("accommodation_nights", shoot) or 0)
        vfx_shots = int(brief.get("vfx_shots", 6) or 0)

        queries = [
            f"film production crew day rates {base}",
            f"film production crew day rates {region}",
            f"hotel nightly rates near filming location {region}",
            f"film permit requirements and fees {region}",
        ]
        sources: list[dict] = []
        sid = 0
        for q in queries:
            for r in self._search(q)[:2]:
                sid += 1
                sources.append({
                    "source_id": f"S{sid:03d}", "url": r.get("source_url", ""),
                    "title": r.get("title", ""), "excerpt": r.get("excerpt", ""),
                    "query": q, "provenance": "sourced_lead",
                })
        source_ids = [s["source_id"] for s in sources]

        def rate(key):
            lo, hi = brief.get(key + "_low"), brief.get(key + "_high")
            if lo is not None and hi is not None:
                return (lo, hi, "estimate")
            return (None, None, "unknown")

        def ln(cat, desc, qty, key, shared=None):
            lo, hi, prov = rate(key)
            d = {"category": cat, "description": desc, "quantity": qty,
                 "low_rate": lo, "high_rate": hi, "provenance": prov,
                 "original_currency": rc, "reporting_currency": rc}
            if shared:
                d["shared_expense_id"] = shared
            return d

        nearby = [ln("labor", f"{lcrew} local crew x {shoot} days", lcrew * shoot, "day_rate"),
                  ln("location_permits", "local permit", 1, "permit"),
                  ln("equipment", "equipment package", shoot, "equipment")]
        travel = [ln("labor", f"{tcrew} traveling crew x {shoot} days", tcrew * shoot, "day_rate"),
                  ln("travel", f"{tcrew} flights to {region}", tcrew, "flight"),
                  ln("accommodation", f"{tcrew} crew x {nights} nights", tcrew * nights, "hotel"),
                  ln("location_permits", "regional permit", 1, "permit")]
        vfx = [ln("labor", f"{lcrew} local crew x {shoot} days", lcrew * shoot, "day_rate"),
               ln("vfx", f"{vfx_shots} transformation shots", vfx_shots, "vfx_rate"),
               ln("equipment", "equipment package", shoot, "equipment")]

        est_note = ("Rates are producer estimates unless a supplier quote is entered; "
                    "unknown rates show Quote needed.")
        return {"sources": sources, "options": [
            {"slot": "NEARBY_PRACTICAL", "candidate": f"Practical location near {base}",
             "cost_lines": nearby, "contingency_pct": 10, "source_ids": source_ids,
             "limitations": [est_note, "Availability unconfirmed."]},
            {"slot": "TRAVEL_PRACTICAL", "candidate": region,
             "cost_lines": travel, "contingency_pct": 10, "source_ids": source_ids,
             "limitations": [est_note, "Incentives not calculated.", "Availability unconfirmed."]},
            {"slot": "LOCAL_VFX", "candidate": f"Local shoot + VFX near {base}",
             "cost_lines": vfx, "contingency_pct": 15, "source_ids": source_ids,
             "limitations": ["VFX quote needed.", est_note]},
        ]}
