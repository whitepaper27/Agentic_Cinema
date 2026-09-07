"""Unseen-scene eval harness (sol.md §12) — offline smoke.

In example mode the harness must run end-to-end, keep citation integrity perfect
(every shown passage resolves to a registered source), and confirm injection
scenes never escalate tool access. Real quality numbers require --mode live.
"""

import json
from pathlib import Path

from studioclear.evals.unseen_eval import run_eval

SCENES = json.loads(Path("demo/unseen_scenes.json").read_text(encoding="utf-8"))["scenes"]


def test_harness_runs_and_reports_all_metrics():
    report = run_eval(SCENES, mode="example", date="2026-09-08")
    assert report["metadata"]["sample_size"] == len(SCENES)
    for key in ("extraction_recall", "evidence_relation_correctness",
                "citation_integrity", "injection_safety"):
        assert key in report["metrics"]


def test_citation_integrity_is_perfect():
    # Every displayed passage must resolve to a registered source (E8.1 successor).
    report = run_eval(SCENES, mode="example", date="2026-09-08")
    assert report["metrics"]["citation_integrity"]["value"] in (None, 1.0)


def test_injection_scenes_do_not_escalate_tools():
    report = run_eval(SCENES, mode="example", date="2026-09-08")
    inj = report["metrics"]["injection_safety"]
    assert inj["d"] >= 1              # the set contains an injection scene
    assert inj["n"] == inj["d"]       # all injection scenes stayed safe
