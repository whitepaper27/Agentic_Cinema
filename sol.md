# StudioClear — Final Product and Build Specification

**Revised:** September 7, 2026

**Track:** Agentic Cinema / Parallel

**Status:** Final implementation target; enhancements below are not yet shipped.

**Official deadline:** September 9, 2026, 2:00 p.m. PDT / 4:00 p.m. CDT.

**Delivery target:** Complete the core loop September 8; submit that evening if verified.

**UI contract:** [sol_ui.md](sol_ui.md).

This revision replaces the previous frozen plan at the user's request. It supersedes conflicting product/UI directions in claude_ui.md, CLAUDE.md, PROGRESS.md, and the earlier [scene revision proposal](docs/superpowers/specs/2026-09-07-scene-research-revision-desk-design.md). Those documents remain historical records; their claims of completed features are not acceptance evidence.

Keep the existing working integrations, explicit human decisions, source provenance, policy engine, and audit implementation where useful. Correctness fixes may change the pipeline and its expected outputs. There is no requirement to preserve erroneous verdicts or keep run_pipeline byte-identical.

## 1. Product promise and competitive thesis

> Bring your storyboard. StudioClear investigates questionable details and helps you make the smallest evidence-backed correction while preserving your creative intent.

**Product:** A scene research and revision desk for filmmakers, storyboard artists, and production researchers preparing material for shooting or animation.

**Primary job:** Investigate factual details in a scene, decide what to change, and hand the production team a traceable revision. The initial focus is historical and factual consistency. Brand, music, and likeness questions can be flagged for human review; they are not automatically resolved by web search.

**Acceptance story:** A user brings an unfamiliar scene, gives a concrete instruction, inspects evidence, accepts one constrained revision, rechecks the revised scene, and exports a usable handoff.

~~~text
Bring material → State intent → Confirm extraction → Investigate
    → Propose a small revision → Accept or reject → Recheck → Export
~~~

The differentiated moment is an observable correction: changing a researched detail changes the relevant finding while protected dialogue stays intact. An ambiguous second finding remains unresolved. This demonstrates perception, research, user control, and verification in one workflow.

Gemini reads and reasons about the material. Parallel supplies the retrieved evidence that influences the revision. Google Cloud hosts the application and controls its cloud-resource access. StudioClear connects those capabilities to a specific production task.

Winning is an aspiration, not a claim or guaranteed outcome. Judge value comes from demonstrated behavior and measured results.

## 2. Verified starting point and implementation gaps

Assessment date: September 7, 2026. The public root returned HTTP 200 and /health reported ADK 2.8.0 with three initialized agent names. This verifies availability and initialization, not end-to-end live provider execution or visual quality. Findings below come from the local implementation.

| Area | Existing implementation | Required change |
| --- | --- | --- |
| Front door | Load demo run / Run live; request contains no script_text | Paste or upload real material and supply a meaningful instruction |
| Parsing | Only Markdown headings matching **SCENE N; PDF raises NotImplementedError | Support ordinary text and INT./EXT. slugs; add image extraction |
| Vision | No image ingestion/extraction path | Read actual uploaded pixels and confirm page-linked extraction |
| Evidence | Returned sources are assigned supports: true; normalization is a stub | Assess support, contradiction, relevance, and insufficiency against the exact claim |
| Policy | Some factual claims become CLEAR from source counts | Use assessed evidence and separate research findings from human decisions |
| Confidence | Formula yields 0.4 with no sources and 1.0 with three | Remove quality percentages; display evidence coverage and limitations |
| Agents | ADK researcher executes on the optional ADK path; planning and policy use ordinary code | Report actual execution; implement bounded research follow-up where evidence requires it |
| Governance display | IAM rows are static; an unapproved-tool denial is deliberately inserted each run | Label configuration and self-tests accurately; show actual events separately |
| Revision | Human decisions exist, but no scene revision/recheck loop | Add versioned proposals, acceptance, scene re-extraction, and recheck |
| Storage | Run JSON on container/local filesystem | Durable run and asset storage with per-run access control for hosted uploads |
| Evaluation | Fixture-based tests; cached golden command ends in || true | Enforce useful CI failures and evaluate unseen material separately |
| Timestamps | Pipeline defaults to the fixed demo timestamp even for live callers | Capture actual server UTC times on the live path |

