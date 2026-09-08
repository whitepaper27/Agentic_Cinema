# StudioClear — Scene-to-Production Planning Desk

**Google Cloud Agentic Cinema — Parallel Track**

[![CI](https://github.com/whitepaper27/Agentic_Cinema/actions/workflows/ci.yml/badge.svg)](https://github.com/whitepaper27/Agentic_Cinema/actions/workflows/ci.yml)
&nbsp;License: MIT &nbsp;·&nbsp; Google ADK 2.8 &nbsp;·&nbsp; Gemini 2.5 (text + vision) &nbsp;·&nbsp; Parallel Search

**🔗 Live demo:** https://studioclear-602811764567.us-central1.run.app — click
**Plan this shoot**, or **Try an example** for the deterministic showcase.

> **One scene, three ways to film it, and a production decision the creator can
> explain.**

A producer brings a scene, confirms what filming it requires, and compares three
approaches — a **nearby practical location**, an **alternative travel location**,
and **local filming with VFX** — using real research, transparent editable costs,
and honest uncertainty. Change a constraint (crew size, days, a rate) and the
applicable costs move. Pick an approach and export a production brief.

**Gemini** reads the scene and proposes production questions & candidate
locations; **Parallel** supplies the retrieved evidence and location leads;
**code** does every calculation; **Google Cloud** hosts it. Optional factual
review and scene rewriting remain available. StudioClear never issues legal
clearance, books anyone, or fabricates a price.

---

## The loop

```
Bring a scene → Choose a task → Confirm requirements → Compare three options
    → Adjust constraints → Select an approach → Export a production brief

Optional: Review factual details  ·  Improve the scene (creative rewrite)
```

The differentiated moment is an **observable production decision**: change the
traveling crew size or a rate and the relevant cost lines recalculate — the
recommendation may or may not change, and the app says so honestly.

---

## What makes it credible (not just a demo)

- **Deterministic cost engine** (`cost_engine.py`) — all arithmetic is Decimal and
  lives in code: line range = qty × rate range, subtotal of **known** lines only,
  contingency applied once, shared expenses (a flight, a rental) counted once, and
  an **overlap-aware** comparison that only calls one option cheaper when its range
  is entirely below the other's *and* coverage is comparable. Otherwise it says the
  ranges overlap.
- **Never a fabricated price.** A missing rate is **"quote needed"** and keeps the
  estimate **incomplete** — never a zero-valued free line, never a made-up number.
  Live rates come from your editable brief (provenance `estimate`) or a supplier
  quote; the app won't invent them.
- **Real research + scene-aware suggestions.** Live mode runs actual Parallel
  searches for crew/hotel/permit leads, and Gemini proposes candidate filming
  locations that match your scene's look — attached to real leads, labeled as
  *leads to verify*, never a feasibility or cost claim.
- **Fantasy preserved, no silent fact-checking.** A task selector (**Plan this
  shoot** / Review factual details / Improve this scene) drives behavior; an empty
  instruction is **not** turned into a historical fact-check, and a magic-stone
  premise stays intact.
- **Honest evidence layer** (optional review) — the model returns a `source_id` +
  quote, code resolves it (rejecting unknown ids / invented quotes) and maps to
  SUPPORTED / CONTRADICTED / MIXED / UNRESOLVED; a recheck **re-extracts** the
  changed scene so a newly-added claim is actually researched.
- **Session-private + durable.** Owner-scoped sessions, a sanitized export (no
  owner/session data), a real **24-hour expiry** (`410 Gone`), and durable Google
  Cloud Storage that survives instance restarts.

---

## Architecture

```
Browser: scene + task + brief (base, crew, days, editable rate estimates)
  → POST /scenes        Gemini extraction (vision|text), fantasy-preserving
  → POST /scenes/{id}/location-suggestions   Gemini candidates + Parallel leads
  → POST /scenes/{id}/shoot-comparisons      real Parallel research + cost engine
                                             → three priced options, honest coverage
  → adjust a constraint → recalc (new comparison revision, code-only arithmetic)
  → POST /shoot-comparisons/{id}/decision    select for planning (no booking)
  → GET  /shoot-comparisons/{id}/handoff     one sanitized planning-brief snapshot

Optional scene review: POST /runs · /runs/{id}/revisions · /revisions/{id}/decision
  · /scenes/{id}/recheck · /scenes/{id}/creative-proposals
```

- **Cost + comparison:** `studioclear/cost_engine.py`, `studioclear/shoot_comparison.py`.
- **Providers:** `providers/production.py` (`LiveProductionProvider` — real Parallel,
  honest rate provenance), `ExampleProductionProvider` (deterministic). Live mode
  returns **503** without a Parallel key rather than faking data.
- **Evidence/revision:** `research_pipeline.py`, `revision.py`, `handoff.py`.
- **Store:** `scene_store.py` (scenes, versions, runs, comparisons; session
  ownership; 24h expiry) over a pluggable backend (`storage_backend.py`: local JSON
  or private GCS with generation-precondition writes + Custom-Time lifecycle).
- **Frontend:** `app/frontend/index.html` — Analyze · **Shoot options** · Scene desk
  · Handoff · Execution (vanilla JS, no build).
- **Hosting:** Google Cloud Run; keys in Secret Manager; a private GCS bucket with a
  24-hour delete lifecycle.

---

## Try it

**Hosted (no setup):** open the live URL → **Plan this shoot** → paste a scene →
confirm → **Shoot options** → **Suggest alternative locations**, pick one → **Compare
three options** → change *Traveling crew* → **Recalculate** → **Select** → download
the brief. Or **Try an example** for the deterministic version.

**One curl — a deterministic comparison (no keys):**
```bash
BASE=https://studioclear-602811764567.us-central1.run.app
SID=$(curl -s -c j.txt -X POST $BASE/scenes -H 'Content-Type: application/json' \
  -d '{"mode":"example","source_type":"paste","task":"plan","title":"Demo",
       "script_text":"A stone turns what it touches to gold on the California coast."}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['scene_id'])")
curl -s -b j.txt -X POST $BASE/scenes/$SID/shoot-comparisons \
  -H 'Content-Type: application/json' \
  -d '{"mode":"example","brief":{"base_city":"LA","travel_region":"Ireland",
       "reporting_currency":"USD","shoot_days":5,"traveling_crew":10}}' | python -m json.tool
```
Health: `GET /health`. (`/healthz` is swallowed by Google's front end — use `/health`.)

## Quickstart (local)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # add GEMINI_API_KEY + PARALLEL_API_KEY for live mode
uvicorn app.api.main:app --reload        # http://127.0.0.1:8000
```
Example mode needs no keys. Live mode reads the two keys from `.env`.

## Testing & CI

```bash
pytest tests/                                   # 144 passing, offline/deterministic
ruff check studioclear tests app                # lint
```
Covers the cost engine (ranges, contingency, shared expenses, overlap-aware
comparison, incentives), the comparison API, the evidence/recheck gates (incl. the
Signal Room re-extraction gate), creative proposals, expiry/410, and sanitized
export. CI installs real deps and runs the full offline suite.

## Limitations & scope (honest)

- **Costs are estimates**, not quotes: live rates come from your brief or a supplier
  quote; unknown rates stay "quote needed" and the estimate stays incomplete. The
  app never fabricates prices, incentives, or availability. Selecting an option
  **creates no booking or outreach**.
- **Location suggestions are leads to research** — not proof filming is permitted or
  affordable there.
- **At most 3 pages / 12 MB** of images; text revisions only (art changes stay
  pending notes). PDF/DOCX import, redrawing, and generated video are out of scope.
- **Not legal advice.** Humans make every decision; there is no "cleared by AI"
  state. Session-private material auto-expires within ~24 hours.

## License

[MIT](./LICENSE)
