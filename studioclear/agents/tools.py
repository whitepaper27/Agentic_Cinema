"""ADK tools (sol.md §8, §25).

Functions the ADK agents may call. ADK auto-wraps them as FunctionTools from
their signature + docstring. `parallel_search` is the load-bearing runtime tool:
it runs a real Parallel query and returns raw sources. Because the pipeline reads
URLs from the tool RESPONSE (not the agent's text), the evidence-integrity
invariant (sol.md E8.1) holds even with an LLM in the loop.
"""

from __future__ import annotations

from studioclear.config import Config


def parallel_search(query: str) -> dict:
    """Search the public web via Parallel for authoritative, independent sources.

    Args:
        query: A focused research question about one clearance item.

    Returns:
        {"sources": [{"source_url", "title", "excerpt"}, ...]} straight from the
        Parallel API — never invent or edit these URLs.
    """
    from parallel import Parallel

    client = Parallel(api_key=Config.from_env().parallel_api_key)
    res = client.search(objective=query, search_queries=[query], max_chars_total=3000)
    sources = []
    for r in (res.results or [])[:5]:
        excerpts = getattr(r, "excerpts", None) or []
        sources.append({
            "source_url": r.url,
            "title": getattr(r, "title", "") or "",
            "excerpt": (excerpts[0] if excerpts else "")[:300],
        })
    return {"sources": sources}


def apply_policy(item_type: str, source_count: int) -> dict:
    """Apply the deterministic studio clearance policy to one item.

    Args:
        item_type: One of the ItemType values (e.g. "brand", "historical_claim").
        source_count: Number of independent sources found for the item.

    Returns:
        {"state", "reason", "policy_key"} — the deterministic triage result. The
        state comes from code, not the model, preserving Policy Determinism.
    """
    from studioclear.contract.clearance_contract import load_policy
    from studioclear.contract.policy_evaluator import evaluate
    from studioclear.models import ItemType

    result = evaluate(ItemType(item_type), source_count, load_policy())
    return {"state": result.state.value, "reason": result.reason,
            "policy_key": result.policy_key}
