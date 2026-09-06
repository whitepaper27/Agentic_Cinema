"""Research Spine CLI (sol.md E3.1 — the Day-1 critical path).

Runs the full spine and writes a clearance report. Default is OFFLINE/mock
(deterministic, no credentials) and also refreshes demo/cached_run.json. `--live`
uses the real Gemini + Parallel adapters (needs credentials).

    python scripts/run_spine.py                 # offline, writes demo/cached_run.json
    python scripts/run_spine.py --live in.pdf    # real APIs
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # repo root on path

from studioclear.pipeline import run_pipeline
from studioclear.providers import build_mock_providers
from studioclear.providers.base import Providers

CACHED = Path("demo/cached_run.json")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", nargs="?", default="demo/demo_script.md")
    ap.add_argument("--live", action="store_true", help="use real Gemini + Parallel")
    ap.add_argument("--no-cache", action="store_true", help="do not write cached_run.json")
    args = ap.parse_args(argv[1:])

    if args.live:
        from studioclear.providers.gemini import GeminiLLMProvider
        from studioclear.providers.parallel import ParallelSearchProvider
        providers = Providers(llm=GeminiLLMProvider(), search=ParallelSearchProvider())
    else:
        providers = build_mock_providers()

    report = run_pipeline(args.script, providers)

    if not args.live and not args.no_cache:
        CACHED.write_text(json.dumps(report, indent=2), encoding="utf-8")

    m, g = report["metrics"], report["governance"]
    print(f"StudioClear — {report['title']} ({report['script_id']})")
    print(f"  references detected : {m['references_detected']}")
    print(f"  evidence-backed     : {m['evidence_backed']}")
    print(f"  multi-source        : {m['multi_source_satisfied']}/{m['multi_source_required']}")
    print(f"  states              : {report['summary']}")
    print(f"  unauthorized blocked: {g['unauthorized_blocked']}")
    print(f"  audit verified      : {g['audit_verified']} ({g['audit_events']} events)")
    if not args.live and not args.no_cache:
        print(f"  wrote               : {CACHED}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
