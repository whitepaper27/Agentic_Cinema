# CLAUDE.md — StudioClear (Agentic Cinema hackathon)

Working notes for Claude Code. Read this first each session.

> **⚠️ PRODUCT = scene-to-production PLANNING desk (Sep 8 2026).** Reframed again
> from the research/revision desk to a **shoot-comparison** product: bring a scene →
> pick a task → (Plan) compare three ways to film it with real evidence + editable
> costs → change a constraint → select → export a planning brief. Research/revision
> is now the *optional* "Scene review". Authoritative specs: **`sol.md`** +
> **`sol_ui.md`**. `claude_ui.md`/`PROGRESS.md` are historical. Current state below.

## Current product (Sep 8) — what actually exists

- **Differentiator = shoot comparison (sol.md §6A).** `studioclear/cost_engine.py`
  (Decimal ranges, subtotal of KNOWN lines, contingency once, shared-expense de-dup,
  unknown→incomplete NEVER zero, overlap-aware compare, conditional incentives) +
  `studioclear/shoot_comparison.py` (three fixed slots NEARBY_PRACTICAL /
  TRAVEL_PRACTICAL / LOCAL_VFX, honest recommendation). Costs respond to the brief.
- **Production providers:** `ExampleProductionProvider` (deterministic, mock.py) and
  `LiveProductionProvider` (providers/production.py — runs REAL Parallel searches for
  leads; rates come from the producer brief as `estimate` or stay `quote needed`;
  **never fabricates prices**). Live comparison → 503 without a Parallel key.
- **Location suggestions (sol.md §6A):** `LLMProvider.suggest_locations` (mock
  deterministic; live Gemini proposes scene-aware candidates + Parallel leads).
  `POST /scenes/{id}/location-suggestions`. Leads only — never feasibility/cost.
- **Task + creative + evidence:** scenes carry `task` (plan|review|improve, default
  plan; NO silent historical-accuracy fallback; fantasy preserved in the extraction
  prompt). Creative proposals (`revision.propose_creative/decide_creative`, no
  citations, AI-labeled) via `POST /scenes/{id}/creative-proposals`. Evidence
  contract + research status (SUPPORTED/CONTRADICTED/MIXED/UNRESOLVED/…) + recheck
  RE-EXTRACTS the changed scene (Signal Room gate) — all still present under review.
- **API (sol.md §9):** scenes `POST/GET/PATCH/DELETE /scenes[/{id}]`; runs `POST /runs`,
  `GET /run/{id}`, revisions/decision/recheck; findings `/keep` decision;
  **comparison** `POST/GET /scenes/{id}/shoot-comparisons`, `GET
  /shoot-comparisons/{id}`, `/decision`, `/handoff`; `/location-suggestions`;
  `/report/{id}` (sanitized handoff). Session cookie `sc_session`, 24h expiry (410).
- **Providers select by mode:** `build_providers_for_mode("live"|"example")` — live
  requires keys (503, never mock fallback); example = text-aware `ExampleLLMProvider`
  + `ExampleSearchProvider` (`demo/example_*.json` is legacy, no longer used).
- **Frontend:** `app/frontend/index.html` — views Analyze (task selector, "Find a
  practical way to film your scene") / **Shoot options** (brief + rate estimates,
  suggest-locations chips, 3 cost cards, recalc, select, download brief) / Scene desk
  / Handoff / Execution. Verified via jsdom (`scratchpad/drive_*.js`), no JS errors.
- **Tests:** 144 passing (`pytest tests/`), `ruff check studioclear tests app` clean.
- **Hosting:** LIVE + durable. GCS bucket `studioclear-runs-602811764567` (24h
  lifecycle: `daysSinceCustomTime:1`+`age:1`, soft-delete off), runtime SA has
  `objectAdmin`. Deployed default-scaled. Latest revision `studioclear-00017-gvj`.
  Redeploy cmd includes `--set-env-vars STUDIOCLEAR_GCS_BUCKET=...,STUDIOCLEAR_DATA_DIR=/tmp/studioclear`.

## What this is

**StudioClear** — an agentic *script clearance research desk* for the **Google
Cloud Agentic Cinema hackathon, Parallel track**. A producer uploads a
screenplay; it extracts real-world references/claims (Gemini), researches them
for cited multi-source evidence (Parallel), applies a deterministic studio
policy → CLEAR / REVIEW / ESCALATE / INSUFFICIENT, keeps humans in final
authority, and audits everything. It does **not** issue legal clearance.

- **Full frozen plan:** `sol.md` (execution plan in Part I, product/compliance in Part II). It is the source of truth — section refs like §27, E8.1 point there.
- **Live status / what's next:** `PROGRESS.md`.
- **Deadline:** Sep 9 2026, 2:00 PM PT. Repo: https://github.com/whitepaper27/Agentic_Cinema (public, MIT).

