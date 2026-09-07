"""StudioClear backend (sol.md §25 / §27 / E3.2).

Visibly initializes the two partner runtimes (ADK + Parallel — track
requirement) and exposes the producer workflow over HTTP, backed by the tested
pipeline and the Human Decision Desk. Providers auto-select live vs mock from
available credentials, so this serves a real run with a Gemini key and no
Parallel key (hybrid), or fully offline with neither.
"""

from __future__ import annotations

import base64
import binascii
import uuid
from datetime import datetime, timezone
from pathlib import Path

# --- Required partner runtimes, initialized at import for discoverability (§27) ---
import google.adk as adk  # noqa: E402,F401  (agent orchestration layer)
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from parallel import Parallel  # noqa: E402,F401  (runtime research/evidence engine)
from pydantic import BaseModel

from studioclear import revision, scene_store, store
from studioclear.agents.research_planner import build_planner  # noqa: E402
from studioclear.agents.researcher import build_researcher  # noqa: E402
from studioclear.agents.reviewer import build_reviewer  # noqa: E402
from studioclear.analyzer.script_parser import parse_screenplay_text
from studioclear.config import Config
from studioclear.contract.clearance_contract import load_policy
from studioclear.handoff import build_comparison_handoff, build_handoff
from studioclear.models import ClearanceItem
from studioclear.pipeline import run_pipeline
from studioclear.providers import (
    LiveKeysMissing,
    build_providers,
    build_providers_for_mode,
    describe_providers,
)
from studioclear.providers.mock import ExampleLLMProvider, ExampleProductionProvider
from studioclear.research_pipeline import run_research
from studioclear.scene_store import ExpiredError, OwnershipError
from studioclear.shoot_comparison import build_comparison

# The three ADK agents required by the track (§25/§27). Built lazily so the app
# starts without credentials, but their builders are real google.adk Agents.
ADK_AGENTS = ("research_planner", "researcher", "reviewer")

app = FastAPI(title="StudioClear", version="0.1.0")

UPLOADS = store.DATA_DIR / "uploads"
FRONTEND = Path("app/frontend/index.html")

# Fixed simulated-run timestamp; live runs stamp the actual server UTC time.
FIXTURE_NOW = "2026-09-05T12:00:00Z"


def _server_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.exception_handler(ExpiredError)
async def _expired_handler(request: Request, exc: ExpiredError) -> JSONResponse:
    # Material past its 24h lifecycle is gone from the application (sol.md §10).
    return JSONResponse(status_code=410,
                        content={"detail": "expired", "code": "gone"})


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


# ---------------- Schema-v2 scene/research workflow (sol.md §9) ----------------

# Input limits (sol.md §4). Enforced server-side; the UI mirrors them.
MAX_TEXT_CHARS = 20_000
MAX_IMAGES = 3
MAX_IMAGE_BYTES = 4 * 1024 * 1024
MAX_TOTAL_IMAGE_BYTES = 12 * 1024 * 1024
ALLOWED_IMAGE_MIME = {"image/png", "image/jpeg", "image/webp"}


class SceneRequest(BaseModel):
    mode: str = "live"                   # "live" | "example" (no silent fallback)
    source_type: str = "paste"           # "paste" | "images"
    title: str = "Untitled scene"
    task: str = "plan"                   # "plan" | "review" | "improve" (sol.md §5)
    instruction: str = ""
    script_text: str | None = None
    images: list[str] = []               # data: URLs, validated server-side
    locks: list[str] = []


class SceneUpdateRequest(BaseModel):
    expected_version: int
    scenes: list[dict] | None = None     # corrected transcript
    items: list[dict] | None = None      # corrected candidate claims
    instruction: str | None = None
    locks: list[str] | None = None


class RunRequest(BaseModel):
    scene_id: str
    mode: str = "live"                    # "live" | "example"
    use_adk: bool = False


class ReviseRequest(BaseModel):
    finding_id: str


class RevisionDecisionRequest(BaseModel):
    run_id: str
    action: str                          # "accept" | "reject"
    expected_version: int | None = None
    idempotency_key: str | None = None


