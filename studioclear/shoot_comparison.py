"""Shoot comparison builder (sol.md §6A).

Assembles the three fixed approach slots (NEARBY_PRACTICAL, TRAVEL_PRACTICAL,
LOCAL_VFX) from a producer brief. A production provider supplies candidate/cost
lines/sources (deterministic in example mode, Parallel-sourced live); the
deterministic cost engine does every calculation. The recommendation is honest:
a single option is only preferred when its range does not overlap the others and
coverage is comparable — otherwise ranges overlap or the comparison is incomplete.
"""

from __future__ import annotations

from datetime import datetime, timezone

from studioclear import cost_engine

SLOTS = ("NEARBY_PRACTICAL", "TRAVEL_PRACTICAL", "LOCAL_VFX")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_comparison(scene: dict, brief: dict, provider, comparison_id: str,
                     provider_mode: str = "example", parent_id: str | None = None,
                     calculation_version: int = 1, now: str | None = None) -> dict:
    """Research + calculate one three-option comparison against a scene version."""
    res = provider.research_options(scene, brief)
    rc = brief.get("reporting_currency", "USD")

    options = []
    for raw in res["options"]:
        priced = {"option_id": raw["slot"], "reporting_currency": rc,
                  "cost_lines": raw["cost_lines"],
                  "contingency_pct": raw.get("contingency_pct", 0)}
        est = cost_engine.option_estimate(priced)
        options.append({
            "option_id": raw["slot"], "slot": raw["slot"],
            "candidate": raw.get("candidate", ""),
            "cost_lines": cost_engine.serialize(raw["cost_lines"]),
            "contingency_pct": raw.get("contingency_pct", 0),
            "estimate": cost_engine.serialize(est),
            "source_ids": raw.get("source_ids", []),
            "limitations": raw.get("limitations", []),
        })

    recommendation = _recommend(options)
    complete = all(o["estimate"]["coverage"] == "complete" for o in options)

    return {
        "comparison_id": comparison_id,
        "parent_comparison_id": parent_id,
        "scene_id": scene.get("scene_id"),
        "scene_version": scene.get("current_version"),
        "provider_mode": provider_mode,
        "calculation_version": calculation_version,
        "reporting_currency": rc,
        "brief": brief,
        "options": options,
        "sources": res.get("sources", []),
        "recommendation": recommendation,
        "estimate_status": "complete estimate" if complete else "incomplete estimate",
        "created_at": now or _now(),
    }


def _recommend(options: list[dict]) -> dict:
    """Prefer an option only if it is cheaper than BOTH others with non-overlapping,
    complete ranges. Otherwise report overlap/insufficiency honestly (sol.md §6A)."""
    priced = [{"option_id": o["option_id"], "reporting_currency": o["estimate"]["currency"],
               "cost_lines": _rehydrate(o["cost_lines"]),
               "contingency_pct": o["contingency_pct"]} for o in options]
    for i, a in enumerate(priced):
        others = [b for j, b in enumerate(priced) if j != i]
        verdicts = [cost_engine.compare_options(a, b) for b in others]
        if all(v["cheaper"] == a["option_id"] for v in verdicts):
            return {"preferred": a["option_id"], "reason": "upper_below_other_lower"}
    if any(cost_engine.option_estimate(p)["coverage"] != "complete" for p in priced):
        return {"preferred": None, "reason": "incomplete_coverage"}
    return {"preferred": None, "reason": "ranges_overlap"}


def _rehydrate(cost_lines: list[dict]) -> list[dict]:
    """Cost lines were serialized (Decimals→str); the engine re-parses via Decimal(str)."""
    return cost_lines
