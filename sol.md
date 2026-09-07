# StudioClear — Final Product and Build Specification

**Revised:** September 7, 2026

**Track:** Agentic Cinema / Parallel

**Status:** Approved implementation target: one scene, three filming options. Production comparison is planned, not shipped. Earlier diagnostic results below are dated observations; reverify current code before assigning implementation status.

**Official deadline:** September 9, 2026, 2:00 p.m. PDT / 4:00 p.m. CDT.

**Delivery target:** Verify one complete scene-to-production comparison before recording. Preserve a submission buffer; use observed progress to schedule the remaining work.

**UI contract:** [sol_ui.md](sol_ui.md).

This revision replaces the previous frozen plan at the user's request. It supersedes conflicting product/UI directions in claude_ui.md, CLAUDE.md, PROGRESS.md, and the earlier [scene revision proposal](docs/superpowers/specs/2026-09-07-scene-research-revision-desk-design.md). Those documents remain historical records; their claims of completed features are not acceptance evidence.

Keep the existing working integrations, explicit human decisions, source provenance, policy engine, and audit implementation where useful. Correctness fixes may change the pipeline and its expected outputs. There is no requirement to preserve erroneous verdicts or keep run_pipeline byte-identical.

This revision incorporates the approved narrower production-planning direction. It replaces the historical-research-first product promise and the proposed expansion into full screenplay generation. Change only the selected scene when requested; retain longer-form authoring as a future direction. Section 14 defines the production-comparison showcase; [demo_scene_video.md](demo_scene_video.md) provides its matching live test and recording script, with LAST LIGHT retained as a separate revision regression.

## 1. Product promise and competitive thesis

> Give StudioClear a scene. Compare practical ways to film it using evidence, transparent cost assumptions, and creative tradeoffs.

**Product:** A scene-to-production planning desk for independent filmmakers, storyboard artists, and producers.

**Primary job:** Understand one selected scene, confirm what filming it requires, and compare three production approaches. Contextual factual research and optional scene/dialogue revision support that decision. Preserve creative premises, including fantasy. Brand, music, and likeness questions can be recorded for human review; web search does not grant permission.

**Acceptance story:** A producer brings an unfamiliar scene, confirms requirements and production assumptions, compares a nearby practical location, an alternative travel location, and local filming with VFX, changes one constraint, then selects an approach and exports a usable brief. Existing scene research/revision remains available without forcing an edit before comparison.

~~~text
Understand scene → Confirm production requirements → Compare three options
    → Adjust constraints → Select an option → Export production brief

Optional: Review scene → Propose edit → Accept or reject → Recheck dependencies
~~~

The differentiated moment is an observable decision: changing traveling crew size, available days, or a creative constraint changes the applicable cost lines and may change the preferred approach. Explain the actual result, including overlapping ranges and missing quotes; do not force a recommendation switch for the demonstration.

Gemini interprets the scene and formulates relevant production questions. Parallel supplies retrieved information about candidate locations, production support, permit/incentive conditions, and applicable rate sources. Code performs arithmetic and constraint checks. The producer reviews assumptions and chooses an option. Google Cloud hosts the application.

Winning is an aspiration, not a claim or guaranteed outcome. Judge value comes from demonstrated behavior and measured results.

## 2. Verified starting point and implementation gaps

Assessment date: September 7, 2026. The following table preserves earlier local observations and offline diagnostics; subsequent repairs may have changed individual rows. It is not a fresh certification of the hosted deployment. Re-run relevant checks before describing any listed defect as current or any feature as complete.

| Area | Existing implementation | Required change |
| --- | --- | --- |
| Input | Paste/image routes exist; image transcript joins extracted claim snippets | Preserve complete dialogue/captions separately from visual descriptions and claims; retain original assets |
| Research | Structured evidence assessment exists, but research receives items without full scene/instruction | Pass version-bound context and intent into question planning and applicability assessment |
| Confirmation | Scene text and item list can be saved independently | Derive claims from confirmed canonical text; invalidate outdated findings/proposals |
| Revision | Proposals, acceptance, versioning, and keep decisions exist | Validate exact target occurrence, current research version, nonempty applicable evidence, and positional locks |
| Recheck | Reuses saved items without extracting revised text | Re-extract the changed scene, discover added claims, and preserve decision/source lineage |
| Handoff | Sanitized JSON exists; earlier-run citations may be absent; latest text can mix with older findings | Bind one export snapshot to an explicit scene version and include all referenced source records |
| Completion | Accepted revision can be labeled Production handoff before any recheck | Require explicit version-matching coverage; missing, failed, or stale recheck stays incomplete |
| UI outputs | Print/TXT use browser state; JSON uses a separate server builder | Render every deliverable from the same validated handoff snapshot |
| Execution | Example mode/self-test labels exist; research audit is not full provider trace | Record actual stage calls/outcomes; keep audit and self-tests secondary |
| Timestamps | Initial live run supplies current time; recheck omits it and inherits fixture default | Use actual live operation/retrieval timestamps on every path |
| Task understanding | Extraction targets clearance references; blank intent falls back to historical accuracy | Confirm the user's task and preserve genre/fictional rules before deriving research questions |
| Location questions | A bare California reference produces generic entity searches | Derive location questions from selected scene requirements, production base, and constraints |
| Production comparison | No verified filming-cost comparison was demonstrated | Implement versioned options, transparent cost arithmetic, conditional incentives, and editable assumptions |