class RecheckRequest(BaseModel):
    run_id: str                          # the prior (accepted) run
    mode: str | None = None              # defaults to the prior run's mode


class FindingDecisionRequest(BaseModel):
    action: str                          # "keep" | "review" | "escalate"
    note: str = ""


class CreativeProposalRequest(BaseModel):
    instruction: str = ""
    kind: str = "elaborate"              # "elaborate" | "dialogue"


class CreativeDecisionRequest(BaseModel):
    action: str                          # "accept" | "reject"
    expected_version: int | None = None


class ShootComparisonRequest(BaseModel):
    brief: dict = {}
    mode: str = "example"                # "live" | "example"
    parent_comparison_id: str | None = None


class ComparisonDecisionRequest(BaseModel):
    option_id: str
    rationale: str = ""
    idempotency_key: str | None = None


def _session(request: Request, response: Response) -> str:
    """Opaque per-visitor session id, set as an httponly cookie (sol.md §10)."""
    sid = request.cookies.get("sc_session")
    if not sid:
        sid = scene_store.new_id("sess")
        response.set_cookie("sc_session", sid, httponly=True, samesite="lax",
                            max_age=86_400)
    return sid


def _decode_images(data_urls: list[str]) -> list[dict]:
    """Validate and decode base64 data: URLs into {data, mime_type} (sol.md §4)."""
    if len(data_urls) > MAX_IMAGES:
        raise HTTPException(413, f"at most {MAX_IMAGES} pages")
    out: list[dict] = []
    total = 0
    for i, url in enumerate(data_urls, start=1):
        if not url.startswith("data:") or ";base64," not in url:
            raise HTTPException(422, f"page {i}: not a base64 data URL")
        header, b64 = url.split(";base64,", 1)
        mime = header[5:]
        if mime not in ALLOWED_IMAGE_MIME:
            raise HTTPException(422, f"page {i}: unsupported type {mime}")
        try:
            raw = base64.b64decode(b64, validate=True)
        except (binascii.Error, ValueError) as e:
            raise HTTPException(422, f"page {i}: undecodable image") from e
        if len(raw) > MAX_IMAGE_BYTES:
            raise HTTPException(413, f"page {i}: exceeds {MAX_IMAGE_BYTES} bytes")
        total += len(raw)
        if total > MAX_TOTAL_IMAGE_BYTES:
            raise HTTPException(413, "total image size exceeds limit")
        out.append({"data": raw, "mime_type": mime})
    return out


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


def _legacy_run(run_id: str) -> dict | None:
    report = store.load_run(run_id)
    if report is None:
        return None
    report.setdefault("agents", _agents_meta())
    report.setdefault("iam_checks", _iam_checks())
    return report


