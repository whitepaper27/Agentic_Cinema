"""Live Gemini extraction smoke test (sol.md E1.5 / E3.1.2).

Proves the real GeminiLLMProvider extracts clearance items from the demo script
and that the embedded prompt-injection line does NOT derail it (E8.2).

    python scripts/smoke_extract.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from studioclear.analyzer.script_parser import parse_script
from studioclear.providers.gemini import GeminiLLMProvider


def main() -> int:
    scenes = parse_script("demo/demo_script.md")
    items = GeminiLLMProvider().extract_items(scenes)
    print(f"LIVE Gemini extracted {len(items)} items:")
    for it in items:
        print(f"  {it.item_id}  s{it.scene}  {it.type.value:16s} {it.text_span}")
    # Sanity: injection line must not collapse extraction to a single/empty set.
    assert len(items) >= 10, "extraction too small — check the model/prompt"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
