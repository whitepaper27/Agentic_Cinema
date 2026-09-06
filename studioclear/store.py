"""Run persistence + the Human Decision Desk (sol.md §14, §18, §19).

P0 store = one JSON file per run (Firestore is a later drop-in, §11). Human
decisions and overrides are applied here and appended to the run's tamper-evident
audit chain (E8.3), so the log stays verifiable after human action.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from studioclear.security.audit import AuditLog

# Configurable so Cloud Run can point it at a writable path (e.g. /tmp), where
# the container filesystem is ephemeral. Defaults to a local dir for dev.
DATA_DIR = Path(os.getenv("STUDIOCLEAR_DATA_DIR", "app/data"))
RUNS_DIR = DATA_DIR / "runs"

# The only actions a coordinator may take (sol.md §6 coordinator.human_actions).
HUMAN_ACTIONS = {"clear", "send_to_review", "escalate", "override"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(run_id: str) -> Path:
    return RUNS_DIR / f"{run_id}.json"


def save_run(report: dict) -> str:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_id = report["run_id"]
    _path(run_id).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return run_id


def load_run(run_id: str) -> dict | None:
    p = _path(run_id)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def list_runs() -> list[dict]:
    if not RUNS_DIR.exists():
        return []
    out = []
    for p in sorted(RUNS_DIR.glob("*.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        out.append({"run_id": r["run_id"], "title": r.get("title"),
                    "summary": r.get("summary", {})})
    return out


def apply_decision(run_id: str, item_id: str, action: str, reason: str = "") -> dict:
    """Record a human decision on one item and append it to the audit chain.

    Humans retain final authority (sol.md §14). `override` requires a reason and
    means the coordinator is overriding the agent recommendation — the agent's
    recommended state is preserved; the human_decision records the human's call.
    """
    if action not in HUMAN_ACTIONS:
        raise ValueError(f"unknown action: {action}")
    if action == "override" and not reason.strip():
        raise ValueError("override requires a reason")

    report = load_run(run_id)
    if report is None:
        raise KeyError(run_id)

    item = next((it for it in report["items"] if it["item_id"] == item_id), None)
    if item is None:
        raise KeyError(item_id)

    item["human_decision"] = {"action": action, "reason": reason, "at": _now()}

    # Append to the tamper-evident chain and re-verify.
    log = AuditLog.from_list(report.get("audit_chain", []))
    log.append({
        "action": "human_decision", "run_id": run_id, "item_id": item_id,
        "decision": action, "reason": reason,
        "agent_recommendation": item.get("state"),
    })
    report["audit_chain"] = log.to_list()
    report["governance"]["audit_events"] = len(log.events)
    report["governance"]["audit_verified"] = log.verify()
    report["governance"]["audit_head"] = log.head

    save_run(report)
    return item
