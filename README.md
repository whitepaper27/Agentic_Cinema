# StudioClear — Agentic Script Clearance Research Desk

**Google Cloud Agentic Cinema — Parallel Track**

[![CI](https://github.com/whitepaper27/Agentic_Cinema/actions/workflows/ci.yml/badge.svg)](https://github.com/whitepaper27/Agentic_Cinema/actions/workflows/ci.yml)
&nbsp;License: MIT &nbsp;·&nbsp; Google ADK 2.8 &nbsp;·&nbsp; Gemini 2.5 &nbsp;·&nbsp; Parallel Search

**🔗 Live demo:** https://studioclear-602811764567.us-central1.run.app — deployed
on Google Cloud Run, running **real** Gemini + Parallel. Open it and click
**"Run demo script."**

> Turn an unstructured screenplay into a **source-backed, policy-aware clearance
> research workflow** where every recommendation is traceable and every final
> decision stays with the studio.
>
> **Agents research and recommend. The studio clears.**

StudioClear extracts real-world references and factual claims from a script,
uses **Parallel** to build cited, multi-source evidence at runtime, applies a
deterministic studio policy to triage each item into **CLEAR / REVIEW /
ESCALATE / INSUFFICIENT EVIDENCE**, enforces bounded agent permissions, and
hands the producer a fully traceable report. It does **not** issue legal
clearance — it removes the manual research and triage work that happens *before*
a human decides.

---

## Why it's built to enterprise standard (not just a demo)

- **Evidence integrity is an enforced invariant.** The LLM can never emit a
  citation — every `source_url` is passed through verbatim from the Parallel
  API response and anything else is dropped. See
  `studioclear/research/evidence_normalizer.py` and
  `tests/adversarial/test_evidence_integrity.py`.
- **Governance that resists subversion.** The uploaded script is untrusted
  input; script text is treated as *data, never instructions*
  (prompt-injection resistant), and agents can only use registry-approved
  capabilities — unapproved calls are genuinely **DENIED** and audited.
- **Tamper-evident audit trail.** Every action is written to an append-only
  **hash chain** that fails verification if any event is altered or deleted.
- **Honest metrics, recall-first.** For clearance the dangerous error is a
  *missed* item — evals foreground recall ("missed clearance risks"), and no
  fabricated quality scores are ever shown.
- **Human authority by design.** No "legally cleared by AI" state exists.

Full plan and rationale: [`sol.md`](./sol.md).

---

## Architecture

```
SCRIPT PDF
  → Gemini extract (references + claims)     gemini-2.5-pro
  → Research Planner groups items            ADK agent
  → StudioClear AuthZ (allow / real DENY)    tool registry
  → Parallel Search (real, multi-batch)      parallel-web SDK
  → Evidence (cited, integrity-enforced)     gemini-2.5-flash
  → Deterministic policy evaluation          studio policy YAML
  → CLEAR / REVIEW / ESCALATE
  → Human decision desk + override           (all audited)
  → Traceable clearance report
```

Planner, Researcher, and Reviewer are **Google ADK** agents; the backend entry
point (`app/api/main.py`) initializes **ADK + the Parallel SDK** (track
requirement). **Deployed on Cloud Run** with the two API keys in **Secret
Manager**; run data in a JSON store (swappable for Firestore, sol.md §11).

## How it works — one item through all 8 stages

Every upload runs the spine in `studioclear/pipeline.py`:
`parse → extract → plan → authorize(+DENY) → search → integrity → policy → report+audit`.
Here is a single real item (`the Golden Gate Bridge`) flowing through it:

| # | Stage | What happens to this item |
|---|-------|---------------------------|
| 1 | **Parse** | Script loaded as **untrusted data** — never executed as instructions (prompt-injection defense). |
| 2 | **Extract** (`gemini-2.5-pro`) | Gemini finds the reference and types it: `location → "the Golden Gate Bridge"`. |
| 3 | **Plan** (ADK Planner) | Item is grouped into a research batch. |
| 4 | **Authorize (+DENY)** | The `parallel.search.public_web` capability is checked against the approved-tool registry → **ALLOW**. An unapproved tool would be **DENIED** and audited (the run logs `unauthorized_blocked: 1`). |
| 5 | **Search** (Parallel / ADK Researcher) | Query *"authoritative, independent sources about 'the Golden Gate Bridge' (location)"* → evidence with `en.wikipedia.org/wiki/Golden_Gate_Bridge`, etc. |
| 6 | **Integrity** | The LLM is **never** allowed to emit a `source_url` — every URL is passed through verbatim from Parallel; `confidence` is a **pure function** of independent-source count (no guessed scores). |
| 7 | **Policy** (deterministic) | Rule engine assigns a state. |
| 8 | **Report + audit** | Result written to a **tamper-evident hash chain**; a human then clears / reviews / escalates / overrides. |

The deterministic policy (stage 7) triages the 14 demo items like this:

| Item | Type | Sources | → State | Reason |
|------|------|---------|---------|--------|
| the Golden Gate Bridge | location | 1 | **CLEAR** | `verified_for_research` |
| a Nikon DSLR | brand | 1 | **REVIEW** | `studio_review_required` |
| a documentary about Jane Goodall | living_person | 1 | **ESCALATE** | `human_review_required` |
| **LunarFizz soda** (fictional) | fictional_brand | **0** | **INSUFFICIENT** | `no_authoritative_match` |

That last row is the honesty beat: a fictional product finds **zero** authoritative
sources, so the system says *"I can't back this"* rather than bluffing a citation.

## Security &amp; governance — where it lives

Enterprise credibility here is **agent governance** (least-privilege, provable
DENY, tamper-evident audit) — not a login screen. Each claim maps to real code:

| Guarantee | How it's enforced | Code |
|-----------|-------------------|------|
| **Least-privilege agents** | Agents may only use an **allow-listed** capability; the `ExecutionContext` must also carry the matching permission. Authority only ever *shrinks*: `Effective = User ∩ Script ∩ Agent ∩ Tool ∩ CloudIAM ∩ StudioPolicy`. | `security/authorization.py`, `security/tool_registry.py` |
| **Real DENY (not theater)** | An unapproved capability (`unapproved_legal_database.search`) returns `DENY → tool_not_authorized`, writes an audit row, and the run reports `unauthorized_blocked`. | `authorization.decide()`, `pipeline.py` |
| **One real Cloud IAM check** | The Cloud Run runtime service account's only privileged grant is `secretAccessor` on the two API-key secrets — the app's genuine IAM boundary. | `deploy/terraform/`, Secret Manager |
| **Tamper-evident audit** | Append-only hash chain: `hash = sha256(prev_hash + canonical_json(event))`. Alter or drop any event and verification fails. Human overrides append to the *same* chain. | `security/audit.py`, `store.py` |
| **Evidence integrity** | The LLM can never fabricate a citation — URLs pass through verbatim from the search API. | `research/evidence_normalizer.py` |
| **Prompt-injection resistance** | Uploaded script text is treated as data, never as instructions; an embedded "ignore your rules" line is ignored. | `tests/adversarial/`, extractor prompt |
| **Human authority** | No "cleared by AI" state exists by design; the studio makes the final call. | `models.py` (states), `store.apply_decision()` |

> **Honest scoping:** this is *agent-capability* authorization + audit, not
> multi-tenant user **RBAC**. That's deliberate for a 4-day build — the judged
> differentiator on this track is provable agent governance over real Parallel
> research, which is exactly what the table above delivers. Multi-user RBAC is a
> named non-goal (sol.md §23).

## Try it live (three ways)

**1. The hosted UI (easiest — no setup):**
Open **https://studioclear-602811764567.us-central1.run.app** and click
**"Run demo script."** It runs on a built-in seeded screenplay — you don't need
to upload anything. Toggles:
- **"Use live Gemini + Parallel"** — runs the real APIs (~40s) instead of the
  cached deterministic run.
- **"Agentic (ADK)"** — routes research through the ADK Researcher agent (~75s;
  this is the track's agentic path).

Click any row to open the evidence drawer (with real source links), then use the
**Clear / Review / Escalate / Override** buttons — each appends to the audit chain.

**2. One curl (proves the live pipeline):**
```bash
curl -s -X POST https://studioclear-602811764567.us-central1.run.app/upload \
  -H "Content-Type: application/json" \
  -d '{"title":"Smoke Test","prefer_live":true,"use_adk":false}' | python -m json.tool
# → providers: Gemini + Parallel, 14/14 evidence-backed, audit_verified: true
```
Health check: `GET /health` (lists ADK 2.8 + the 3 agents). *Note: `/healthz` is
reserved by Google's front end on `*.run.app` — use `/health`.*

**3. Locally** — see [Quickstart](#quickstart) below.

## Repository layout

```
studioclear/     analyzer · contract · agents · research · security · evals
app/             api (FastAPI) · frontend
demo/            seeded script, golden expected_items.json, cached run
scripts/         smoke tests + run_spine (the Day-1 critical path)
tests/           unit · adversarial · integration · parallel
```

The pure, load-bearing modules (models, policy evaluator, AuthZ, audit chain,
evidence integrity, confidence, metrics) are **implemented and tested**, and the
external-API surfaces (Gemini extraction, Parallel search, the ADK agents) are
**fully wired and verified live** on Cloud Run — both the fast path and the
agentic ADK path return real, cited, audit-verified results.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # add PARALLEL_API_KEY + GCP project

# prove the platform before building product code (sol.md E1.5)
python scripts/smoke_gemini.py
python scripts/smoke_parallel.py

# run the offline test + eval suite (green today, no API keys needed)
pytest tests/unit tests/adversarial tests/integration
```

## Testing & CI

- `pytest tests/unit tests/adversarial` — deterministic, offline, must be green.
- `pytest tests/parallel` — Parallel reliability harness (priority suite).
- `python -m studioclear.evals.run_golden --cached demo/cached_run.json` —
  recall-first golden eval; a missed clearance risk fails the gate.
- GitHub Actions (`.github/workflows/ci.yml`) runs lint + tests + golden evals
  on every push.

## Responsible AI & limitations

StudioClear is a **research and triage system, not legal advice**. It never
issues legal clearance; humans retain final authority. It surfaces uncertainty
explicitly (`INSUFFICIENT EVIDENCE`) and makes every recommendation
source-traceable. Demo content uses real brands and people in **neutral factual
context only**, uses a **fictional** brand for any negative context, and shows
no third-party logos, slogans, or trademark graphics.

## License

[MIT](./LICENSE)