Offline diagnostic results: an accepted revision was labeled Production handoff before recheck; earlier-run evidence references were missing from exported sources. A fresh Signal Room scene with an added cable claim triggered zero extraction calls, passed only the saved camera item to research, and returned recheck status complete. These are control-flow failures, not model-accuracy measurements.

A real citation URL establishes provenance. It does not establish that its passage supports a claim, that publishers are independent, or that a depiction is cleared for use.

## 3. Judging strategy

The official rules give equal weight to technological implementation, design, potential impact, and idea quality. They require active Parallel Search use for this track. [Official rules](https://agentic-cinema.devpost.com/rules)

| Criterion | What the submission must demonstrate | Evidence to retain |
| --- | --- | --- |
| Technological implementation | Gemini scene understanding, actual Parallel research, deterministic cost calculations, and versioned outputs | Provider events, source provenance, calculation checks, live results |
| Design | A producer understands assumptions and completes an option comparison using their own scene | Browser walkthrough, editable inputs, clear missing information, usable brief |
| Potential impact | A filmmaker can assess a filming choice and communicate the next work to a collaborator | Observed user session, decision rationale, actual task results |
| Idea quality | Creative requirements and production constraints determine relevant research and recommendations | Same scene before/after a constraint change, applicable cost differences, honest uncertainty |

Do not substitute agent counts, animated stages, citation totals, or security badges for a demonstrated outcome.

## 4. Scope and deliberate cuts

### Required for this submission

- One selected scene and one active comparison at a time, with a title. If input covers several scenes, preserve the full source and ask the user to select one for production comparison.
- Paste text or upload up to three original comic/storyboard pages.
- PNG, JPEG, and WebP only; validate decoded content, not just extensions.
- Starting limits: 4 MiB per image, 12 MiB total decoded images, 20 megapixels per image, and 20,000 characters of pasted text. Account separately for base64 request overhead if using JSON transport.
- An explicit task, genre/fictional premises, confirmed scene requirements, and exact text spans the user wants to preserve. Remove the silent historical-accuracy fallback.
- Page/scene-linked extraction with a correction step before research.
- Claim-level evidence, clear uncertainty, and separate human-review routing.
- Optional elaboration, action/dialogue rewrite, or factual correction of the selected scene, one proposal at a time with accept/reject. Creative proposals need no external factual verdict; factual corrections require applicable evidence.
- Re-extraction and research of the entire changed scene, including newly introduced claims.
- Three options: nearby practical location; one alternative travel location, domestic or international; local filming with VFX. At most two researched jurisdictions per comparison.
- Confirmed production base, dates, budget/currency, traveling/local crew counts, preparation/shoot/travel days, creative constraints, and VFX shot assumptions.
- Editable cost ranges with source/estimate/quote provenance, explicit missing costs, conditional incentives, and unconfirmed availability.
- A producer-selected option and a consistent production brief: scene TXT, printable PDF, and structured JSON.
- Authentic runtime metadata, explicit demo modes, durable hosted runs.
- Existing demo remains accessible as a clearly labeled example.

### Deferred until after submission

Full-story/screenplay generation; extensive multi-scene dialogue development; production-wide scheduling/optimization; worldwide tax-law coverage; automated tax filing; crew/location booking; PDF/DOCX import; generated video; comic art redrawing; face identification; automated rights clearance; full screenplay continuity graphs; batch revisions; external publishing; email outreach; additional partner tracks; new orchestration frameworks; semantic memory; enterprise SSO; multi-user collaboration.

Image revision in this build means dialogue/caption text and panel-specific production notes. Uploaded artwork remains unchanged. A proposed drawing change stays marked as pending art work and cannot be verified as visually applied.

If time tightens, reduce source pages and the number of quoted cost lines while retaining one useful, honest comparison. Do not present an incomplete subtotal as a full production budget. If only text input works, state that limitation and leave the comic objective incomplete. No promise of winning follows from passing this specification.

## 5. User workflow and intent contract

1. **Bring a scene.** Upload pages or paste an idea/script. Preserve the full input; select one scene when it contains several dramatic events.
2. **Choose the task.** Show Plan this shoot as the visible default, with Review factual details and Improve this scene as alternatives. Confirm intent, genre, creative rules, and protected dialogue. Never silently substitute historical research.
3. **Confirm understanding.** Present a concise scene summary, full transcript, setting, cast, props, effects, and unknowns. Distinguish user text, image transcription, interpreted action, and creative suggestions.
4. **Confirm production inputs.** Supply the brief described in section 6A. Budget/location-dependent work waits for those inputs; optional writing can continue without them.
5. **Compare options.** Research relevant questions and show three approaches with evidence, costs, creative fit, availability limitations, and next actions.
6. **Adjust constraints.** Edit crew/day/rate assumptions and recalculate. Research new conditions only when needed, recording what was reused or refreshed.
7. **Select for further planning.** Persist the producer's choice and rationale against the comparison version. Optional scene edits use preview/acceptance and invalidate affected comparisons until refreshed.
8. **Export.** Download current scene text and a production brief containing alternatives, assumptions, evidence, conditional incentives, and outstanding work.

Intent must change observable behavior: research scope/prioritization, the question asked, or revision constraints. Echoing the prompt in a report is insufficient.

Exact locked text is enforced with code. Semantic constraints such as preserving a joke or character motivation are model-assessed and user-reviewed; do not call them mechanically guaranteed.

For a gold-touching-stone premise, recognize the fantasy rule and leave it intact. A reference to California is context, not an assertion to mark UNRESOLVED. An unfinished phrase such as “she is a source of plague not…” remains an unresolved creative choice; optional completions are proposals. Do not fabricate dialogue in the source transcript. Offer scene elaboration separately from sourced research, and do not disable writing because no factual contradiction was found.

## 6. Architecture and execution

Extend the existing Python/FastAPI backend and vanilla-JavaScript frontend. Keep provider adapters and deterministic policy evaluation. Do not introduce a new frontend framework solely for this enhancement.

~~~text
Browser: pages/text + selected task + instruction + locked spans
  → validate and persist source material
  → Gemini reads the complete scene and proposes production requirements
  → producer confirms scene version, requirements, constraints, and cost inputs
  → formulate focused questions for three production approaches
  → authorize Parallel searches and register actual retrieved evidence
  → validate source applicability and identify missing quotes/requirements
  → code calculates comparable costs and checks constraints
  → producer adjusts assumptions; code recalculates and explains differences
  → producer selects an option for further planning
  → export one snapshot of scene, comparison, sources, and remaining work

Optional scene review: propose → accept/reject → new version → recheck dependencies
~~~

**Execution approach:** Use bounded requests for extraction, research, comparison, proposal, acceptance, and recheck. Persist operation IDs and results. The frontend shows an indeterminate busy state while a request runs. Acceptance persists independently of recheck; failed research does not erase producer inputs. Simple quantity/rate recalculation uses code and needs no model call.

Do not claim streaming progress or cancellation unless the backend implements them. A browser timeout does not prove server cancellation. Use operation IDs and idempotency keys so retries can recover prior results.

**Starting research budgets:** At most eight prioritized findings per analysis; at most two search attempts per finding; at most five candidate sources per attempt. Show unresearched findings as “Not researched: run limit reached.” Record actual attempts and tune the budgets against live latency before freeze. These are scope controls, not measured performance claims.

Research follow-up must be purposeful: refine an ambiguous entity, seek a primary source, or investigate conflicting evidence. Stop on sufficient evidence, explicit failure, or budget exhaustion. Log the reason and actual tool response.

## 6A. Production comparison contract

### Confirmed brief and options

Store production base city/country, filming window, reporting currency, optional budget ceiling, traveling/local crew and principal cast counts, preparation/shoot/travel days, accommodation nights, location requirements, and hard creative constraints. Missing dates/rates remain unknown. Do not infer nationality, tax residence, production-company eligibility, or travel willingness from the scene setting. Require a base and a selected scene before recommending nearby locations; an unknown budget permits comparison but not an affordability verdict.

Offer three fixed approach slots: NEARBY_PRACTICAL, TRAVEL_PRACTICAL, and LOCAL_VFX. The producer selects the alternative region/country, or confirms a research-suggested candidate, before detailed comparison. Limit jurisdiction research to two. A slot may return infeasible or insufficient information; do not invent a viable location to fill it. Research location/permit feasibility for the actual intended activity. A public destination description is not proof filming is allowed there.

Ask up to eight prioritized production questions across the comparison, with at most twelve total Parallel attempts including follow-ups and at most five candidate results per attempt. Record skipped questions and budget exhaustion. These are implementation limits, not observed latency claims.

### Cost calculation and provenance

Each cost line stores category, description, quantity/unit, low/high unit rate, original currency, reporting-currency conversion basis/date, source reference or producer note, and provenance: sourced published rate, supplier quote, producer estimate, or unknown. Include labor, travel, accommodation, local transport, equipment, location/permits, sets/props, VFX, and separately entered contingency. Record whether a rate includes tax, overtime, or related charges; uncertain inclusions remain explicit. Do not reuse current prices outside their applicable dates without a stale-rate warning.

Use decimal arithmetic. Line range = quantity × unit-rate range; subtotal = sum of known line ranges in the reporting currency. A contingency percentage applies to a displayed eligible subtotal and is counted once. Missing rates or conversions produce an incomplete estimate, never zero-valued free items. Do not label a known-cost subtotal as a complete total. Show assumptions for paid travel/preparation days and locally hired versus traveling crew. Use shared expense identifiers to avoid charging the same flight, lodging, or equipment rental twice within an option. Do not sum the mutually exclusive option budgets.

Savings comparisons use the same scene, dates, scope, and a named baseline. Display ranges and exclusions. Only claim one option is cheaper across the estimate range when its upper bound is below the other's lower bound and cost coverage is comparable. Otherwise say ranges overlap or comparison is incomplete. Do not invent precise savings from model prose.

### Incentives, availability, and effects

Show costs before incentives as the default. A separate conditional scenario may show potential benefits only when an official source and explicit qualifying-expenditure assumptions support the calculation. Include jurisdiction, program, effective date, rate basis, conditions, minimum spend/caps where known, certification/application requirements, tax treatment, payment timing, and unanswered eligibility questions. Do not apply a headline percentage to the entire budget or count unconfirmed incentives as cash available for the shoot. If a required fact is missing, show not calculated and a review task. These are sourced planning scenarios, not eligibility determinations or tax filings.

Crew and studio directories establish leads. Availability stays unconfirmed without a dated supplier response or appropriate live availability data. Do not contact, hire, reserve, or book anyone through this feature. Record next actions for the producer.

For LOCAL_VFX, confirm shot count, shot duration, camera movement, transformation/water/reflection complexity, practical set/plate requirements, and revision allowance. Use producer estimates or applicable supplier quotes for costs; generic vendor pages do not establish a quote. A proposed rewrite reducing effects is a creative option that requires acceptance before its lower-complexity assumptions apply to the current scene.

### Recommendation and versioning

Evaluate confirmed hard constraints first. Recommend investigating an eligible option when its costs, creative suitability, and evidence support that recommendation. Otherwise return a qualified shortlist or insufficient information. Explain tradeoffs and assumptions; do not use invented quality scores. A budget overrun can eliminate an option even if it is the cheapest; uncertain availability cannot be called confirmed feasible.

Recalculation creates an immutable comparison revision with a parent ID and change summary. Reuse applicable source records with their original provenance; refresh research when dates, jurisdiction, or requirements invalidate them. Scene changes mark dependent comparisons stale. Selection requires a current comparison, and is recorded as selected for further planning, not approved for expenditure.

Planning references: [BFI certification guidance](https://www.bfi.org.uk/apply-british-certification-expenditure-credits), [British Film Commission production support](https://britishfilmcommission.org.uk/why-the-uk/how-we-support-you). These illustrate required source quality; every actual jurisdiction/rate must be researched for the user's case.

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

### One authoritative scene version

Canonical scene content is the source of truth. Claims are derived from an identified version, never a separately editable competing transcript. Store complete transcribed speech/captions, interpreted visual action, and original assets distinctly. A list of detected references is not a scene transcript.

Bind research, proposals, decisions, and rechecks to scene ID/version. A confirmed text/context/instruction change invalidates dependent current results. Pass full relevant context and instruction to question planning and evidence applicability assessment. Ask a specific question (for example, availability of a prop in the scene's year), not merely whether an entity exists.

Validate edit targets using version-bound span locations and original text. Refuse missing/ambiguous targets and no-op edits. Each protected occurrence must remain unchanged; finding the same string elsewhere is not lock validation. Require nonempty, applicable evidence for a proposed factual correction rather than merely filtering IDs against all sources in the run.

A proposal includes revision_id, base_scene_version, target span IDs, original text, proposed edits, rationale, grounded evidence references, exact-lock validation, semantic-constraint notes, and any art-change instructions. Each evidence reference is the pair `{origin_run_id, source_id}` so a recheck cannot accidentally reinterpret `S001` from a different run.

Record proposal kind: creative_edit or factual_correction. The evidence requirements below apply to factual corrections and any asserted factual basis of a creative edit. A creative elaboration/dialogue proposal may have no citations; label it AI-proposed creative text and enforce the same target, version, user-acceptance, and lock rules. Never label invented narrative as researched fact. Recheck derived factual claims and production requirements after either kind of accepted edit.

**Rules:**

- Apply structured edits to the canonical scene text. Editing only item.text_span is insufficient.
- Return proposal text and evidence IDs; resolve citation links on the server.
- Preserve all exact locked spans. If the requested correction conflicts with one, return a conflict explanation without a silently altered proposal.
- Do not propose a factual assertion as corrected when evidence is unresolved.
- Validate that the proposal's base version is current before acceptance.
- Rejection preserves the scene and records the user's choice.
- Repeated acceptance with the same operation key creates no duplicate versions.
- Acceptance creates a new immutable scene version and marks previous findings stale.
- “Keep as written” is a persisted human decision with an optional note. The UI may call it recorded only after the server saves it.
- Recheck re-extracts all claims in the changed scene; match retained, modified, added, and removed claims using stable IDs and explicit lineage.
- Reuse unchanged-claim evidence only when claim, context, freshness policy, and provenance remain applicable. Record reuse. Research changed and newly introduced claims through Parallel.
- A removed claim is “Removed in revision,” not “Verified.” A newly introduced unsupported detail prevents a “fully rechecked” completion message.
- Retain both before and after results. Recheck may remain MIXED or UNRESOLVED.
- A failed recheck leaves the accepted version intact with a retryable failure; do not fall back to old green statuses.

Separate operation completion from research coverage and factual outcomes. Record the exact rechecked version, extraction outcome, assessed/skipped claim IDs, and failures. A completed recheck may have UNRESOLVED findings, but skipped or failed research must remain explicit; never imply all claims were checked. Preserve keep/review decisions for retained claims with original version/time provenance; changed claims require renewed review, not silently inherited approval.

Text-only changes cannot establish that a depicted visual error was corrected. If art must change, export the art note and keep visual verification pending until updated artwork is supplied.

## 9. Versioned data and API contract

These are target contracts; some existing scene endpoints already implement portions. New comparison and creative-edit routes are planned. Keep sol_ui.md in sync and preserve legacy saved-report access.

### Required stored entities

| Entity | Required fields |
| --- | --- |
| Scene | scene_id, owner/session scope, source type, ordered assets, current_version |
| Scene version | version, parent_version, canonical text, page/panel/span IDs, creation time, instruction and exact locks |
| Run | run_id, scene_id/version, schema_version, policy_version, status, provider execution metadata, operation IDs |
| Finding | stable finding_id, scene/page/panel/span references, exact claim, research status, routing, evidence IDs, limitations |
| Source | source_id, raw URL/title/passages, query, retrieval time, provenance and independence notes |
| Revision | revision_id, base/result versions, structured edits, rationale, `{origin_run_id, source_id}` evidence references, constraints, decision |
| Recheck | operation_id, before/after run IDs, claim lineage, unresolved/new/removed claims, status/error |
| Event | sequence, UTC time, run/version, actor category, actual action/result, operation ID, hash-chain fields |
| Production brief | scene_id/version, task, confirmed requirements, producer inputs, unresolved creative choices |
| Shoot comparison | comparison_id, parent_comparison_id, scene_id/version, input snapshot, three option slots, calculation version, source records, operation outcome, expiry |
| Cost line | category, quantity/unit, low/high rate, original/reporting currency, conversion basis/date, provenance, source or estimate note, shared expense ID |
| Planning decision | comparison_id, option_id, selected-for-planning status, producer rationale, actual decision time |

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
| POST /scenes/{scene_id}/creative-proposals | Propose optional scene elaboration/dialogue edits against expected scene version; no factual finding required |
| POST /scenes/{scene_id}/shoot-comparisons | Research/calculate a brief against expected scene version; optional parent_comparison_id creates a new revision for changed assumptions |
| GET /shoot-comparisons/{comparison_id} | Read saved brief, options, calculations, sources, limitations, and status |
| POST /shoot-comparisons/{comparison_id}/decision | Persist option choice/rationale for further planning; require current scene/comparison and idempotency key |
| GET /shoot-comparisons/{comparison_id}/handoff | Read/create the single persisted snapshot of the selected comparison and its scene; matching scene review is optional |
| GET /report/{run_id} | Versioned structured handoff; frontend supports print/PDF |
| GET /scenes/{scene_id}/assets/{asset_id} | Authorized preview of uploaded material |
| GET /operations/{operation_id} | Recover persisted outcome/error after an uncertain timeout |
| DELETE /scenes/{scene_id} | Remove user material and associated runs/assets under the documented retention policy |

Keep existing /policy, /health, and legacy /upload behavior available for the explicit legacy demo. Prevent arbitrary user content from silently selecting mock providers.

The shareable handoff is an allowlisted export schema rather than a dump of the internal run object. It contains the complete original and accepted scene text, scene/version lineage, instruction, protected spans, accepted/rejected/keep decisions, evidence references and source records, recheck lineage, unresolved work, and pending art notes. It excludes `owner`, session identifiers, cookies, internal authorization context, and other access-control material. Text, PDF, and JSON are the product outputs; generated film/video remains deferred.

Creative proposals use the existing revision-decision route with their recorded proposal kind. Comparison creation accepts the confirmed brief, editable rate/quantity assumptions, expected scene version, and an idempotency key. Invalid inputs fail validation; absent prices return explicit incomplete estimates. The server performs all calculations and records actual research failures. A retry must not create duplicate accepted edits, comparison revisions, or planning decisions.

The comparison handoff adds comparison_id, parent ID, selected option/decision, all three approaches, cost lines/totals/coverage, currency and conversion basis, source dates, conditional incentives, unconfirmed availability, and remaining quotes/tasks. Preserve originating evidence tuples across comparison revisions. Planning sources use the same source-provenance contract as scene research. Legacy reports remain readable and receive no synthetic comparison data.

### Single handoff snapshot and export validation

- Build and identify one handoff snapshot using `handoff_id`, `scene_id`, `scene_version`, `run_id`, and `exported_at`. Screen preview, TXT, printable PDF, and JSON consume that same snapshot. Do not join an old run to `versions[-1]` or construct a second client-side report.
- Snapshot evidence cited by a proposal before later research can replace the current source list. Export the union of current finding sources and historical revision sources, keyed by `{origin_run_id, source_id}`. Preserve their original query, passage, and retrieval time; never relabel old records as new sources.
- Validate that every exported evidence reference resolves to exactly one included source and every quoted passage matches its stored record. An unresolved reference blocks the validated handoff with a structured error; standalone scene text can remain available as an explicitly incomplete draft.
- Export accepted/rejected/keep decisions with their version and actual decision time. Unresolved work includes the question, limitation, human decision, and next action, not just a claim/status pair.
- No accepted change: Research draft. Accepted change with absent, pending, failed, or version-mismatched recheck: Accepted revision — recheck incomplete. A version-matching completed check can produce a Production handoff, with any skipped research, unresolved questions, and pending artwork prominently disclosed. This label never means clearance or that every finding is supported.
- A new scene edit leaves an old snapshot as labeled history; it cannot become the current handoff. Revalidate ownership and fixed expiry whenever serving or generating a snapshot.

The preceding Research draft/recheck labels describe the scene-research component. A production comparison does not require an accepted text edit or a factual contradiction. Its heading is Production planning brief with independent estimate status: Complete estimate, Incomplete estimate, or Stale comparison. A complete estimate means all modeled cost categories have explicit values/assumptions, not that suppliers, incentives, or real-world feasibility are confirmed. Display scene-review/recheck status separately, including Not requested. Both components must reference the same scene version if combined. Export a saved incomplete planning brief with its limitations; block mismatched versions or unresolved citation references from a current validated snapshot.

Comparison snapshots add comparison_id and calculation_version to the existing identifiers; run_id may be absent when scene research was not requested. TXT contains the current scene and minimal snapshot/version identification; PDF/JSON contain the production comparison. They share one snapshot identity without requiring a cost table inside the screenplay text.

Separate fixture provenance from operation time. A simulated example keeps its fixture timestamp in a clearly named provenance field; revisions, decisions, rechecks, and exports use their actual server UTC timestamps. Never present a fixture timestamp as the creation time of later user actions.

Return structured errors with code, message, retryable, operation_id, and affected page/finding. Use 409 for stale-version conflicts, 413 for size limits, 422 for invalid/unreadable input, and an appropriate 5xx for unavailable live providers. Preserve unaffected pages and user-entered text when possible.

## 10. Hosted reliability, privacy, and storage

Do not put new personal uploads into a publicly enumerable /runs list or rely on hard-to-guess IDs as the sole access control.

Use a lightweight opaque session cookie and enforce ownership on reads, assets, edits, decisions, rechecks, and deletion. This is a single-session workspace, not authenticated studio identity or enterprise RBAC. Separate public examples from private session runs.

For the hosted path, use a dedicated private Cloud Storage bucket for source images and run/version JSON. Use generation preconditions or equivalent compare-and-swap to prevent lost updates. Retain local filesystem storage for development only. Do not put assets directly on a public bucket.

Cloud Run instances must read the same durable state. Validate that a run survives an instance restart and can be read through a different instance. Keep secrets server-side in Secret Manager with narrowly scoped resource access.

### Twenty-four-hour lifecycle rule

- Set `expires_at = scene.created_at + 24 hours` when the scene is created. Every related asset, run, revision, recheck, and operation inherits this fixed deadline; edits and rechecks never extend it.
- Production briefs, comparisons, saved rates/quotes, decisions, and handoff snapshots inherit that same deadline. Recalculation and export never restart the clock.
- After validating session ownership, enforce expiry on every read, asset request, mutation, decision, recheck, and export. Return `410 Gone` for expired material. Revalidate before saving a long-running result so processing cannot resurrect an expired scene.
- Store private user data under the dedicated `studioclear/` prefix in a private Cloud Storage bucket. Write the original scene creation time to each related object's Custom-Time metadata.
- Configure lifecycle deletion for that prefix using `daysSinceCustomTime: 1`, plus `age: 1` as a fallback for legacy objects without Custom-Time. Merge these rules with unrelated bucket rules and keep permanent public examples outside the disposable prefix.
- Use a dedicated disposable-data bucket with object versioning and soft delete disabled. Do not disable either on a shared bucket. Do not apply a retention lock that would prevent user-requested early deletion.
- Application access ends exactly at `expires_at`; Cloud Storage lifecycle deletion is asynchronous and can occur later. Describe this accurately rather than promising physical deletion at exactly 24 hours. A user-triggered delete immediately revokes application access and requests deletion of related objects.
- Backfill existing private scenes and runs from the original scene creation timestamp; use object creation time only when the original cannot be recovered. Keep source text/images out of ordinary logs.

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
- Fantasy rules and bare place names do not automatically become factual contradictions or generic location queries; the selected task changes research questions.
- Creative scene/dialogue proposals work without a CONTRADICTED finding, remain unaccepted until the user decides, and preserve exact locks.
- Decimal cost arithmetic, day/night quantities, currency conversion, explicit inclusions, contingency, and shared expenses; no double-counted flights/rentals.
- Unknown rates/conversions remain incomplete rather than zero. Compare ranges only with equivalent coverage; overlapping estimates do not imply a guaranteed saving.
- Incentives apply only in an explicitly conditional scenario with sufficient assumptions; missing eligibility or rate basis prevents a calculated benefit.
- Availability leads remain unconfirmed. New dates/jurisdictions invalidate applicable rates and research. Constraint failures prevent an unqualified recommendation.
- Changed scene content makes dependent comparisons stale; cost-only recalculation preserves applicable source provenance and creates a new comparison revision.
- A scene with no accepted correction can still produce a planning brief; PDF/JSON and scene TXT resolve to the same snapshot and version.

### Primary product gate: gold-stone scene

Use the user's rough premise as input: a romantic date becomes a California gold/sea-treasure adventure; a discovered stone turns touched objects, food, and people into gold; the ending is unfinished. Preserve the complete premise, identify fantasy intent, and ask the user to select one scene for comparison. Default suggested selection is the discovery/first-transformation scene, pending confirmation; do not combine the entire journey into one shoot.

Confirm the selected scene's environment, cast, transformation shot requirements, and unresolved decisions. Optional elaboration may suggest action/dialogue but cannot replace the premise or silently finish its ending. No generic California link collection counts as production research.

Given a producer-supplied base, dates, crew, currency, and rate assumptions, compare nearby practical, alternative travel, and local/VFX approaches. Record sources and missing quotes. Change traveling crew size or available days; verify exactly which cost/constraint terms change. A recommendation may stay the same. Save a choice and export consistent outputs. All test budgets/rates are labeled synthetic when used offline; a live demonstration records real searches and distinguishes estimates from quotes.

This is the primary submission acceptance story. Signal Room and LAST LIGHT below remain regression material for evidence, image reading, creative constraints, and recheck; they do not replace the production-comparison gate.

Keep deterministic fixture tests for regression, but do not call their outputs live model quality measurements.

### First repair gate: Signal Room

Use this original text as the first regression case, not another Apollo fixture:

~~~text
INT. SIGNAL ROOM - NIGHT
SUPER: 1935

ELSIE
Keep the light on. I promised I would return.

She photographs the logbook with a digital camera.
An unidentified crest is stamped on the door.
~~~

Instruction: "Check whether the props fit the stated year. Preserve Elsie's dialogue exactly. Do not invent an identity for the crest." Lock the complete dialogue occurrence above.

1. Confirm that the complete scene survives extraction and that the research question includes the 1935 setting. Do not preassign a factual verdict or a replacement prop; retrieve applicable evidence live.
2. Inspect a source-backed proposal, accept only a justified edit, and verify that dialogue, unrelated action, and scene context remain intact. The unidentified crest must not acquire an invented identity or permission claim.
3. In a separate controlled edit, append: "A caption says: The first transatlantic cable opened in 1858." Save a new version and recheck. The added claim must be extracted and researched or explicitly marked skipped/failed; its truth is not assumed by this test.
4. Verify that older accepted-change citations still resolve, keep decisions remain in history, and all exports refer to the identical checked version.
5. Repeat with an original readable storyboard page, including dialogue that is not itself a researchable claim. Verify actual image reading and full transcription, not concatenated extracted references.

The September 7 offline probe exercised step 3's control flow with a stubbed research function: only the saved camera claim was passed through, extraction calls were zero, and recheck reported complete. No live provider, browser, historical validation, or image test was performed in that probe. Convert this observed failure into an automated regression before changing pipeline behavior.

Once used for development, Signal Room is a regression case, not a held-out evaluation example. Reserve different material for final live evaluation.

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

Live acceptance must exercise actual source reading, confirmed requirements, Gemini/Parallel operations, the three option slots, transparent estimates, one changed producer constraint, selection, and export. Verify one optional accepted revision and dependent recheck in a separate regression run. If images are advertised, test actual uploaded pixels. Browser checks cover narrow/wide layouts, keyboard operation, errors, and readable print output. Record build and artifacts; old test counts are not new verification.

## 13. Implementation order and freeze

Each phase has a gate. Do not polish an unsupported conclusion or record planned features as working.

| Phase | Work and principal files | Exit condition |
| --- | --- | --- |
| 1. Scene understanding and correctness | Task selection; source/version/proposal/recheck integrity | Fantasy intent survives; selected scene requirements and contextual questions replace bare-name searches; outstanding integrity defects are reproduced and repaired |
| 2. One working comparison | Production brief; Gemini/Parallel research; deterministic cost module | Three approach slots expose comparable costs or explicit missing information; a producer-input change recalculates correctly |
| 3. Usable decision and handoff | Comparison UI; selection; shared export snapshot | A producer can choose an approach, understand the basis, and export a version-consistent planning brief |
| 4. Unfamiliar-user verification | Fresh scene; observed producer; source/privacy/expiry checks | Useful decision without coaching, actual failure observations, reliable recovery and private storage |
| 5. Record and submit | Runtime evidence; honest video; README/Devpost | Submission describes only verified behavior, with traceable results and no unsupported savings claims |

Integrate private storage, session scope, and expiry with the first new entities; verify them again before release.

Use the verified submission deadline above, but schedule remaining blocks from actual progress. The first milestone is one working production comparison. Do not spend another block on artwork or added features if this milestone still returns generic links or unsupported totals. Freeze only the demonstrated scope and retain time for recording/submission.

If a phase overruns, reduce pages/findings and optional UI features. Do not skip correctness, falsely mark completion, or present a replay as fresh processing. Reassess the schedule against actual remaining hours.

## 14. Showcase and three-minute video

Use one original scene with a real production choice. The selected gold-stone transformation scene is the primary example; LAST LIGHT can exercise regression cases. Collect a producer-supplied base, dates, constraints, and rate assumptions before rehearsal. Do not prescribe a winning location or savings figure in advance.

A creator's original comic can be the input. Frame the task for a filmmaker adapting it, with a concrete production decision.

| Time | On-screen action | Claim demonstrated |
| --- | --- | --- |
| 0:00–0:15 | Preview the actual scene and resulting three-option comparison | The producer's decision and the product outcome |
| 0:15–0:45 | Input/confirm selected scene, fantasy rule, production requirements, and brief | Real scene understanding and user control |
| 0:45–1:25 | Open practical/travel/VFX options, source passage, and cost assumptions | Relevant research and transparent calculations |
| 1:25–2:00 | Change traveling crew size or available days; recalculate | Actual cause and effect, with no forced ranking change |
| 2:00–2:30 | Inspect tradeoffs, missing quote/conditional incentive, and select an approach | A qualified, usable production decision |
| 2:30–3:00 | Export the brief, show actual provider activity, report any observed user result | Traceable handoff and demonstrated usefulness |

Rehearse using real runs. A recording may cut waiting time if labeled; do not replace the result with fixture output. Any replay must visibly say “Recorded example” with its original provenance. Mock examples must say “Simulated example.” Neither demonstrates a newly uploaded image being processed live.

Keep full elapsed processing time and failures alongside edited footage. Label assumptions, estimates, recorded runs, and limitations. Do not treat a purpose-built example as a held-out benchmark. A reader should understand why the producer selected an approach and what must still be confirmed. Optional rewrites require separate acceptance and recalculation before their reduced effects requirements can affect the current budget.

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

- Bring a scene or rough premise, preserve its creative rules, and select one scene for planning.
- Confirm production requirements and enter the producer inputs needed for a meaningful comparison.
- Inspect nearby practical, alternative travel, and local/VFX approaches with sourced facts, editable cost ranges, and explicit missing information.
- Change a crew/day/creative constraint and understand the resulting calculation and feasibility differences.
- Distinguish before-incentive costs from conditional incentive scenarios and availability leads from confirmations.
- Select an option for further planning and export its assumptions, alternatives, sources, and outstanding work without needing to accept a text correction.
- Bring an unfamiliar storyboard or pasted scene and give a meaningful instruction.
- Inspect and correct what the system read.
- Open a finding tied to the material and assess its actual supporting or contradicting passage.
- See where evidence is insufficient without an invented confidence score.
- Request one small supported revision and compare it to the original.
- Accept or reject the revision, with protected text enforced.
- Recheck the changed scene, including newly introduced claims.
- Distinguish applied text changes from pending art instructions.
- Export the accepted text, sources, remaining questions, and decision history.
- Download the complete production handoff as scene text, printable PDF, and sanitized JSON with no session/access identifiers.
- See the exact 24-hour expiry and lose application access at that deadline without an edit extending it.
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
| E6, §21 | Section 14: functioning production comparison; revision loop remains a supporting regression |
| E8.1 | Section 7: provenance plus passage/claim assessment |
| E8.2 | Sections 10–12: untrusted input, tool boundaries, tests |
| E8.3, §19 | Section 11: audit consistency and its limits |
| §12–§14 | Sections 7–8: research status, human routing, revision authority |
| §15–§17 | Sections 10–11: session access, authorization, honest events |
| §18 | Sections 5, 9, and sol_ui.md: production handoff |
| §23, §31 | Section 4: explicit deferrals |
| §28, §33 | Sections 13 and 16: freeze and acceptance gates |

**Final product line:** One scene, three ways to film it, and a production decision the creator can explain.