## Current status (as of Sep 7)

Working and tested **live** (real Gemini + Parallel keys): full spine, FastAPI
backend + UI, human override→audit, and **real ADK agents** (the §25/§27
compliance lock is CLOSED — Planner/Researcher/Reviewer are `google.adk` Agents;
Researcher calls `parallel_search` as an ADK tool at runtime). CI is green (**45
tests**). **DEPLOYED & verified live on Cloud Run:**
https://studioclear-602811764567.us-central1.run.app (project
`gen-lang-client-0406755615`, region `us-central1`, keys in Secret Manager,
`--max-instances 3`). A live `/upload` returns real Gemini+Parallel providers,
14/14 evidence-backed, audit verified.

**UI was rebuilt Sep 7 to the `claude_ui.md` spec** — a three-view **Decision
desk / Run / Report** (light "archival binder", IBM Plex Sans + Courier Prime,
verdict-as-inked-stamp). See the "UI" section below. **Remaining: (1) a human
visual eyeball of the new UI** (browser automation was unavailable, so it's
data-verified via a jsdom headless render but not eyeballed); **(2) record the
3-min video.** Do NOT re-do finished work — check PROGRESS.md.

## How to run

```bash
# Windows, from D:\Eb1\Hackathon
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt          # or the .venv already exists
cp .env.example .env                       # keys already in .env (gitignored)

pytest tests/                              # 45 pass, offline/deterministic
python scripts/run_spine.py                # offline mock run -> demo/cached_run.json
python scripts/smoke_gemini.py             # live Gemini
python scripts/smoke_parallel.py           # live Parallel
python scripts/smoke_extract.py            # live Gemini extraction (14 items)
python scripts/smoke_adk.py                # live ADK researcher -> Parallel tool
uvicorn app.api.main:app --reload          # http://127.0.0.1:8000  (UI at /)
ruff check studioclear tests               # lint
```

The venv already has all deps installed (pydantic, pyyaml, fastapi, uvicorn,
google-genai, google-adk, parallel-web, python-dotenv, pytest, ruff).

## Architecture (where things live)

- `studioclear/pipeline.py` — the spine: parse → extract → plan → authorize(+DENY) → search → integrity-enforce → policy → report + audit. Provider-agnostic.
- `studioclear/providers/` — **the swap layer.** `build_providers(prefer_live, use_adk)`: mock (offline, deterministic) / live Gemini+Parallel / ADK. Same downstream code.
  - `mock.py` replays `demo/mock_extraction.json` + `demo/mock_evidence.json`.
  - `gemini.py`, `parallel.py` — real adapters. `adk_search.py` — ADK researcher agent as a SearchProvider.
- `studioclear/agents/` — real ADK agents: `research_planner.py`, `researcher.py`, `reviewer.py`, plus `tools.py` (parallel_search, apply_policy) and `adk_runtime.py`.
- `studioclear/contract/policy_evaluator.py` — deterministic policy (§12). `policy/demo_policy_v1.yaml`.
- `studioclear/research/evidence_normalizer.py` — the **evidence-integrity invariant** + deterministic confidence.
- `studioclear/security/` — `authorization.py` (AuthZ + DENY), `tool_registry.py`, `audit.py` (hash-chained), `secrets.py`.
- `studioclear/store.py` — JSON run store + Human Decision Desk (override → appends to audit chain).
- `app/api/main.py` — FastAPI: `/upload`, `/run/{id}` (injects read-only `agents[]` + `iam_checks[]` at serve time), `/report`, `/decision`, `/audit`, `/policy` (studio-policy rules for the UI), `/health` (+`/status`, `/healthz`). `/` serves the UI with `Cache-Control: no-store`.
- `app/frontend/index.html` — single-page UI (vanilla JS, no build), the **three-view Decision desk** per `claude_ui.md`.
- `demo/` — seeded script, `expected_items.json` (golden), `cached_run.json` (deterministic demo artifact), `adk_run.json` (agentic sample).

## UI (spec of record: `claude_ui.md`)

`app/frontend/index.html` is built to **`claude_ui.md`** (repo root) — the
authoritative UI spec; it supersedes the earlier `sol_ui.md` / dark "Clearance
Desk" drafts (now stale). Three views: **Decision desk** (default; queue by
what-needs-the-producer, evidence pane is the hero), **Run** (execution list +
StudioClear-AuthZ vs Cloud-IAM columns + audit table; the one DENY renders in
three places), **Report** (printable, totals computed client-side). Identity:
archival-binder light palette, **IBM Plex Sans + Courier Prime via Google Fonts**
(with system fallbacks), verdict as a rotated inked stamp.
- **Deliberate deviations from the spec (stay honest):** no fabricated
  timestamps (audit events carry none → uses sequence + verifiable hash +
  `generated_at`); "Run live" is one blocking `/upload` call, not 2s polling
  (the run isn't queryable mid-flight and the spec barred pipeline/endpoint
  changes); no invented `plan.replanned` event.
