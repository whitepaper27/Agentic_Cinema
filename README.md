# StudioClear — Scene Research & Revision Desk

**Google Cloud Agentic Cinema — Parallel Track**

[![CI](https://github.com/whitepaper27/Agentic_Cinema/actions/workflows/ci.yml/badge.svg)](https://github.com/whitepaper27/Agentic_Cinema/actions/workflows/ci.yml)
&nbsp;License: MIT &nbsp;·&nbsp; Google ADK 2.8 &nbsp;·&nbsp; Gemini 2.5 (text + vision) &nbsp;·&nbsp; Parallel Search

**🔗 Live demo:** https://studioclear-602811764567.us-central1.run.app — click
**"Try an example"** to run the deterministic showcase, or paste your own scene /
upload a storyboard page to run it live.

> **Bring your storyboard or scene. StudioClear investigates questionable
> details and helps you make the smallest evidence-backed correction while
> preserving your creative intent.**

A filmmaker brings an unfamiliar scene, gives one instruction, inspects the
evidence, accepts a single constrained revision, rechecks the changed scene, and
exports a production handoff. **Gemini** reads and reasons about the material;
**Parallel** supplies the retrieved evidence that drives the revision; **Google
Cloud** hosts the app and controls its resource access.

It does **not** issue legal clearance, redraw artwork, or establish a person's
identity from a drawing. Authoritative specs: [`sol.md`](./sol.md) (product,
evidence, gates) and [`sol_ui.md`](./sol_ui.md) (UX).

---

## The loop

```
Bring a scene → State intent → Confirm extraction → Investigate
    → Propose a small revision → Accept or reject → Recheck → Export
```

The differentiated moment is an **observable, evidence-backed correction**:
changing a researched detail changes the relevant finding while protected
dialogue stays intact, and an ambiguous second finding is honestly left
unresolved. That demonstrates perception, research, user control, and
verification in one workflow.

**Showcase (Try an example):** a scene claims *"the Apollo 11 Moon landing in
1968."* Research returns a NASA primary source dated 1969 → the finding reads
**Evidence challenges this detail (CONTRADICTED)**. You propose the smallest fix,
accept it, and recheck → the corrected claim now reads **Supported by retrieved
evidence**. A separate ambiguous detail stays **Not enough evidence**.

---

## What makes it credible (not just a demo)

- **Evidence is grounded in code, not the model.** The model selects a stored
  `source_id` and quotes a retrieved passage — it can **never** supply a URL.
  Code resolves every reference back to a stored source and **rejects unknown
  IDs and invented quotes**. `research/evidence_normalizer.py:resolve_assessments`,
  `tests/adversarial/test_evidence_resolution.py`.
- **Research status is deterministic.** Validated assessments map to
  **SUPPORTED / CONTRADICTED / MIXED / UNRESOLVED / NOT_RESEARCHED / STALE** by
  pure code — context-only sources can't clear a claim, one syndicated story
  isn't corroboration, and an applicable contradiction is never washed out by
  weak support. `contract/policy_evaluator.py:assess_research_status`,
  `tests/unit/test_research_status.py`.
- **No fabricated confidence.** Quality percentages were removed; the UI shows
  evidence coverage and limitations instead (sol.md §7).
- **Research vs. human routing are separate.** A factually SUPPORTED item can
  still route to a human for rights/likeness review. Brand/music/likeness route
  to a person; web search does not resolve them.
- **Honest failure modes.** Live mode without keys returns a 503 and **never**
  substitutes fixtures over your material; empty extraction says so; the
  "example" is always labeled **Simulated example**, live runs **Processed live**.
- **Governance you can inspect.** An authorization self-test denies an unapproved
  tool at the tool boundary; every run keeps a hash-chained event log
  ("Chain consistency verified" — not a tamper-proof claim). `security/`.
- **Human authority by design.** No "cleared by AI" state exists.

---

## Architecture

```
Browser: pages/text + instruction + locked spans
  → POST /scenes    validate + persist source, Gemini extraction (vision|text)
  → confirm/correct the editable draft            PATCH /scenes/{id}  (new version)
  → POST /runs      authorize each tool call, Parallel search,
                    Gemini grades passages by source_id, CODE resolves + scores
  → POST /runs/{id}/revisions       smallest evidence-backed edit (no mutation)
  → POST /revisions/{id}/decision   accept → new immutable scene version
  → POST /scenes/{id}/recheck       re-extract + re-research, claim lineage
  → GET  /report/{id}               versioned production handoff (text/PDF/JSON)
```

- **Schema-v2 pipeline:** `studioclear/research_pipeline.py`.
- **Revision/recheck:** `studioclear/revision.py`; **storage + versions +
  session ownership:** `studioclear/scene_store.py`.
- **Providers:** `build_providers_for_mode("live"|"example")` — live is real
  Gemini + Parallel (keys required, no fallback); example is deterministic
  fixtures (`demo/example_*.json`). ADK research path retained.
- **Frontend:** `app/frontend/index.html`, four views — **Analyze a scene /
  Scene desk / Handoff / Execution** — vanilla JS, no build.
- **Hosting:** Google Cloud Run; API keys in **Secret Manager**; the runtime
  service account's only privileged grant is `secretAccessor` on those secrets.

The legacy clearance-viewer (`/upload`, `run_pipeline`) is retained only as a
clearly-labeled legacy demo.

---

## Try it

**Hosted UI (no setup):** open the live URL, click **Try an example**, then walk
Analyze → Scene desk → propose/accept a revision → recheck → Handoff. Or paste
your own scene / upload up to three storyboard pages to run it live.

**One curl — the deterministic example flow (no keys):**
```bash
BASE=https://studioclear-602811764567.us-central1.run.app
# 1) bring a scene (simulated example providers)
SCENE=$(curl -s -X POST $BASE/scenes -H 'Content-Type: application/json' \
  -d '{"mode":"example","source_type":"paste","title":"Demo",
       "script_text":"It was the Apollo 11 Moon landing in 1968 that changed everything."}')
SID=$(echo "$SCENE" | python -c "import sys,json;print(json.load(sys.stdin)['scene_id'])")
# 2) research it → findings with research status (one CONTRADICTED)
curl -s -X POST $BASE/runs -H 'Content-Type: application/json' \
  -d "{\"scene_id\":\"$SID\",\"mode\":\"example\"}" | python -m json.tool
```
Health check: `GET /health` (lists ADK 2.8 + the three agents). `/healthz` is
reserved by Google's front end on `*.run.app` — use `/health`.

---

## Quickstart (local)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # add GEMINI_API_KEY + PARALLEL_API_KEY for live mode

uvicorn app.api.main:app --reload        # http://127.0.0.1:8000  (UI at /)
```

Example mode needs no keys. Live mode (real Gemini + Parallel) reads
`GEMINI_API_KEY` / `PARALLEL_API_KEY` from `.env`.

## Testing & CI

```bash
pytest tests/                                   # 98 passing, offline/deterministic
ruff check studioclear tests app                # lint
```

- `tests/unit`, `tests/adversarial` — pure logic: status mapping, evidence
  resolution (unknown IDs / invented quotes), routing, parser.
- `tests/integration` — the schema-v2 pipeline, scene/run API, and the full
  revision→accept→recheck flow (including the CONTRADICTED→SUPPORTED flip).

## Limitations & scope (honest)

- **Text revisions only** — dialogue/captions + panel-specific notes. Uploaded
  artwork is never modified; a needed drawing change is exported as a pending art
  note and is not verified as visually applied.
- **Visual references are candidates** — StudioClear does not infer identity,
  ownership, permission, or likeness from a drawing.
- **Durable hosting** — a pluggable storage backend is in place
  (`studioclear/storage_backend.py`): local JSON for dev, a private GCS bucket
  when `STUDIOCLEAR_GCS_BUCKET` is set (writes use a generation precondition).
  To enable multi-instance durability, provision a private bucket, grant the Cloud
  Run runtime service account `roles/storage.objectAdmin` on it, and redeploy with
  `--set-env-vars STUDIOCLEAR_GCS_BUCKET=<bucket>` (drop `--max-instances 1`).
  The hosted bucket has a **24h delete lifecycle** with soft-delete disabled, so
  uploads are physically removed within a day (sol.md §10). Full read-modify-write
  CAS is a follow-up. PDF/DOCX import is deferred.
- **Not legal advice** — StudioClear researches and recommends; humans retain
  final authority and no "cleared by AI" state exists.

Demo content uses real brands/people in **neutral factual context only** and no
third-party logos, slogans, or trademark graphics.

## License

[MIT](./LICENSE)