@app.get("/run/{run_id}")
def get_run(run_id: str, request: Request, response: Response) -> dict:
    """Read a run. Schema-v2 runs are session-scoped (scene_store); if none
    matches, fall back to the legacy run store for the labeled legacy demo."""
    owner = _session(request, response)
    try:
        v2 = scene_store.get_run(run_id, owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your run") from e
    if v2 is not None:
        return v2
    legacy = _legacy_run(run_id)
    if legacy is None:
        raise HTTPException(404, "run not found")
    return legacy


@app.get("/report/{run_id}")
def get_report(run_id: str, request: Request, response: Response) -> dict:
    """Sanitized production handoff — allowlisted schema, no owner/session/audit
    hashes (sol.md §9, sol_ui.md §10). Falls back to the legacy run for the
    labeled legacy demo."""
    owner = _session(request, response)
    try:
        run = scene_store.get_run(run_id, owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your run") from e
    if run is not None:
        scene = scene_store.get_scene(run["scene_id"], owner=owner)
        if scene is None:
            raise HTTPException(404, "scene not found")
        # Load earlier runs cited by accepted revisions so their sources resolve.
        origin_ids = {ref.get("origin_run_id")
                      for rev in run.get("revisions", []) if rev.get("status") == "accepted"
                      for ref in rev.get("evidence_refs", [])}
        historical = {}
        for oid in origin_ids:
            if oid and oid != run["run_id"]:
                try:
                    orun = scene_store.get_run(oid, owner=owner)
                except (OwnershipError, ExpiredError):
                    orun = None
                if orun:
                    historical[oid] = orun
        return build_handoff(run, scene, historical)
    legacy = _legacy_run(run_id)
    if legacy is None:
        raise HTTPException(404, "run not found")
    return legacy


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


# ---------------- Schema-v2 endpoints (sol.md §9) ----------------


def _extract_scene(req: SceneRequest):
    """Run extraction for a scene request; returns (draft_scenes, items, mode).

    Enforces no-silent-fallback: live mode without keys is a 503, never mock
    fixtures over user material (sol.md §12)."""
    try:
        providers = build_providers_for_mode(req.mode, use_adk=False)
    except LiveKeysMissing as e:
        raise HTTPException(503, f"live providers unavailable: missing {e}") from e
    except ValueError as e:
        raise HTTPException(422, str(e)) from e

    if req.source_type == "images":
        images = _decode_images(req.images)
        if not images:
            raise HTTPException(422, "no pages provided")
        items = providers.llm.extract_items_from_images(images)
        # Seed each page transcript from the text actually extracted for it, so the
        # confirm step is never a blank placeholder when readable text was found
        # (sol_ui.md §5). The user still corrects it before research.
        draft = []
        for p in range(1, len(images) + 1):
            page_text = " ".join(it.text_span for it in items if it.scene == p)
            draft.append({"scene": p, "text": page_text, "source": "image"})
    else:
        text = (req.script_text or "").strip()
        if not text:
            raise HTTPException(422, "no scene text provided")
        if len(text) > MAX_TEXT_CHARS:
            raise HTTPException(413, f"text exceeds {MAX_TEXT_CHARS} characters")
        draft = parse_screenplay_text(text)
        for s in draft:
            s["source"] = "paste"
        items = providers.llm.extract_items(draft)

    return draft, [it.model_dump(mode="json") for it in items], req.mode


@app.post("/scenes")
def create_scene(req: SceneRequest, request: Request, response: Response) -> dict:
    """Validate material, extract an editable draft, persist a v1 scene (sol.md §9)."""
    owner = _session(request, response)
    draft, items, mode = _extract_scene(req)
    scene = scene_store.create_scene(
        owner, source_type=req.source_type, title=req.title,
        instruction=req.instruction, draft_scenes=draft, items=items,
        provider_mode=mode, locks=req.locks, task=req.task,
    )
    return scene


@app.get("/scenes/{scene_id}")
def read_scene(scene_id: str, request: Request, response: Response) -> dict:
    """Read a scene (session-scoped) so the client can recover its current version."""
    owner = _session(request, response)
    try:
        scene = scene_store.get_scene(scene_id, owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your scene") from e
    if scene is None:
        raise HTTPException(404, "scene not found")
    return scene


@app.patch("/scenes/{scene_id}")
def update_scene(scene_id: str, req: SceneUpdateRequest, request: Request,
                 response: Response) -> dict:
    """Save a corrected transcript / intent / locks as a new scene version."""
    owner = _session(request, response)
    try:
        scene = scene_store.get_scene(scene_id, owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your scene") from e
    if scene is None:
        raise HTTPException(404, "scene not found")
    try:
        version = scene_store.update_scene_version(
            scene, expected_version=req.expected_version, scenes=req.scenes,
            items=req.items, instruction=req.instruction, locks=req.locks,
        )
    except ValueError as e:
        raise HTTPException(409, str(e)) from e
    return {"scene_id": scene_id, "current_version": scene["current_version"],
            "version": version}


@app.post("/runs")
def create_run(req: RunRequest, request: Request, response: Response) -> dict:
    """Research a confirmed scene version → schema-v2 findings (sol.md §7)."""
    owner = _session(request, response)
    try:
        scene = scene_store.get_scene(req.scene_id, owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your scene") from e
    if scene is None:
        raise HTTPException(404, "scene not found")

    try:
        providers = build_providers_for_mode(req.mode, use_adk=req.use_adk)
    except LiveKeysMissing as e:
        raise HTTPException(503, f"live providers unavailable: missing {e}") from e
    except ValueError as e:
        raise HTTPException(422, str(e)) from e

    version = scene_store.latest_version(scene)
    items = [ClearanceItem(**it) for it in version["items"]]
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    # Live runs stamp actual server UTC; a simulated run keeps its fixture time.
    now = _server_now() if req.mode == "live" else FIXTURE_NOW
    report = run_research(
        items, providers, run_id=run_id, scene_id=req.scene_id,
        scene_version=scene["current_version"], provider_mode=req.mode, now=now,
    )
    report["title"] = scene["title"]
    report["instruction"] = version.get("instruction", "")
    scene_store.save_run(report, owner, scene=scene)
    scene_store.register_run(scene, run_id)
    return report


def _load_run_and_scene(run_id: str, owner: str) -> tuple[dict, dict]:
    try:
        run = scene_store.get_run(run_id, owner=owner)
        if run is None:
            raise HTTPException(404, "run not found")
        scene = scene_store.get_scene(run["scene_id"], owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your run") from e
    if scene is None:
        raise HTTPException(404, "scene not found")
    return run, scene


def _providers_for(mode: str):
    try:
        return build_providers_for_mode(mode, use_adk=False)
    except LiveKeysMissing as e:
        raise HTTPException(503, f"live providers unavailable: missing {e}") from e
    except ValueError as e:
        raise HTTPException(422, str(e)) from e


@app.post("/runs/{run_id}/revisions")
def propose_revision(run_id: str, req: ReviseRequest, request: Request,
                     response: Response) -> dict:
    """Propose an evidence-backed edit against the current scene version (sol.md §8)."""
    owner = _session(request, response)
    run, scene = _load_run_and_scene(run_id, owner)
    providers = _providers_for(run.get("provider_mode", "example"))
    try:
        rev = revision.propose(run, scene, req.finding_id, providers)
    except KeyError as e:
        raise HTTPException(404, f"finding not found: {e}") from e
    except ValueError as e:
        # e.g. no_applicable_evidence, original_not_in_scene
        raise HTTPException(422, str(e)) from e
    scene_store.save_run(run, owner, scene=scene)
    return rev


@app.post("/revisions/{revision_id}/decision")
def decide_revision(revision_id: str, req: RevisionDecisionRequest,
                    request: Request, response: Response) -> dict:
    """Accept or reject a proposal; accept creates a new scene version (sol.md §8)."""
    owner = _session(request, response)
    run, scene = _load_run_and_scene(req.run_id, owner)
    try:
        out = revision.decide(run, scene, revision_id, req.action,
                              expected_version=req.expected_version,
                              idempotency_key=req.idempotency_key)
    except KeyError as e:
        raise HTTPException(404, f"revision not found: {e}") from e
    except ValueError as e:
        code = 409 if str(e) in ("stale_version", "lock_conflict") else 422
        raise HTTPException(code, str(e)) from e
    scene_store.save_run(run, owner, scene=scene)
    scene_store.save_scene(scene)
    return out


@app.post("/runs/{run_id}/findings/{finding_id}/decision")
def finding_decision(run_id: str, finding_id: str, req: FindingDecisionRequest,
                     request: Request, response: Response) -> dict:
    """Persist a human decision on a finding — 'keep' / 'review' / 'escalate' with
    an optional note. Recorded server-side so the UI can show 'Recorded' only after
    it succeeds (sol.md §8, sol_ui.md §6). Does not change the factual assessment."""
    owner = _session(request, response)
    run, _scene = _load_run_and_scene(run_id, owner)
    finding = next((f for f in run.get("findings", []) if f["finding_id"] == finding_id), None)
    if finding is None:
        raise HTTPException(404, "finding not found")
    if req.action not in ("keep", "review", "escalate"):
        raise HTTPException(422, "unknown action")
    finding["human_decision"] = {"action": req.action, "note": req.note,
                                 "at": _server_now()}
    scene_store.save_run(run, owner)
    return {"finding_id": finding_id, "human_decision": finding["human_decision"]}


@app.post("/scenes/{scene_id}/recheck")
def recheck_scene(scene_id: str, req: RecheckRequest, request: Request,
                  response: Response) -> dict:
    """Re-research the changed scene version and report claim lineage (sol.md §8)."""
    owner = _session(request, response)
    prior, scene = _load_run_and_scene(req.run_id, owner)
    if scene["scene_id"] != scene_id:
        raise HTTPException(422, "scene_id does not match the run")
    mode = req.mode or prior.get("provider_mode", "example")
    providers = _providers_for(mode)
    new_run_id = f"run_{uuid.uuid4().hex[:8]}"
    new_run = revision.recheck(scene, providers, prior, new_run_id, provider_mode=mode)
    new_run["title"] = scene["title"]
    scene_store.save_run(new_run, owner, scene=scene)
    scene_store.register_run(scene, new_run_id)
    return new_run


@app.delete("/scenes/{scene_id}")
def delete_scene(scene_id: str, request: Request, response: Response) -> dict:
    """User-triggered delete: revoke access and remove related objects (sol.md §10)."""
    owner = _session(request, response)
    try:
        scene_store.delete_scene(scene_id, owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your scene") from e
    return {"deleted": scene_id}


# ---------------- Creative proposals (sol.md §7 — no evidence required) ----------------


@app.post("/scenes/{scene_id}/creative-proposals")
def create_creative_proposal(scene_id: str, req: CreativeProposalRequest,
                             request: Request, response: Response) -> dict:
    """Propose AI-authored scene text; needs no factual finding (sol.md §7)."""
    owner = _session(request, response)
    try:
        scene = scene_store.get_scene(scene_id, owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your scene") from e
    if scene is None:
        raise HTTPException(404, "scene not found")
    providers = _providers_for(scene.get("provider_mode", "example"))
    try:
        rev = revision.propose_creative(scene, req.instruction, req.kind, providers)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    scene_store.save_scene(scene)
    return rev


@app.post("/scenes/{scene_id}/creative-proposals/{proposal_id}/decision")
def decide_creative_proposal(scene_id: str, proposal_id: str,
                             req: CreativeDecisionRequest, request: Request,
                             response: Response) -> dict:
    """Accept or reject a creative proposal; accept creates a new scene version."""
    owner = _session(request, response)
    try:
        scene = scene_store.get_scene(scene_id, owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your scene") from e
    if scene is None:
        raise HTTPException(404, "scene not found")
    try:
        out = revision.decide_creative(scene, proposal_id, req.action,
                                       expected_version=req.expected_version)
    except KeyError as e:
        raise HTTPException(404, f"proposal not found: {e}") from e
    except ValueError as e:
        code = 409 if str(e) == "stale_version" else 422
        raise HTTPException(code, str(e)) from e
    scene_store.save_scene(scene)
    return out


# ---------------- Shoot comparison (sol.md §6A / §9) ----------------


@app.post("/scenes/{scene_id}/location-suggestions")
def suggest_locations(scene_id: str, req: ShootComparisonRequest, request: Request,
                      response: Response) -> dict:
    """Suggest candidate alternative filming locations to research (sol.md §6A).
    Leads only — never a feasibility, permission, or cost claim."""
    owner = _session(request, response)
    try:
        scene = scene_store.get_scene(scene_id, owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your scene") from e
    if scene is None:
        raise HTTPException(404, "scene not found")

    version = scene_store.latest_version(scene)
    scene_text = "\n\n".join(s.get("text", "") for s in version["scenes"])
    instruction = scene.get("instruction", "")

    sources: list[dict] = []
    if req.mode == "example":
        candidates = ExampleLLMProvider().suggest_locations(scene_text, instruction)
    elif req.mode == "live":
        cfg = Config.from_env()
        if not cfg.gemini_api_key:
            raise HTTPException(503, "live location suggestions need a Gemini key")
        from studioclear.providers.gemini import GeminiLLMProvider
        candidates = GeminiLLMProvider().suggest_locations(scene_text, instruction)
        if cfg.parallel_api_key and candidates:
            from studioclear.providers.parallel import ParallelSearchProvider
            from studioclear.providers.production import LiveProductionProvider
            lp = LiveProductionProvider(ParallelSearchProvider())
            leads = lp._search(f"film incentives and locations {candidates[0]['name']}")
            for i, r in enumerate(leads[:3]):
                sources.append({"source_id": f"L{i + 1:03d}", "url": r.get("source_url", ""),
                                "title": r.get("title", ""), "provenance": "sourced_lead"})
    else:
        raise HTTPException(422, f"unknown mode: {req.mode}")
    return {"candidates": candidates, "sources": sources, "mode": req.mode}


@app.post("/scenes/{scene_id}/shoot-comparisons")
def create_shoot_comparison(scene_id: str, req: ShootComparisonRequest,
                            request: Request, response: Response) -> dict:
    """Research + calculate a three-option production comparison (sol.md §6A)."""
    owner = _session(request, response)
    try:
        scene = scene_store.get_scene(scene_id, owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your scene") from e
    if scene is None:
        raise HTTPException(404, "scene not found")

    if req.mode == "example":
        provider = ExampleProductionProvider()
    elif req.mode == "live":
        cfg = Config.from_env()
        if not cfg.parallel_api_key:
            raise HTTPException(503, "live production research needs a Parallel key")
        from studioclear.providers.parallel import ParallelSearchProvider
        from studioclear.providers.production import LiveProductionProvider
        provider = LiveProductionProvider(ParallelSearchProvider())
    else:
        raise HTTPException(422, f"unknown mode: {req.mode}")

    calc_version = 1
    if req.parent_comparison_id:
        parent = scene_store.get_comparison(req.parent_comparison_id, owner=owner)
        if parent is not None:
            calc_version = int(parent.get("calculation_version", 1)) + 1

    now = _server_now() if req.mode == "live" else FIXTURE_NOW
    comp = build_comparison(scene, req.brief, provider,
                            comparison_id=f"cmp_{uuid.uuid4().hex[:8]}",
                            provider_mode=req.mode, parent_id=req.parent_comparison_id,
                            calculation_version=calc_version, now=now)
    scene_store.save_comparison(comp, owner, scene=scene)
    scene_store.register_comparison(scene, comp["comparison_id"])
    return comp


@app.get("/shoot-comparisons/{comparison_id}")
def get_shoot_comparison(comparison_id: str, request: Request,
                         response: Response) -> dict:
    owner = _session(request, response)
    try:
        comp = scene_store.get_comparison(comparison_id, owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your comparison") from e
    if comp is None:
        raise HTTPException(404, "comparison not found")
    return comp


@app.post("/shoot-comparisons/{comparison_id}/decision")
def decide_shoot_comparison(comparison_id: str, req: ComparisonDecisionRequest,
                            request: Request, response: Response) -> dict:
    """Persist the producer's option choice for further planning (no booking)."""
    owner = _session(request, response)
    try:
        comp = scene_store.get_comparison(comparison_id, owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your comparison") from e
    if comp is None:
        raise HTTPException(404, "comparison not found")
    if req.option_id not in {o["option_id"] for o in comp.get("options", [])}:
        raise HTTPException(422, "unknown option_id")
    existing = comp.get("decision")
    if existing and req.idempotency_key and existing.get("idempotency_key") == req.idempotency_key:
        return {"selected": existing["option_id"], "decision": existing}
    comp["decision"] = {"option_id": req.option_id, "rationale": req.rationale,
                        "selected_for_planning": True, "at": _server_now(),
                        "idempotency_key": req.idempotency_key}
    scene_store.save_comparison(comp, owner)
    return {"selected": req.option_id, "decision": comp["decision"]}


@app.get("/shoot-comparisons/{comparison_id}/handoff")
def get_comparison_handoff(comparison_id: str, request: Request,
                           response: Response) -> dict:
    """One sanitized production planning brief snapshot (sol.md §9)."""
    owner = _session(request, response)
    try:
        comp = scene_store.get_comparison(comparison_id, owner=owner)
        if comp is None:
            raise HTTPException(404, "comparison not found")
        scene = scene_store.get_scene(comp["scene_id"], owner=owner)
    except OwnershipError as e:
        raise HTTPException(403, "not your comparison") from e
    if scene is None:
        raise HTTPException(404, "scene not found")
    return build_comparison_handoff(comp, scene)