- **Design skill:** the official Anthropic **`frontend-design`** skill is
  installed at `~/.claude/skills/` — invoke it for visual work. `brand-guidelines`
  is also installed but do NOT apply it (that's Anthropic's brand, not StudioClear).
- **Verify UI without a browser:** jsdom headless render — `cd scratchpad &&
  npm i jsdom && node rendertest.js` against a local `uvicorn` on the given port
  (checks every view renders with no JS errors). Snapshots via `snapshot.js`.

## Conventions / invariants (do not break)

- **Evidence integrity (E8.1):** the LLM must NEVER emit a `source_url`. URLs pass through verbatim from the search tool/API. `enforce_grounded_sources` guards it; `tests/adversarial/test_evidence_integrity.py` proves it. This is the product's core credibility — never regress it.
- **Determinism / no fake scores (§20):** policy state and `confidence` are pure functions of inputs. Don't introduce LLM-guessed states or unearned "calibration".
- **Human authority (§14):** no "legally cleared by AI" state exists by design.
- **Demo-safety (§4/§27):** real brands/people in NEUTRAL factual context only; fictional brand (LunarFizz) for any negative context; no logos/slogans.
- **Keep CI green:** `ruff check studioclear tests` + `pytest tests/` before every push. Bare `pytest` works via root `conftest.py` (don't delete it).
- **ADK compliance is closed — keep it that way:** the three agents must stay real `google.adk` Agents and the backend must visibly init ADK + Parallel.

## Key facts / gotchas

- **Env keys** live in `.env` (gitignored, NEVER commit): `Gemini_API_Key`, `Parallel_API_Key`. Config reads several name variants; Windows env is case-insensitive so `GEMINI_API_KEY`/`PARALLEL_API_KEY` resolve too. Gemini is the **Developer API** (api-key auth), not Vertex.
- **Models:** `gemini-2.5-pro` (extraction), `gemini-2.5-flash` (researcher/normalizer). ADK 2.8.0. parallel-web >=1.0.1: `client.search(objective=, search_queries=[...])` → `res.results[].url/.title/.excerpts`.
- **Windows console:** prefix live-run python with `PYTHONIOENCODING=utf-8` and avoid non-ASCII in prints (cp1252 crashes on `→`, `—`).
- **ADK mode is slow** (one agent run per item, ~14 calls). UI defaults to fast path; "Agentic (ADK)" toggle for the live demo. `LunarFizz` → INSUFFICIENT only in mock/cached; live returns tangential sources → ESCALATE (record the honesty beat from cached mode).
- **Local Python is 3.10.5** (repo targets 3.11; both fine). CI uses 3.11.

## Git / GitHub

- Remote `origin` = `https://github.com/whitepaper27/Agentic_Cinema.git` (account **whitepaper27**, auth via Windows Credential Manager — `git push` works non-interactively). `gh` CLI is NOT authenticated.
- Commit only when asked. End messages with the Co-Authored-By trailer. Never commit `.env` or `app/data/`.

## Deployment (DONE — how to redeploy)

Deployed via `gcloud run deploy --source .` (Cloud Build builds the Dockerfile).
gcloud is installed at `C:\Users\Sahil\google-cloud-sdk` **but its bundled Python
is missing**, so every gcloud call needs two env vars (sourced from
`scratchpad/gcenv.sh`):
```bash
export CLOUDSDK_PYTHON="C:\\Python310\\python.exe"
export PYTHONPATH="C:\\Users\\Sahil\\google-cloud-sdk\\lib\\third_party"
export PATH="/c/Users/Sahil/google-cloud-sdk/bin:$PATH"
```
Redeploy after a code change:
```bash
gcloud run deploy studioclear --source . --region us-central1 \
  --allow-unauthenticated \
  --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest,PARALLEL_API_KEY=PARALLEL_API_KEY:latest \
  --memory 1Gi --cpu 1 --timeout 600 --max-instances 3 --quiet
```
- **Health check is `/health` (or `/status`), NOT `/healthz`** — Google's front
  end swallows `/healthz` on `*.run.app` before it reaches the container.
- `.gcloudignore` keeps `.env`/`.venv`/`.git` out of the Cloud Build upload.

## Next steps

1. **Eyeball the new UI live** (https://studioclear-602811764567.us-central1.run.app,
   hard-refresh once) — the only unverified thing is how it *looks*; it's
   data-verified. Fix any panel that doesn't match `claude_ui.md`.
2. **Record the 3-min video** against `demo/cached_run.json` (sol.md E6) — the
   `claude_ui.md` §9 beat sheet maps the take to this UI. Deterministic take.
3. Optional: demo polish, README screenshots, Devpost submission text (include the live URL).
