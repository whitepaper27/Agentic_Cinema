# Build Progress — StudioClear

Snapshot of what's built and verified vs. the plan in `sol.md`. Updated 2026-09-05.

## Verified working (live, with real credentials)

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

1. **ADK agent wiring (compliance lock §25/§27).** Planner/Researcher/Reviewer
   are currently plain Python behind the provider interface; the track requires
   them as real `google.adk` Agents run via `Runner`, with the backend entry
   point visibly initializing ADK. The grouping/search/policy logic is already
   pure and tested — wrap it in ADK agents and call `parallel_search` as an ADK
   tool. **Top priority.**
2. **Demo tuning** — pick a fictional brand that reliably returns no
   authoritative match live, or rely on the cached run for the honesty beat.
3. **Deploy** to Cloud Run and verify the hosted app (Day-4).
4. **Record the 3-minute video** against `demo/cached_run.json` (sol.md E6).
5. **First git commit** + push public repo with MIT license (sol.md §27).

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
