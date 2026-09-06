# Build Progress — StudioClear

Snapshot of what's built and verified vs. the plan in `sol.md`. Updated 2026-09-05.

## Verified working (live, with real credentials)

- **Real ADK agents (§25/§27 compliance lock — DONE).** Planner, Researcher, and
  Reviewer are genuine `google.adk` Agents (ADK 2.8.0). The Researcher runs via
  `Runner` and calls `parallel_search` as an ADK tool at runtime; URLs are read
  from the tool-response event, so evidence integrity holds. Full agentic run:
  `ADKSearchProvider` drove all 14 items → 14/14 evidence-backed, audit verified
  (`demo/adk_run.json`). Backend entry point visibly imports/initializes ADK +
  Parallel. `scripts/smoke_adk.py`, `/healthz` lists the agents.

- **Live Gemini extraction** — `gemini-2.5-pro` extracts all 14 seeded clearance
  items with correct types; the embedded prompt-injection line is ignored
  (treated as data, not instructions). `scripts/smoke_extract.py`.
- **Live Parallel research** — real multi-source evidence with genuine
  authoritative publishers (nasa.gov, cdc.gov, pmc.ncbi.nlm.nih.gov, who.int, …).
  `scripts/smoke_parallel.py`.
- **Full live spine** — PDF/MD → extract → plan → authorize(+DENY) → Parallel →
  integrity-enforce → policy → report + audit. Full run: 14/14 evidence-backed,
  multi-source 3/3, 100% traceable, 1 unauthorized blocked, audit verified.
- **FastAPI backend** — `/upload`, `/run`, `/report`, `/decision`, `/audit`,
  `/healthz`, served UI at `/`. Verified via uvicorn + curl and TestClient.
- **Producer UI** — `app/frontend/index.html`: summary tiles, item table,
  evidence drawer with source links, human clear/review/escalate/override,
  tamper-evident audit badge.
- **Human override → audit** — overrides append to the hash-chained audit log,
  which still verifies afterward.

## Tested (offline, deterministic — CI-safe)

- **40 tests pass**; **ruff clean**; golden gate **14/14 (0 missed)**.
- Pure modules are real + unit-tested: policy determinism, deterministic
  confidence, evidence-integrity invariant, AuthZ + DENY, hash-chained audit,
  recall-first metrics, planner, parser, pipeline end-to-end, API.
- `demo/cached_run.json` frozen for the demo/video (deterministic, shows the
  clean LunarFizz INSUFFICIENT-EVIDENCE narrative).

## Deployment (scaffolded, not applied)

- `Dockerfile` + `.dockerignore` for Cloud Run.
- `deploy/terraform/` — Cloud Run service + runtime SA + Secret Manager binding
  (the one real IAM check). `deploy/README.md` has gcloud + Terraform paths.

## Remaining (priority order)

1. **Deploy** to Cloud Run and verify the hosted app (Day-4). Dockerfile +
   Terraform ready; blocked only on `gcloud auth` + a GCP project.
2. **Record the 3-minute video** against `demo/cached_run.json` (sol.md E6).
3. **Demo tuning** — the fictional brand (LunarFizz) returns tangential live
   matches → ESCALATE; the cached/mock run shows the clean INSUFFICIENT-EVIDENCE
   honesty beat, so record the honesty moment from cached mode.

## Done

- ADK agent wiring (§25/§27) — see "Verified working" above.
- Public GitHub repo + MIT license: https://github.com/whitepaper27/Agentic_Cinema

## Run it

```bash
python -m venv .venv && .venv/Scripts/activate   # win
pip install -r requirements.txt
cp .env.example .env     # add Gemini_API_Key + Parallel_API_Key

pytest tests/                         # 40 pass, offline
python scripts/run_spine.py           # offline run -> cached_run.json
python scripts/smoke_extract.py       # live Gemini
python scripts/smoke_parallel.py      # live Parallel
uvicorn app.api.main:app --reload     # open http://127.0.0.1:8000
```
