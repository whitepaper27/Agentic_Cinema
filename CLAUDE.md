# CLAUDE.md — StudioClear (Agentic Cinema hackathon)

Working notes for Claude Code. Read this first each session.

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

## Current status (as of Sep 6)

Working and tested **live** (real Gemini + Parallel keys): full spine, FastAPI
backend + UI, human override→audit, and **real ADK agents** (the §25/§27
compliance lock is CLOSED — Planner/Researcher/Reviewer are `google.adk` Agents;
Researcher calls `parallel_search` as an ADK tool at runtime). CI is green (43
tests). **Remaining: (1) deploy to Cloud Run — blocked on user's gcloud/GCP;
(2) record the 3-min video.** Do NOT re-do finished work — check PROGRESS.md.

## How to run

```bash
# Windows, from D:\Eb1\Hackathon
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt          # or the .venv already exists
cp .env.example .env                       # keys already in .env (gitignored)

pytest tests/                              # 43 pass, offline/deterministic
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
- `app/api/main.py` — FastAPI (/upload, /run, /report, /decision, /audit, /healthz). `app/frontend/index.html` — single-page UI.
- `demo/` — seeded script, `expected_items.json` (golden), `cached_run.json` (deterministic demo artifact), `adk_run.json` (agentic sample).

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

## Next steps (tomorrow)

1. **Deploy to Cloud Run** — `deploy/README.md` Option A (Console + GitHub, no local tooling). After deploy, verify hosted `/healthz` and a live `/upload`.
2. **Record the 3-min video** against `demo/cached_run.json` (sol.md E6) — deterministic take.
3. Optional: demo polish, README screenshots, Devpost submission text.
