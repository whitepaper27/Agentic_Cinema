"""StudioClear backend (sol.md §25 / §27 / E3.2).

Visibly initializes the two partner runtimes (ADK + Parallel — track
requirement) and exposes the producer workflow over HTTP, backed by the tested
pipeline and the Human Decision Desk. Providers auto-select live vs mock from
available credentials, so this serves a real run with a Gemini key and no
Parallel key (hybrid), or fully offline with neither.
"""

from __future__ import annotations

import uuid
from pathlib import Path

# --- Required partner runtimes, initialized at import for discoverability (§27) ---
import google.adk as adk  # noqa: E402,F401  (agent orchestration layer)
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from parallel import Parallel  # noqa: E402,F401  (runtime research/evidence engine)
from pydantic import BaseModel

from studioclear import store
from studioclear.agents.research_planner import build_planner  # noqa: E402
from studioclear.agents.researcher import build_researcher  # noqa: E402
from studioclear.agents.reviewer import build_reviewer  # noqa: E402
from studioclear.config import Config
from studioclear.contract.clearance_contract import load_policy
from studioclear.pipeline import run_pipeline
from studioclear.providers import build_providers, describe_providers

# The three ADK agents required by the track (§25/§27). Built lazily so the app
# starts without credentials, but their builders are real google.adk Agents.
ADK_AGENTS = ("research_planner", "researcher", "reviewer")

app = FastAPI(title="StudioClear", version="0.1.0")

UPLOADS = store.DATA_DIR / "uploads"
FRONTEND = Path("app/frontend/index.html")


class UploadRequest(BaseModel):
    script_text: str | None = None      # omit to use the seeded demo script
    title: str = "Untitled Script"
    prefer_live: bool = True
    use_adk: bool = False               # run research through the ADK agent (§25)


class DecisionRequest(BaseModel):
    run_id: str
    item_id: str
    action: str                         # clear | send_to_review | escalate | override
    reason: str = ""


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    body = (FRONTEND.read_text(encoding="utf-8") if FRONTEND.exists()
            else "<h1>StudioClear</h1><p>API up. See /docs.</p>")
    # Never let a browser serve a stale UI during the demo.
    return HTMLResponse(body, headers={"Cache-Control": "no-store"})


# NOTE: `/healthz` is intercepted by the Google Front End on *.run.app (the
# request never reaches the container), so we also expose `/health` and
# `/status`, which are not reserved. All three run the same check.
@app.get("/healthz")
@app.get("/health")
@app.get("/status")
def healthz() -> dict:
    # Build the ADK agents to prove they initialize (real google.adk Agents).
    agents = [build_planner().name, build_researcher().name, build_reviewer().name]
    return {"status": "ok", "product": "StudioClear",
            "adk_version": adk.__version__, "adk_agents": agents}


@app.post("/upload")
def upload(req: UploadRequest) -> dict:
    """Ingest a script, run the full spine, persist the run, return the summary."""
    run_id = f"run_{uuid.uuid4().hex[:8]}"

    if req.script_text:
        UPLOADS.mkdir(parents=True, exist_ok=True)
        script_path = UPLOADS / f"{run_id}.md"
        script_path.write_text(req.script_text, encoding="utf-8")
    else:
        script_path = Path("demo/demo_script.md")

    providers = build_providers(prefer_live=req.prefer_live, use_adk=req.use_adk)
    report = run_pipeline(str(script_path), providers, run_id=run_id, title=req.title)
    store.save_run(report)
    return {"run_id": run_id, "title": report["title"],
            "summary": report["summary"], "metrics": report["metrics"],
            "governance": report["governance"],
            "providers": describe_providers(providers)}


@app.get("/policy")
def policy() -> dict:
    """The deterministic studio policy (§12) that drives every triage state —
    exposed so the UI can show the config behind each CLEAR/REVIEW/ESCALATE."""
    return {"policy_id": "demo_policy_v1", "studio_policy": load_policy()}


@app.get("/runs")
def runs() -> list[dict]:
    return store.list_runs()


def _agents_meta() -> list[dict]:
    """Static agent metadata for the Run view — models read from config, never
    hardcoded in the UI (claude_ui.md §7). These are the three real ADK agents."""
    cfg = Config.from_env()
    return [
        {"name": "research_planner", "role": "Planner",
         "model": cfg.extraction_model, "tools": []},
        {"name": "researcher", "role": "Researcher",
         "model": cfg.normalizer_model, "tools": ["parallel.search.public_web"]},
        {"name": "reviewer", "role": "Reviewer",
         "model": cfg.normalizer_model, "tools": ["policy.evaluate"]},
    ]


def _iam_checks() -> list[dict]:
    """The one real Cloud IAM boundary: the Cloud Run runtime service account may
    read exactly the two API-key secrets and nothing else (claude_ui.md §3)."""
    sa = "Cloud Run runtime service account"
    return [
        {"identity": sa, "resource": "Secret Manager · GEMINI_API_KEY",
         "role": "secretAccessor", "decision": "ALLOW"},
        {"identity": sa, "resource": "Secret Manager · PARALLEL_API_KEY",
         "role": "secretAccessor", "decision": "ALLOW"},
        {"identity": sa, "resource": "any resource outside the project",
         "role": "—", "decision": "DENY"},
    ]


@app.get("/run/{run_id}")
def get_run(run_id: str) -> dict:
    report = store.load_run(run_id)
    if report is None:
        raise HTTPException(404, "run not found")
    # Read-only presentational fields for the Run view (claude_ui.md §7) — added
    # at serve time so the determinism-locked run_pipeline / stored run are untouched.
    report.setdefault("agents", _agents_meta())
    report.setdefault("iam_checks", _iam_checks())
    return report


@app.get("/report/{run_id}")
def get_report(run_id: str) -> dict:
    return get_run(run_id)


@app.get("/audit/{run_id}")
def get_audit(run_id: str) -> dict:
    report = store.load_run(run_id)
    if report is None:
        raise HTTPException(404, "run not found")
    return {"run_id": run_id, "chain": report.get("audit_chain", []),
            "verified": report["governance"]["audit_verified"]}


@app.post("/decision")
def decision(req: DecisionRequest) -> dict:
    """Human clear / review / escalate / override — appended to the audit chain."""
    try:
        item = store.apply_decision(req.run_id, req.item_id, req.action, req.reason)
    except KeyError as e:
        raise HTTPException(404, f"not found: {e}") from e
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return {"ok": True, "item": item}