A real citation URL establishes provenance. It does not establish that its passage supports a claim, that publishers are independent, or that a depiction is cleared for use.

## 3. Judging strategy

The official rules give equal weight to technological implementation, design, potential impact, and idea quality. They require active Parallel Search use for this track. [Official rules](https://agentic-cinema.devpost.com/rules)

| Criterion | What the submission must demonstrate | Evidence to retain |
| --- | --- | --- |
| Technological implementation | Real Gemini extraction, Parallel research, evidence interpretation, revision and recheck | Actual request/tool events, provider metadata, repository path, live smoke results |
| Design | A user completes the entire workflow with their own material | Browser walkthrough, clear failures, source preview, usable export |
| Potential impact | A filmmaker makes a supported correction and produces a useful handoff | An observed user session and measured task results; clearly label any anecdote |
| Idea quality | Research leads to a minimal creative revision under user constraints | Before/after scene, protected-text comparison, changed finding, unresolved finding |

Do not substitute agent counts, animated stages, citation totals, or security badges for a demonstrated outcome.

## 4. Scope and deliberate cuts

### Required for this submission

- One project/run at a time, with a title.
- Paste text or upload up to three original comic/storyboard pages.
- PNG, JPEG, and WebP only; validate decoded content, not just extensions.
- Starting limits: 4 MiB per image, 12 MiB total decoded images, 20 megapixels per image, and 20,000 characters of pasted text. Account separately for base64 request overhead if using JSON transport.
- A research/revision instruction and exact text spans the user wants to preserve.
- Page/scene-linked extraction with a correction step before research.
- Claim-level evidence, clear uncertainty, and separate human-review routing.
- One proposed revision at a time, before/after comparison, accept/reject.
- Re-extraction and research of the entire changed scene, including newly introduced claims.
- Revised text plus a printable production handoff and structured JSON export.
- Authentic runtime metadata, explicit demo modes, durable hosted runs.
- Existing demo remains accessible as a clearly labeled example.

### Deferred until after submission

PDF/DOCX import; generated video; comic art redrawing; face identification; automated rights clearance; full screenplay continuity graphs; batch revisions; external publishing; email outreach; additional partner tracks; new orchestration frameworks; semantic memory; enterprise SSO; multi-user collaboration.

Image revision in this build means dialogue/caption text and panel-specific production notes. Uploaded artwork remains unchanged. A proposed drawing change stays marked as pending art work and cannot be verified as visually applied.

If time tightens, reduce the showcase to one page and one researched correction. Preserve evidence correctness, user acceptance, and recheck. If only text works, describe that limitation honestly and mark the comic-input objective incomplete.

## 5. User workflow and intent contract

1. **Bring a scene.** Upload pages or paste text; preview, reorder, or remove pages before analysis.
2. **Direct the work.** Enter an instruction such as “Check historical details. Preserve the characters, joke, and ending.” Select exact dialogue/caption spans to lock.
3. **Confirm extraction.** Gemini returns page descriptions, candidate panels, transcribed text, and candidate claims. The user corrects misreads before research.
4. **Investigate.** Select a finding, inspect its source location, see the exact research question and relevant retrieved passages.
5. **Request a revision.** Propose the smallest supported change. Show what changes, why, what remains protected, and any unresolved tradeoff.
6. **Accept or reject.** The proposal does not alter the current scene until accepted.
7. **Recheck.** Create a new scene version, re-extract its claims, and research changes and new claims. Preserve prior findings and decisions as history.
8. **Export.** Leave with the accepted text and a production handoff, including pending art notes and unresolved questions.

Intent must change observable behavior: research scope/prioritization, the question asked, or revision constraints. Echoing the prompt in a report is insufficient.

Exact locked text is enforced with code. Semantic constraints such as preserving a joke or character motivation are model-assessed and user-reviewed; do not call them mechanically guaranteed.

## 6. Architecture and execution

Extend the existing Python/FastAPI backend and vanilla-JavaScript frontend. Keep provider adapters and deterministic policy evaluation. Do not introduce a new frontend framework solely for this enhancement.

~~~text
Browser: pages/text + instruction + locked spans
  → validate and persist source material
  → Gemini multimodal/text extraction
  → user confirms corrected scene version
  → plan focused claim questions
  → authorize each actual research tool call
  → Parallel Search returns source records
  → Gemini classifies passages against claims using source IDs
  → code validates references, quotes, constraints, and policy
  → user reviews evidence and requests a small revision
  → Gemini proposes structured edits against a version
  → code validates protected spans and evidence references
  → user accepts
  → persist new scene version and mark findings stale
  → re-extract changed scene + research changed/new claims
  → export versioned handoff and audit history
~~~

**Execution approach:** Begin with bounded synchronous requests for each user-visible operation: extraction, research, proposal, acceptance, and recheck. The frontend shows an indeterminate busy state while a request runs. Acceptance persists independently of recheck so a provider failure does not lose an accepted edit.

Do not claim streaming progress or cancellation unless the backend implements them. A browser timeout does not prove server cancellation. Use operation IDs and idempotency keys so retries can recover prior results.

**Starting research budgets:** At most eight prioritized findings per analysis; at most two search attempts per finding; at most five candidate sources per attempt. Show unresearched findings as “Not researched: run limit reached.” Record actual attempts and tune the budgets against live latency before freeze. These are scope controls, not measured performance claims.

Research follow-up must be purposeful: refine an ambiguous entity, seek a primary source, or investigate conflicting evidence. Stop on sufficient evidence, explicit failure, or budget exhaustion. Log the reason and actual tool response.

## 7. Evidence contract and research states

### Source provenance

The server assigns immutable source IDs to raw Parallel results and preserves their URL, title, returned passages, query, retrieval time, and operation ID. Retrieval time comes from the server clock; record a provider timestamp separately if supplied.

The model selects source IDs and passage ranges. It cannot supply citation URLs. Code resolves references back to stored records and rejects unknown IDs and quotes that cannot be matched to retrieved text under a documented whitespace-normalization rule.

An explanation may paraphrase. A displayed quote must be a retrieved passage, not model-written text. Preserve enough context to assess it; the existing 300-character truncation may discard necessary qualifications.

Allow only http/https citation links in rendering. Treat page titles, excerpts, source text, and model output as untrusted content.

### Claim assessment

For each source/claim pair record:

| Field | Meaning |
| --- | --- |
| relation | supports, contradicts, context_only, or unclear |
| passage reference | Stored source ID and exact passage/range |
| explanation | Why this passage bears on the claim |
| applicability | Relevant person/entity, date, place, and scope |
| source type | Primary, secondary, or unknown, with a basis |
| limitations | Missing context, uncertain applicability, or conflicting evidence |

Entity existence and factual truth are different research questions. Neither establishes permission to depict an entity.

Distinct hostnames are a coverage measure, not proof of publisher independence. Deduplicate URLs and domains, record publisher/provenance relationships where known, and label independence unknown where it cannot be established. Do not automatically count syndicated copies or subdomains as independent corroboration.

### Findings and routing are separate

| Research status | Meaning and rule |
| --- | --- |
| SUPPORTED | Applicable supporting evidence meets the versioned studio research policy and has no unresolved material contradiction |
| CONTRADICTED | Applicable evidence directly challenges the claim; show the disputed detail |
| MIXED | Material support and contradiction coexist without a resolved explanation |
| UNRESOLVED | Evidence, context, source quality, or applicability is insufficient |
| NOT_RESEARCHED | Deliberately out of scope or skipped by a recorded budget |
| STALE | Finding belongs to an older scene version and awaits recheck |

Use a separate workflow field: NONE, REVIEW, or ESCALATE. Human decisions are separate again. A factually supported scene may still require rights or producer review.

Initial factual policy: one directly applicable primary source, or two corroborating sources whose independence is documented, can meet the evidence threshold. An unresolved material contradiction prevents SUPPORTED. These are studio research rules, not claims of universal truth; publish the policy version and its limitations.

Code deterministically maps validated structured assessments to states. The model's evidence interpretation can still be wrong; evaluate that layer independently.

Empty search results mean “No relevant evidence found in this search,” not “fictional,” “safe,” or “rights-free.” A provider timeout is an operational failure, never evidence of absence.

### Compatibility

Version new runs with schema_version 2. Preserve old saved reports as legacy artifacts. Display old CLEAR as “Legacy policy result: CLEAR — based on source count; not reverified.” Do not relabel old results SUPPORTED without a real reassessment.

Deprecate confidence in the new schema. No percentage-quality badge until there is an independently evaluated calibration procedure. Source counts, disagreement, and missing evidence are sufficient for this submission.

## 8. Revision and recheck contract

A proposal includes revision_id, base_scene_version, target span IDs, original text, proposed edits, rationale, grounded evidence IDs, exact-lock validation, semantic-constraint notes, and any art-change instructions.

**Rules:**

- Apply structured edits to the canonical scene text. Editing only item.text_span is insufficient.
- Return proposal text and evidence IDs; resolve citation links on the server.
- Preserve all exact locked spans. If the requested correction conflicts with one, return a conflict explanation without a silently altered proposal.
- Do not propose a factual assertion as corrected when evidence is unresolved.
- Validate that the proposal's base version is current before acceptance.
- Rejection preserves the scene and records the user's choice.
- Repeated acceptance with the same operation key creates no duplicate versions.
- Acceptance creates a new immutable scene version and marks previous findings stale.
- Recheck re-extracts all claims in the changed scene; match retained, modified, added, and removed claims using stable IDs and explicit lineage.
- Reuse unchanged-claim evidence only when claim, context, freshness policy, and provenance remain applicable. Record reuse. Research changed and newly introduced claims through Parallel.
- A removed claim is “Removed in revision,” not “Verified.” A newly introduced unsupported detail prevents a “fully rechecked” completion message.
- Retain both before and after results. Recheck may remain MIXED or UNRESOLVED.
- A failed recheck leaves the accepted version intact with a retryable failure; do not fall back to old green statuses.

Text-only changes cannot establish that a depicted visual error was corrected. If art must change, export the art note and keep visual verification pending until updated artwork is supplied.

## 9. Versioned data and API contract

These are target interfaces, not existing endpoints. Agree on them before frontend implementation; keep sol_ui.md in sync.

### Required stored entities

| Entity | Required fields |
| --- | --- |
| Scene | scene_id, owner/session scope, source type, ordered assets, current_version |
| Scene version | version, parent_version, canonical text, page/panel/span IDs, creation time, instruction and exact locks |
| Run | run_id, scene_id/version, schema_version, policy_version, status, provider execution metadata, operation IDs |
| Finding | stable finding_id, scene/page/panel/span references, exact claim, research status, routing, evidence IDs, limitations |
| Source | source_id, raw URL/title/passages, query, retrieval time, provenance and independence notes |
| Revision | revision_id, base/result versions, structured edits, rationale, evidence IDs, constraints, decision |
| Recheck | operation_id, before/after run IDs, claim lineage, unresolved/new/removed claims, status/error |
| Event | sequence, UTC time, run/version, actor category, actual action/result, operation ID, hash-chain fields |

Panel bounds are optional normalized coordinates tied to a specific asset. If bounds are unreliable, fall back to page-level navigation. Never invent precise regions or treat extraction order as identity across edits.

### Proposed routes

| Route | Purpose |
| --- | --- |
| POST /scenes | Validate text or image upload, persist source, extract editable draft |
| PATCH /scenes/{scene_id} | Save corrected draft, intent, exact locks; require expected version |
| POST /runs | Research a confirmed scene version with explicit live mode |
| GET /run/{run_id} | Read authoritative run, findings, source references, revision/recheck status |
| POST /runs/{run_id}/revisions | Propose an evidence-backed edit against the current version |
| POST /revisions/{revision_id}/decision | Accept or reject using expected version and idempotency key |
| POST /scenes/{scene_id}/recheck | Re-extract and research a specified accepted version |
| GET /report/{run_id} | Versioned structured handoff; frontend supports print/PDF |
| GET /scenes/{scene_id}/assets/{asset_id} | Authorized preview of uploaded material |
| GET /operations/{operation_id} | Recover persisted outcome/error after an uncertain timeout |
| DELETE /scenes/{scene_id} | Remove user material and associated runs/assets under the documented retention policy |

Keep existing /policy, /health, and legacy /upload behavior available for the explicit legacy demo. Prevent arbitrary user content from silently selecting mock providers.

Return structured errors with code, message, retryable, operation_id, and affected page/finding. Use 409 for stale-version conflicts, 413 for size limits, 422 for invalid/unreadable input, and an appropriate 5xx for unavailable live providers. Preserve unaffected pages and user-entered text when possible.

## 10. Hosted reliability, privacy, and storage

Do not put new personal uploads into a publicly enumerable /runs list or rely on hard-to-guess IDs as the sole access control.

Use a lightweight opaque session cookie and enforce ownership on reads, assets, edits, decisions, rechecks, and deletion. This is a single-session workspace, not authenticated studio identity or enterprise RBAC. Separate public examples from private session runs.

For the hosted path, use a dedicated private Cloud Storage bucket for source images and run/version JSON. Use generation preconditions or equivalent compare-and-swap to prevent lost updates. Retain local filesystem storage for development only. Do not put assets directly on a public bucket.

Cloud Run instances must read the same durable state. Validate that a run survives an instance restart and can be read through a different instance. Keep secrets server-side in Secret Manager with narrowly scoped resource access.

Starting retention policy: retain uploads/runs for 24 hours unless the user deletes them earlier; disclose this before upload. Enforce expiry on access and through a cleanup mechanism. Configure and disclose any soft-delete/backup retention before promising physical deletion. Keep source text/images out of ordinary logs.

Add bounded request sizes, concurrency, provider attempts, and per-session run limits. Show a useful error when a limit is reached. Never expose provider keys in a browser configuration.

Persist actual provider mode per stage. A missing live key or provider outage blocks that stage. Mock output must never attach fixed demo evidence to a user's coincidentally matching item ID.

## 11. Agent execution, authorization, and audit honesty

Use the existing Google ADK research integration where it delivers actual tool-driven research. No additional named agent roles are required.

The research agent should formulate a focused question, inspect returned evidence, and make a bounded follow-up decision. Extraction and revision may be direct Gemini calls. Planning and policy may remain deterministic code.

Record execution from actual calls/events: model, component type, start/end time, tool name, query, result count, retry/follow-up reason, and outcome. Initialized agent objects and /health names do not establish that those agents ran.

Put authorization at the actual tool boundary, including ADK function tools and retries. An outer pipeline check alone does not prove every subsequent tool invocation was authorized.

Label the existing forced unapproved-tool event “Authorization self-test.” Exclude it from operational incident counts. If no real denied request occurred, report none. Do not narrate planner recovery unless a trace demonstrates it.

Display Terraform/IAM configuration as configuration. Runtime access success is a separate observation; a hardcoded DENY row cannot establish cloud permission denial.

The local hash chain checks internal event consistency. It does not prove resistance to wholesale rewriting or tail truncation without a separately trusted checkpoint. Use “Chain consistency verified,” not “tamper-proof,” “immutable,” or “compliance-grade.” Audit records do not establish legal approval or authenticated reviewer identity in the session-only prototype.

Treat uploaded text, image text, research pages, and model output as untrusted. Enforce allowed tools, validated structured output, escaped rendering, and exact locks outside model instructions. Injection testing provides bounded evidence of robustness, not a blanket immunity claim.

## 12. Evaluation and release gates

### Offline regression tests

Retain useful existing tests and add meaningful coverage for the changed behavior:

- Plain text, Markdown, screenplay slugs, empty input, and images with unreadable text.
- Missing keys and failed providers never substitute fixture extraction/evidence.
- Sources that mention a subject but do not support its claim cannot produce SUPPORTED.
- Contradictory sources, irrelevant sources, repeated publishers, unknown source IDs, and invented quotes.
- Corrected extraction changes the researched claim and invalidates dependent proposals.
- Locked text preserved; conflicting revision refused; proposal does not mutate the scene.
- Acceptance/rejection, idempotency, stale-version conflicts, and durable version history.
- Recheck of new/changed/removed claims; failures retain accepted text and mark findings stale.
- Session ownership, private assets, upload bounds, and rendering of untrusted content.
- Export agrees with the accepted version and exposes unresolved findings.
- Injection attempts in scenes and retrieved text cannot expand tool access.

Keep deterministic fixture tests for regression, but do not call their outputs live model quality measurements.

### Unseen-scene evaluation

Before freeze, aim for at least six short scenes not used to tune the demo: plain text, a storyboard, a valid fact, a false factual detail, an ambiguous/insufficient case, and an injection-containing scene. These categories may overlap.

Manually label expected claims, acceptable evidence relations, and protected spans before running the system. Include at least one test where revision introduces another factual detail and one where art correction is required.

Publish actual numerators and denominators, sample size, date, provider/model, and limitations:

| Measure | What to report |
| --- | --- |
| Extraction recall | Expected researchable claims found / expected claims |
| False positives | Incorrectly flagged claims, with examples |
| Evidence relation correctness | Human-checked supported/contradicted/context assessments |
| Citation integrity | Valid source references and matched quotes / citations shown |
| Revision usefulness | Human assessment of correction and creative constraints |
| Exact-lock preservation | Successful unchanged locks / tested locks |
| Recheck coverage | Changed/new claims rechecked / changed/new claims |
| Workflow completion | Users completing upload-to-export / observed users |
| Reliability | Completed/failed runs, retries, actual end-to-end duration |

These are small-set observations, not population accuracy or legal-risk reduction. Do not invent ROI, money saved, or percentage time savings. A manual comparison is useful only if actually conducted under stated conditions.

### CI and live checks

Remove the golden-eval || true suppression and ensure meaningful failures fail CI. Update obsolete expected states deliberately for schema v2; preserve legacy fixtures with their original labels. Install dependencies needed for the exercised integration tests rather than silently skipping the API path.

Current repository commands:

~~~text
.venv\Scripts\python.exe -m pytest tests/unit tests/adversarial tests/integration
.venv\Scripts\python.exe -m ruff check studioclear tests app
.venv\Scripts\python.exe -m studioclear.evals.run_golden --cached demo/cached_run.json
~~~

The cached golden command is a legacy regression check. Run new schema-v2 checks and the unseen-scene evaluation separately once implemented.

Live acceptance must exercise actual uploaded pixels, Gemini, Parallel tool events, one accepted revision, recheck, and export. Browser checks cover narrow and wide layouts, keyboard operation, errors, and readable print output. Record commit/revision and artifacts; do not carry forward old “45 tests passed” claims as new verification.

## 13. Implementation order and freeze

Each phase has a gate. Do not polish an unsupported conclusion or record planned features as working.

| Phase | Work and principal files | Exit condition |
| --- | --- | --- |
| 1. Evidence foundation | models.py; research/evidence_normalizer.py; providers; contract/policy_evaluator.py; pipeline.py | Irrelevant/contradicting sources cannot clear a factual claim; legacy results labeled |
| 2. Real input | analyzer/script_parser.py; providers/gemini.py; app/api/main.py; frontend | A new pasted scene and actual uploaded page produce editable extraction; no mock fallback |
| 3. Research desk | source/claim store; focused questions; ADK tools; evidence UI | Confirmed scene yields source-linked support/contradiction/uncertainty with actual execution |
| 4. Revision loop | new revision module; store/versioning; API and frontend | Propose → accept/reject → changed-scene recheck, with exact locks and failure recovery |
| 5. Handoff and hosting | report UI; durable storage/session scope; retention; deployment config | Export matches accepted version; hosted run survives restart and remains session-scoped |
| 6. Proof and submission | tests/evals; README; demo assets; video and Devpost | Unseen-scene results recorded; honest three-minute walkthrough and submission complete |

Integrate upload privacy/storage when introducing real uploads; phase 5 is the release verification of that work, not permission to expose private drafts earlier.

**September 7:** Evidence correctness and real input; complete an unfamiliar-scene research slice.

**September 8, first work block:** Finish one constrained revision and recheck; verify export and hosted reliability.

**September 8, remaining time:** Freeze after gates pass, run evaluation, record video, align README and submission.

**September 9:** Verification and submission buffer; avoid speculative feature expansion.

If a phase overruns, reduce pages/findings and optional UI features. Do not skip correctness, falsely mark completion, or present a replay as fresh processing. Reassess the schedule against actual remaining hours.

## 14. Showcase and three-minute video

Use an original storyboard with one intentionally researchable factual mismatch and one ambiguous detail. Establish the corrected fact and relevant primary-source passage during rehearsal; do not invent the expected result in this document.

A creator's original comic can be the input. Frame the task for a filmmaker adapting it, with a concrete production decision.

| Time | On-screen action | Claim demonstrated |
| --- | --- | --- |
| 0:00–0:25 | Show the scene, upload it, enter an instruction | Real input and a specific production task |
| 0:25–1:10 | Confirm extraction; open one finding and source passage | Vision/text comprehension and evidence interpretation |
| 1:10–2:05 | Request a small revision, compare, accept | User-controlled correction and preserved constraints |
| 2:05–2:35 | Recheck; show changed/new findings and an unresolved item | Verification and explicit uncertainty |
| 2:35–3:00 | Export handoff; briefly open actual Gemini/Parallel execution | Usable output and runtime integration |

Rehearse using real runs. A recording may cut waiting time if labeled; do not replace the result with fixture output. Any replay must visibly say “Recorded example” with its original provenance. Mock examples must say “Simulated example.” Neither demonstrates a newly uploaded image being processed live.

The strongest comparison changes only the factual detail while preserving exact locked text. Keep the evidence and actual scene versions available for inspection. The user acceptance is central; security details belong in the execution view.

## 15. Submission requirements and sources

Recheck the official rules before final submission; the checklist is a planning aid, not an eligibility determination.

- [ ] Hosted project URL works without developer credentials.
- [ ] Google technology and Parallel Search are actually invoked in the submitted runtime.
- [ ] Public repository contains source, required assets, setup instructions, and a detectable complete open-source license.
- [ ] Parallel is selected as the submission track.
- [ ] Public YouTube/Vimeo demonstration is at most three minutes and in English or includes English subtitles.
- [ ] Demo shows functioning software and labels any replay/simulation.
- [ ] Original submission material satisfies the rules concerning third-party content, branding, privacy, and intellectual property.
- [ ] Verify entrant eligibility, project creation requirements, and submission fields against current rules.
- [ ] README, screenshots, video, and Devpost describe the same final implementation.
- [ ] Completed Devpost submission is confirmed before the deadline.

The rules accept several Google SDKs; they do not prescribe three named ADK agents. Keeping ADK is our implementation choice. Do not claim Firestore, Vertex AI, a particular model version, or agent count is a track requirement. The existing Gemini adapter uses the Developer API by default; describe the actual configuration.

Sources: [Hackathon overview and judging criteria](https://agentic-cinema.devpost.com/), [official rules and Parallel requirements](https://agentic-cinema.devpost.com/rules), [organizer resources](https://agentic-cinema.devpost.com/resources).

## 16. Final definition of done

The build is complete when a judge can:

- Bring an unfamiliar storyboard or pasted scene and give a meaningful instruction.
- Inspect and correct what the system read.
- Open a finding tied to the material and assess its actual supporting or contradicting passage.
- See where evidence is insufficient without an invented confidence score.
- Request one small supported revision and compare it to the original.
- Accept or reject the revision, with protected text enforced.
- Recheck the changed scene, including newly introduced claims.
- Distinguish applied text changes from pending art instructions.
- Export the accepted text, sources, remaining questions, and decision history.
- Inspect actual Gemini/Parallel execution without confusing configured agents, self-tests, or replay data with live work.

All boxes require working behavior and verification. This specification itself closes none of them.

## 17. Compatibility with older section references

Source comments still refer to the previous numbered plan. Use this mapping when maintaining them; it preserves useful intent without preserving obsolete claims.

| Old reference | Current authority |
| --- | --- |
| E1, §25, §27 | Sections 6, 11, and 15: actual runtime and verified submission requirements |
| E2, §4 | Sections 12 and 14: labeled fixtures, unseen evaluation, original demo |
| E3, E7, §7–§11, §22, §24 | Sections 4–10 and 13: scope, architecture, interfaces, sequence |
| E5, §20 | Section 12: meaningful evaluation; no arbitrary quality scores |
| E6, §21 | Section 14: functioning revision-loop demonstration |
| E8.1 | Section 7: provenance plus passage/claim assessment |
| E8.2 | Sections 10–12: untrusted input, tool boundaries, tests |
| E8.3, §19 | Section 11: audit consistency and its limits |
| §12–§14 | Sections 7–8: research status, human routing, revision authority |
| §15–§17 | Sections 10–11: session access, authorization, honest events |
| §18 | Sections 5, 9, and sol_ui.md: production handoff |
| §23, §31 | Section 4: explicit deferrals |
| §28, §33 | Sections 13 and 16: freeze and acceptance gates |

**Final product line:** One unfamiliar scene, one evidence-backed improvement, and a production handoff the creator chose.
