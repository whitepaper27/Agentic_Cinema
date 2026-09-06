"""ADK runtime helpers (sol.md §25).

Bootstraps ADK to use the Gemini Developer API key, runs an agent to completion,
and extracts structured tool responses from the event stream. Keeping URL
extraction at the TOOL-RESPONSE layer (not the agent's free text) is what lets
ADK agents participate without breaking the evidence-integrity invariant (E8.1).
"""

from __future__ import annotations

import asyncio
import os

from studioclear.config import Config


def bootstrap_adk_env() -> None:
    """Point ADK/google-genai at the Developer API key (no Vertex/ADC needed)."""
    cfg = Config.from_env()
    if cfg.gemini_api_key:
        os.environ.setdefault("GOOGLE_API_KEY", cfg.gemini_api_key)
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "0")


def run_agent_sync(agent, message: str) -> list:
    """Run an ADK agent to completion and return its Event list (sync wrapper)."""
    from google.adk.runners import InMemoryRunner

    runner = InMemoryRunner(agent=agent, app_name="studioclear")
    return asyncio.run(runner.run_debug(message, quiet=True))


def extract_tool_responses(events: list, tool_name: str) -> list:
    """Return the raw response payloads for every call to `tool_name`."""
    out = []
    for e in events:
        parts = getattr(getattr(e, "content", None), "parts", None) or []
        for p in parts:
            fr = getattr(p, "function_response", None)
            if fr is not None and fr.name == tool_name:
                out.append(fr.response)
    return out


def final_text(events: list) -> str:
    """The agent's last text part (its recommendation/summary)."""
    text = ""
    for e in events:
        parts = getattr(getattr(e, "content", None), "parts", None) or []
        for p in parts:
            if getattr(p, "text", None):
                text = p.text
    return text
