# StudioClear — Agentic Script Clearance Research Desk

**Google Cloud Agentic Cinema — Parallel Track**

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
requirement). Runs on Cloud Run; secrets via Secret Manager; evidence/audit in
Firestore.

## Repository layout

```
studioclear/     analyzer · contract · agents · research · security · evals
app/             api (FastAPI) · frontend
demo/            seeded script, golden expected_items.json, cached run
scripts/         smoke tests + run_spine (the Day-1 critical path)
tests/           unit · adversarial · integration · parallel
```

The pure, load-bearing modules (models, policy evaluator, AuthZ, audit chain,
evidence integrity, confidence, metrics) are **implemented and tested**. The
external-API surfaces (Gemini, Parallel, ADK, Firestore) are clean stubs marked
`NotImplementedError` for the build.

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
