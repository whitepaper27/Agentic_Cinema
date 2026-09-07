# StudioClear — Final UI and Interaction Specification

**Revised:** September 7, 2026

**Status:** Approved UI target: one scene, three filming options. Comparison screens are planned, not shipped. Reverify current behavior before marking requirements complete; earlier diagnostic failures are historical observations.

**Product/API authority:** [sol.md](sol.md).

**Implementation:** app/frontend/index.html; existing vanilla JavaScript and CSS.

**Current hosted app:** https://studioclear-602811764567.us-central1.run.app/

This replaces the earlier Agent Operations Desk specification and conflicting UI directions in claude_ui.md and the prior scene-revision proposal. Preserve useful existing evidence, policy, decision, and print components. Historical test counts, deployment revisions, and “all data is real” claims are not verification of this design.

The approved scope adds a focused production comparison and optional selected-scene elaboration. Full screenplay/story generation, extensive dialogue development, worldwide tax coverage, booking, and generated video remain deferred. This document and sol.md supersede the broader unimplemented story-generation proposal. The matching live test and recording sequence are in [demo_scene_video.md](demo_scene_video.md).

## 1. Experience objective

A producer brings one scene, confirms its creative and filming requirements, compares three ways to shoot it, adjusts practical constraints, and exports a production brief. Optional factual review or scene/dialogue rewriting remains available.

The source scene, production decision, cost assumptions, and remaining unknowns are the visual center. Execution and governance are supporting detail.

**Five-second comprehension test:** On arrival, a user can tell what to upload, what instruction to give, and what they will receive.

**End-to-end test:** With unfamiliar material and their own production inputs, a user can compare options, change a constraint, select an approach, and export a useful brief. A user may keep their original scene unchanged throughout.

Opening copy:

> **Find a practical way to film your scene.**

> Bring a scene or storyboard. Compare a nearby location, a travel location, and local filming with VFX using evidence and editable cost assumptions.

Primary action: **Plan a scene**.

Secondary action: **Try an example**.

Do not promise legal clearance, automatic comic redrawing, guaranteed accuracy, or a finished film.

## 2. Information architecture

Use four primary views and secondary Run details:

| View | Purpose | Availability |
| --- | --- | --- |
| Scene brief | Material, selected task, source/requirements confirmation, producer inputs | Default entry |
| Shoot options | Three approaches, sources, assumptions, costs, constraints, selection | After confirmed scene and minimum production brief |
| Scene review | Optional elaboration/dialogue proposals, factual findings, acceptance, recheck | After a scene exists; creative actions need no research finding |
| Handoff | Scene text, saved comparison/choice, evidence, assumptions, outstanding work | After a comparison or scene-research result exists; show component status |
| Run details | Actual operations, providers, failures, policy, audit | Secondary link, labeled Execution internally if needed |

Use a compact header with title, scene version, comparison revision/status, and expiry. “New scene” starts a separate workspace; preserve drafts until the user explicitly discards them. Changing a scene marks its comparison stale; show that consequence immediately.

The Scene brief is the front door for pasted ideas/scripts and comic pages. If input spans several scenes, show a suggested breakdown and require selection of one for comparison. Preserve the whole source and label any inferred scene boundaries.

Remove the ADK checkbox from the normal user journey. Runtime routing is an implementation choice and remains visible in Execution.

## 3. Desktop layout

At approximately 1200–1440 px, Scene brief and Scene review use a two-column workspace: about 45% source and 55% understanding/review. Shoot options uses a compact source/requirements strip above three comparable cards, with a full-width assumptions/cost detail panel beneath. Stack cards on narrow screens.

~~~text
StudioClear   Project title                     Scene v2   Recheck pending
Scene brief       Shoot options       Scene review       Handoff       Run details

Task: Review selected detail. Preserve the scene's fantasy premise and dialogue.
Protected text: 2 spans                                      Edit intent

┌──────────────────────────────┬────────────────────────────────────────┐
│ Page 1 of 2      Zoom  Fit    │ Findings                               │
│                              │ Needs attention 3   Supported 1        │
│ Original storyboard          │                                        │
│                              │ Page 1 · Panel 2 · Contradicted         │
│ [selected panel, if located]  │ The exact disputed claim               │
│                              │ Why this needs attention               │
│                              │                                        │
│ Transcript / accepted text   │ Evidence                               │
│ Show original / Current      │ Retrieved passage · Source · Relation  │
│                              │ View source                            │
│                              │                                        │
│ Pending art notes, if any    │ Propose a small revision                │
└──────────────────────────────┴────────────────────────────────────────┘
~~~

Selecting a finding keeps the source visible, identifies its page/panel, and opens the corresponding evidence. Avoid moving the user into an unrelated dashboard.

Source highlighting is conditional on validated coordinates or text-span locations. When precise localization is unavailable, show “Page-level location” and navigate to that page.

## 4. Scene brief: input and intent

### Material controls

Provide two explicit modes: **Storyboard / comic pages** and **Paste a scene**. Preserve each draft when switching modes; submit only the selected mode.

**Images:**

- Visible upload button plus drag-and-drop.
- Accept PNG, JPEG, and WebP; up to three pages.
- Show limits adjacent to the control: 4 MiB/page, 12 MiB total, 20 MP/page.
- Show thumbnails with filename, page order, remove, and move earlier/later controls.
- Provide a keyboard-accessible file picker and reorder controls.
- Validate client-side for quick feedback; backend validation remains authoritative.
- Revoke temporary object URLs when previews are replaced or removed.

**Text:**

- Large textarea with a real scene example as placeholder, not prefilled user content.
- Hint: “Paste dialogue, captions, or a screenplay scene. Special headings are optional.”
- Show character count against the 20,000-character limit.
- Empty or whitespace-only input disables submission.
- Do not advertise PDF/DOCX until implemented and verified.

### Instruction

Task selector: **Plan this shoot** (visible default), **Review factual details**, or **Improve this scene**. A task selects the operation; it does not rewrite the user's intent.

Instruction label: **What matters for this scene?** Example: “Keep the gold-touching power and dialogue. Compare practical locations with a local/VFX approach.”

An empty instruction must not silently become “Check historical accuracy. Preserve the dialogue.” Show the selected task's interpretation and confirm genre, fictional rules, and unknowns. Historical research is requested explicitly or driven by a specific factual question.

Allow selecting exact transcript/text spans to protect after extraction. Do not claim the app can deterministically preserve a semantic quality such as humor.

### Privacy and action

Before upload, show the configured retention and processing disclosure in plain language. Once the lifecycle in sol.md is implemented and verified, use:

> **Available for 24 hours after creation. Access expires automatically; stored copies are then removed through automated cleanup. Editing does not extend this time. Downloaded copies remain with you.**

After creation, show the exact UTC expiry and a local-time rendering in the project header and Handoff. Add **Delete now** and remind the user to download the handoff before expiry. Do not promise physical deletion at exactly 24 hours because storage lifecycle cleanup is asynchronous.

The user should understand that uploaded material is processed with Gemini and research questions are sent to Parallel. Keep credential names and setup instructions out of this flow.

Primary button: **Read my scene**.

Busy label: **Reading your scene…**

On success, continue to Confirm understanding. Reading does not silently initiate paid location research. Writing can proceed while production-specific inputs are still missing.

## 5. Confirm understanding and requirements

Show the source and extracted content side by side. Keep the uploaded page or complete pasted scene available throughout confirmation, Scene review, Shoot options, revision comparison, and recheck:

- Page thumbnail/preview and page number.
- Candidate panel labels and editable dialogue/captions produced from the actual image extraction; do not initialize image transcripts as blank placeholders when readable text was extracted.
- Preserve every readable dialogue/caption, including text with no researchable claim. Joining extracted claim snippets is not transcription. Keep original artwork, transcription, and interpreted action distinct.
- A separate description of visible action; distinguish transcription from model interpretation.
- Candidate references and factual claims tied to their text/page.
- An option to correct misreads.
- Exact-text lock controls.
- Current instruction, still editable.
- Confirmed summary, genre/fictional rules, selected scene, environment, cast, props, interiors/exteriors, period, and effects requirements.
- Unfinished story choices shown explicitly; proposed completions never replace the original without acceptance.
- Primary action for planning: **Confirm and add production details**. For factual review: **Confirm and research**. For writing: **Review a scene proposal**.

Suggested correction copy: “Check that we read this correctly before researching it.”

Visual references remain candidates. Do not infer identity, ownership, permission, or definitive character likeness from a drawing.

If a page is unreadable, identify it and offer replace/remove. To continue with readable pages, require an explicit choice and carry the omitted-page note into the report.

If no factual claims are found, show “No factual questions identified for this task.” Production planning and creative actions remain available. A bare California reference should appear as story-setting context or a question needing specificity, not automatically as “Not enough evidence.” Do not substitute demo findings.

Editing confirmed text creates a new version and invalidates dependent findings/proposals. Make that consequence visible near the save action.

The user corrects the canonical scene, not two competing versions of the same text in independent scene and claim editors. Regenerate derived claims from that confirmed version. Lock controls refer to the current text occurrence, not a stale checkbox value captured before correction.

## 5A. Shoot options

### Producer inputs

Collect base city/country, shoot window, reporting currency, optional budget ceiling, traveling/local crew and cast, preparation/shoot/travel days, accommodation nights, and hard creative constraints. Explain which unknowns prevent location selection, affordability assessment, or full totals. Never infer production base from a fictional setting. Preserve inputs through errors, mode switches, and refresh after saving.

Confirm the alternative travel region/country before research. Allow domestic or international travel within the two-jurisdiction limit. For VFX, request shot count/duration, camera movement and effect complexity, practical plate/set needs, and revision allowance. Unknown rates/quotes remain empty with “Quote needed”; do not populate plausible-looking prices from model prose.

Primary action: **Compare three options**. Busy copy: **Researching shoot options…** with actual operation status or an indeterminate indicator. Cost-only changes use **Recalculate costs** and do not imply a new web search.

### Comparison cards and evidence

Use fixed cards: **Nearby practical location**, **Alternative travel location**, **Local filming + VFX**. Each shows the candidate/method, scene requirements it meets, creative compromises, cost range or known-cost subtotal, constraint failures, quote gaps, availability status, and a next action. A slot with no supported candidate reads “Insufficient information” or “Does not meet your constraints.” Do not invent a location or force a recommendation.

Keep the source scene and fantasy rules accessible while comparing. Expand **Evidence and assumptions** to show the relevant question, passage, link, retrieval date, applicability, and limitations. A destination's existence is not permission to film there. A directory listing is labeled a lead with availability unconfirmed.

Use plain explanation: “Travel costs increased because the traveling crew changed from [old] to [new].” Values come from saved calculations. Overlapping ranges read “Costs overlap under these assumptions.” Incomplete options cannot receive a confident cheapest/savings badge. No arbitrary creative-fit percentage.

### Editable costs and conditional incentives

Show cost lines with category, quantity/unit, low/high rate, currency/conversion date, and provenance: published rate, supplier quote, your estimate, or unknown. Expose tax/overtime inclusions where known. Sum in code on the server; show subtotal, contingency, total/coverage, and missing categories separately. Do not total the three mutually exclusive options together.

Display costs **Before incentives** by default. A separate **Conditional incentive scenario** shows official sources, eligibility conditions, qualifying-spend assumptions, unresolved questions, and potential value only when calculable. Unknown conditions read “Not calculated — eligibility information needed.” Do not imply a rebate is confirmed or available to fund the shoot.

Editing quantities/rates creates a new comparison revision on recalculation. Changed jurisdiction, dates, or scene requirements mark affected sources/estimates stale and require refresh. Show the previous comparison as history and the new change summary; do not lose an accepted scene edit if comparison research fails.

### Decision and status

Primary decision: **Select for further planning**, with optional producer rationale. Confirm persistence before showing selected. This action creates no booking, supplier message, or tax application.

Keep calculation status (complete estimate, incomplete estimate, stale), evidence gaps, and availability separate. “Complete estimate” means every modeled category has a value/assumption; it is not supplier confirmation. Export incomplete estimates with visible limitations. A stale comparison cannot be presented as current.

## 6. Scene review: optional writing and evidence

Provide **Elaborate this scene**, **Improve action/dialogue**, and **Research a specific detail**. Writing actions are enabled once a scene exists; they do not depend on a CONTRADICTED or MIXED finding. Proposed creative text is labeled as a suggestion and follows preview/accept/reject and lock validation. Preserve author-provided fantasy rules. Full-story generation is outside this submission.

### Queue and status

Order findings by work needed: contradictions and mixed evidence; unresolved questions; human-review routing; supported claims. Display not-researched findings in a separate visible group with the reason.

Each finding row has:

- A plain-language claim or candidate reference.
- Page/scene/panel location.
- Research status in text and an icon.
- A concise reason.
- Optional independent human-review badge.
- Revision/recheck state if relevant.

Do not remove a finding merely because the user clicked an acceptance or review button. Supported, dismissed, removed, and human-reviewed are different conditions.

### Evidence panel

The active finding shows:

1. Exact claim and relevant scene context.
2. The question researched.
3. Research status and plain-language explanation.
4. Source passages, their relation to the claim, publisher/title, retrieval time, and open-source link.
5. Any evidence conflict, applicability limitation, or unknown source independence.
6. Policy/review routing in a secondary expander.
7. An action appropriate to the evidence.

Show contradicting evidence prominently. If a passage only gives context, label it **Context only**. Source count alone never creates a “Verified” badge.

Use the source URLs supplied by the backend. Escape content; allow only validated http/https links; use safe external-link attributes. Do not construct citations client-side.

### Primary actions

- **Propose a small revision** when evidence supports a concrete correction.
- **Refine the question** when context is ambiguous and remaining research budget permits.
- **Mark for human review** when evidence or rights questions need a person.
- **Keep as written** sends a server request that persists a user decision with optional notes; it does not change the factual assessment. Show “Recorded” only after that request succeeds.

Show an explanation when a factual correction is unavailable: “We need applicable evidence before proposing a factual correction.” This must not disable the separate creative-writing actions.

An unresolved card must answer "Evidence for what?" Show the specific question, missing context/evidence, and next action. For an unidentified prop/crest, ask for identifying context or record human review; do not treat an entity-existence source as proof of period suitability or permission. A kept item reads **Kept by reviewer — research unresolved** when appropriate, with the saved note and time. Keeping it never turns its research badge green.

## 7. Status language shared with the backend

| Backend status | UI label | Meaning |
| --- | --- | --- |
| SUPPORTED | Supported by retrieved evidence | Meets the configured research policy; no unresolved material contradiction |
| CONTRADICTED | Evidence challenges this detail | An applicable passage conflicts with the claim |
| MIXED | Sources disagree | The conflict is unresolved |
| UNRESOLVED | Not enough evidence | Missing context or adequate evidence |
| NOT_RESEARCHED | Not researched | Scope or run limit prevented research |
| STALE | Recheck needed | Finding belongs to a previous scene version |

Human routing uses separate labels: **Human review requested** or **Escalated for review**. If no external workflow exists, make clear that this records a note; it does not send a message.

Revision labels: **Proposed**, **Accepted**, **Rejected**, **Recheck pending**, **Recheck complete**, **Recheck failed**. “Complete” means the recheck operation finished; it does not mean all findings are supported.

Legacy reports: display **Legacy policy result: CLEAR** with “Based on source count; not reverified.” Never turn legacy CLEAR into a green SUPPORTED badge.

Avoid: “100% confidence,” “AI-cleared,” “Safe to publish,” “Rights confirmed,” and “All risks resolved.”

## 8. Revision comparison

Open the proposal in the right-hand work area while keeping source context accessible. Allow an expanded comparison on smaller displays.

Show:

- **Original** text and **Proposed** text.
- A readable word-level diff; additions and deletions also have non-color cues.
- **Why this change** with evidence references.
- **Protected text** with backend validation results.
- **Creative constraints to review** for semantic requests.
- **Art changes still needed**, separate from applied text changes.
- Base scene version.
- Proposal kind: creative edit or factual correction. A creative proposal can have no source citations; do not invent evidence for dialogue. A factual correction must expose its applicable passage.

Primary action: **Accept text revision**.

Secondary action: **Reject proposal**.

Rejecting retains the scene and records the decision. Editing a proposal manually creates a new proposal requiring validation; do not let a client-side edit bypass evidence/lock checks.

For an exact-lock conflict, show the conflicting span and require the user to explicitly change the lock or request another proposal. Never silently unlock text.

A stale proposal receives: “This scene changed after the proposal was created. Review a new proposal for the current version.” Do not offer acceptance against an obsolete version.

After acceptance, show **Scene v2 saved. Recheck needed.** Start the separate recheck operation once acceptance succeeds. If the browser loses the response, recover the operation before retrying.

Mark existing production comparisons stale after a scene edit. Refresh confirmed production requirements and any affected cost assumptions before presenting those comparisons as current. Keep the user's previous comparison and choice in history.

## 9. Recheck behavior

Recheck is about the revised scene, not a higher source-count score.

Show the accepted text while the backend re-extracts every claim in the changed scene and evaluates retained, modified, added, and removed claims. Re-searching only the old item list does not count as a recheck. A compact comparison reports:

| Change category | Display |
| --- | --- |
| Retained claim | Current finding and whether evidence was reused |
| Modified claim | Before/after research status and evidence basis |
| Added claim | New finding and research result |
| Removed claim | Removed in revision; do not mark verified |
| Pending art change | Text note accepted; visual correction not verified |

Use specific completion copy: “Rechecked scene v2. One detail now supported; one question remains unresolved,” with counts computed from the returned data.

If recheck fails, preserve the accepted version and offer **Retry recheck**. Keep previous evidence available as history with a stale label. Export remains available, clearly marked **Recheck incomplete**.

If an instruction concerns a visual change, the original image preview must retain a visible “Original artwork” label. A changed caption in a text panel must never look like the image itself was edited.

## 10. Handoff and export

Page title for comparisons: **Production planning brief**. Legacy scene-only outputs retain their scene-research labels.

Lead with the deliverable:

- Selected approach and producer rationale, with the alternatives and why they remain less suitable or uncertain.
- Comparison revision, before-incentive cost ranges/coverage, rate assumptions, conditional incentives, unconfirmed availability, and next work/quotes needed.
- Current confirmed scene text, including any separately accepted revisions.
- Scene/project title, source version, export time, and instruction.
- Accepted changes with original/proposed text, user decision, and evidence.
- Page/panel-specific art instructions that remain to be applied.
- Unresolved, mixed, stale, and not-researched findings.
- Human review notes.
- Source index with URLs and retrieved times.
- Actual run mode and policy version in a compact footer.
- Exact expiry time and a reminder that downloaded files are outside the application's lifecycle.

Actions: **Download scene text**, **Print / Save PDF**, **Download production brief (JSON)**. Legacy scene-only reports may retain **Download research JSON**. These are the final product outputs. Do not add film/video generation controls for this submission; the required hackathon video is a recording of this workflow functioning.

The JSON download uses a sanitized handoff schema, not the internal run object. It includes complete original and accepted scene text, versions, instruction, protected spans, decisions, pending art notes, unresolved work, recheck lineage, sources, and evidence references as `{origin_run_id, source_id}`. It excludes `owner`, cookies/session IDs, and internal authorization context. Keep raw audit hashes behind a technical expander or in a separately labeled internal diagnostic export.

A scene-research report without an accepted revision is labeled **Research draft**. One with a failed recheck is labeled **Accepted revision — recheck incomplete**. These labels describe the optional scene-review component; an unchanged scene can produce a production planning brief.

The incomplete label also applies when recheck is absent, pending, stale, or for a different scene version. Use the backend's validated label and coverage, not a client test for whether a revisions array is nonempty. A completed operation with unresolved questions is distinct from all claims being supported; disclose skipped or failed research explicitly.

For the production brief, display Complete estimate, Incomplete estimate, or Stale comparison separately from scene review/recheck status (including Not requested). Do not imply factual verification or confirmed costs because an approach was selected. Both components must reference the same scene version when combined.

### One preview, three matching downloads

Fetch the version-bound handoff snapshot defined in sol.md section 9 before displaying this screen. For production comparison use the comparison-handoff endpoint; existing scene reports retain their route. Render accepted text, comparison, assumptions, changes, sources, decisions, and status. TXT carries the scene and snapshot/version identification; print/PDF and JSON carry the complete planning brief. All derive from the same snapshot; do not require budget tables inside screenplay TXT.

Each accepted factual correction shows its supporting passage and full citation, not just an S-number or a generic rationale. Creative edits show their rationale, proposal kind, and user decision without fabricated citations. Include source title, full URL, origin run, retrieval time, decision time, and relevant limitations in print where applicable. Project title, version, instruction, run mode, and unresolved work must not disappear through `noprint` styling. Long passages and URLs must wrap without clipping.

If snapshot validation fails, show the specific blocker and retry action. Allow an explicitly labeled scene-text draft if available, but do not offer a misleading validated Production handoff. An older snapshot stays marked as history after further edits. Reloading or exporting must enforce session ownership and the fixed expiry.

Print layout must preserve readable quotes, page numbers, version, source references, and unresolved work. Hide navigation and interactive controls. Expand required evidence in print even if it was collapsed on screen. Include text equivalents for all essential image annotations.

Do not put authorization self-tests or large agent diagrams ahead of the revised scene. Raw audit history belongs in the structured export or Execution view.

Make the selected production approach and its basis the Handoff focus. Show current scene/comparison versions, estimated costs and coverage, next actions, and any separately accepted creative/factual changes with their review status. Keep **Simulated example** visible throughout every example run and in all its exports.

## 11. Execution: verifiable supporting detail

This secondary view answers “What actually ran?” for technical judges and debugging.

Show actual operations: extraction, planning, search, evidence assessment, revision, acceptance, and recheck. Each row identifies component type, status, actual time when captured, tool/provider, and result/error.

Include production-question research, deterministic cost calculation/recalculation, comparison persistence, and producer selection. A recalculation without a provider call is labeled a calculation, not an agent research operation.

Label component types accurately: **Gemini call**, **ADK research agent**, **Deterministic policy**, **User action**. Do not attribute deterministic batch grouping to a planner model that never executed.

An initialization-only agent belongs under **Configured components**, not completed operations. A health endpoint proves availability, not execution.

Separate:

- **Research activity:** Actual Parallel query, request/operation ID, returned source count, bounded follow-up reason.
- **Access controls:** Actual authorization events.
- **Configuration:** Deployed or declared IAM settings with verification status.
- **Self-tests:** The deliberate unapproved-tool denial, labeled and excluded from incident counts.
- **Audit:** Sequence/events and server-computed chain consistency status.

Use **Chain consistency verified**. Explain its limited meaning in an expander. No “tamper-proof” or “immutable audit” claim.

If timestamps or token counts were not captured, show “Not recorded.” Do not synthesize stage times from a single generated_at value or estimate cost without a documented pricing basis.

## 12. Live, recorded, simulated, and failed runs

Persisted per-stage execution metadata is the authority. Class names, /health, or a user's requested mode alone cannot prove live success.

| Mode | Visible treatment |
| --- | --- |
| Live completed | “Processed live” plus actual completion time; Execution shows provider calls |
| Live processing | Actual operation name or a truthful generic busy state |
| Recorded real example | Persistent “Recorded example” label and original run time/provenance |
| Simulated fixture | Persistent “Simulated example” label; no live badge |
| Legacy hybrid result | Stage-level mode labels and limitations |
| Live provider failure | Explain the failed operation; never switch to mock output |

“Try an example” must reveal whether it opens a recorded/simulated result or analyzes an example source live. A fresh live example is allowed only if actual calls occur.

Never replace the user's material with Midnight Signal or any fixture on empty input, extraction failure, missing credentials, or network failure.

## 13. Loading, failure, and recovery

The initial implementation uses bounded requests, not a streaming backend.

- Use an indeterminate spinner and clear operation label.
- Display elapsed time if measured by the client, labeled as elapsed waiting time.
- Do not show timed fake stage transitions or percentages.
- Prevent duplicate submissions while an operation is pending.
- Use server operation IDs and idempotency keys to recover uncertain outcomes.
- A Stop waiting button, if added, must not claim to cancel server processing.
- Keep text, instruction, selected source, and confirmed version intact after errors.

| Condition | User-facing outcome |
| --- | --- |
| No material | Inline instruction; submission disabled |
| Unsupported/oversized file | Name the file and limit; retain valid pages |
| Unreadable page | Replace/remove or explicitly continue with remaining pages |
| No claims extracted | Review transcription or change material; no clean bill of health |
| Provider unavailable | “Research could not finish”; preserve draft, offer retry |
| No relevant sources | UNRESOLVED with query and search scope |
| Conflicting passages | MIXED with both passages visible |
| Run budget exhausted | NOT_RESEARCHED with reason |
| Version conflict | Refresh current scene and create a new proposal |
| Recheck failed | Accepted version retained; prior findings marked stale |
| Expired/deleted material | Clear explanation and New scene action |
| Report failure | Retain run and offer export retry |
| Missing price or exchange rate | Incomplete estimate with the exact missing line; never substitute zero |
| Candidate availability unknown | Lead found; confirmation needed |
| Incentive conditions unknown | Not calculated; show missing eligibility information |
| Changed scene or production dates | Comparison stale; retain history and refresh affected requirements/sources |
| No eligible option | Explain constraint failures and allow editing the brief; do not fabricate a winner |

In-progress image uploads require visible per-file feedback. Never show a thumbnail as safely stored before the server has acknowledged it.

## 14. Visual direction

Use a light production binder with clear typography, a dark-ink header if useful, and generous space around the source material. Let the artwork carry visual interest.

Suggested tokens; verify contrast in the actual implementation:

~~~css
--paper: #f5f2eb;
--surface: #ffffff;
--ink: #202a35;
--muted: #56616d;
--line: #d4d8dc;
--accent: #245b78;
--supported: #256345;
--contradicted: #a32832;
--mixed: #80530c;
--unresolved: #675080;
~~~

Use system sans-serif for controls and evidence reading. Use Courier New or an existing reliable screenplay font for scene text. Existing external fonts may remain only with robust system fallbacks; visual layout must work without font downloads.

Use restrained status labels and fine borders. Avoid celebratory green clearance stamps, oversized metric tiles, decorative agent avatars, fake terminal output, and attention-grabbing security-denial cards.

Default body size: about 16 px; evidence passages at least 15 px on desktop. Keep long prose to a readable line length. Prioritize clear source passages over metadata density.

Only animate transitions that help orientation, such as selecting a panel. Respect reduced-motion preferences. Do not add stock artwork or AI-generated hero art to substitute for the user's material.

## 15. Responsive behavior and accessibility

- Wide screens: source and investigation side by side.
- Medium screens: reduce chrome and allow collapsing the source preview.
- Narrow screens: stack source, selected finding, evidence, and revision; retain a clear “Back to source” control.
- Comparison stacks Original above Proposed when columns become too narrow.
- No horizontal scrolling for core text/forms at a 375 px viewport.
- All actions, source selection, page reordering, and locks work by keyboard.
- Use semantic form labels and headings, visible focus, and useful error associations.
- Move focus to newly opened comparison/dialog content and return it on close.
- Announce operation completion/errors in a restrained aria-live region.
- Never rely solely on color, hover, or pointer-precise image regions.
- Provide text navigation to every page/panel reference.
- Verify zoom at 200%, long titles, long URLs, and keyboard access to print/export.

A diagram or annotation only helps if its information is also available in readable text.

## 16. Frontend/backend mapping

The target routes and data models are defined in sol.md section 9. They require backend implementation.

| UI action | Contract | Render from response |
| --- | --- | --- |
| Read my scene | POST /scenes | Scene/assets, editable extraction, version, operation ID |
| Save correction/intent/locks | PATCH /scenes/{scene_id} | Confirmed canonical version and constraints |
| Confirm and research | POST /runs | Actual mode, findings, sources, run status |
| Open/recover run | GET /run/{run_id} | Authoritative run and recheck history |
| Propose a small revision | POST /runs/{run_id}/revisions | Structured diff, evidence IDs, validated constraints |
| Accept/reject | POST /revisions/{revision_id}/decision | Recorded decision, accepted version if applicable |
| Elaborate/rewrite scene | POST /scenes/{scene_id}/creative-proposals | Creative proposal with base version, protected-text checks, and explicit acceptance |
| Compare/recalculate | POST /scenes/{scene_id}/shoot-comparisons | Saved assumptions, three options, cost lines, coverage, sources, parent ID, actual operations |
| Recover comparison | GET /shoot-comparisons/{comparison_id} | Authoritative saved comparison and limitations |
| Select for further planning | POST /shoot-comparisons/{comparison_id}/decision | Persisted option choice, rationale, and time |
| Open comparison handoff | GET /shoot-comparisons/{comparison_id}/handoff | Shared snapshot of current scene, selected comparison, assumptions, evidence, and outstanding work |
| Recheck accepted scene | POST /scenes/{scene_id}/recheck | Claim lineage, new/current findings, completion/error |
| Preview stored page | GET /scenes/{scene_id}/assets/{asset_id} | Session-authorized asset |
| Recover uncertain operation | GET /operations/{operation_id} | Persisted result or current/error status |
| Open/export handoff | GET /report/{run_id} | Exact accepted version, evidence, remaining work |
| Delete material | DELETE /scenes/{scene_id} | Confirmed deletion/access removal under retention policy |

Minimal frontend state: active scene/version/run, source mode, unsaved draft, selected page/finding, pending operation, proposal, recheck, and authoritative provider metadata.

Add task, confirmed requirements, producer input draft, active comparison/parent ID, selected option, cost edits, and handoff snapshot. Never treat unsaved client arithmetic as an authoritative recommendation or export.

Do not implement verdicts, lock validation, policy evaluation, or version acceptance in client-only code. Derive summary counts from authoritative findings rather than maintaining a second optimistic status model.

On `410 Gone`, replace the workspace with: **“This scene expired after 24 hours and is no longer available in StudioClear.”** Offer **Analyze a new scene**. Do not allow further edits, decisions, rechecks, or exports. A locally downloaded handoff remains the user's responsibility.

## 17. Build order

1. Replace the silent historical-research fallback with task selection and confirmed scene understanding. Verify remaining source/version/recheck defects through regression tests.
2. Connect the producer brief and one complete three-option comparison with real research and deterministic arithmetic.
3. Add editable assumptions, comparison revisions, clear unknowns, and persisted selection.
4. Bind current scene and comparison to one planning-brief snapshot and consistent downloads.
5. Retain optional creative/factual review and source context; show dependency invalidation after edits.
6. Test unfamiliar-user completion, changed constraints, provider failures, refresh, privacy/expiry, narrow/keyboard layouts, and print.
7. Record the working producer decision with actual runtime evidence; leave self-tests/hash rows secondary.

Integrate the backend evidence fixes first. Do not put new trust labels on old source-count conclusions.

## 18. Acceptance walkthrough and video

Use one selected scene from the gold-stone premise and producer-supplied filming inputs. LAST LIGHT and Signal Room remain evidence/revision regression cases. Do not substitute a historical date correction for the primary comparison test.

- [ ] A new visitor finds upload/paste and understands the output immediately.
- [ ] The gold-touching power is retained as fantasy; generic California links do not count as a filming comparison.
- [ ] The user selects one scene and confirms its production requirements without losing the full original source.
- [ ] Optional scene/action/dialogue writing works without a factual contradiction and requires acceptance before changing text.
- [ ] Three approach slots show supported candidates or explicit insufficiency, with editable rate/quantity assumptions.
- [ ] Changing traveling crew size or days recalculates relevant costs and explains the difference without forcing a ranking change.
- [ ] Missing costs/conversions remain incomplete; overlapping ranges and conditional incentives do not yield unsupported savings claims.
- [ ] Crew/location availability remains unconfirmed without dated confirmation.
- [ ] Selection persists as a planning decision; no booking or outreach occurs.
- [ ] A production brief works without an accepted text revision, and its scene-review status is separately visible.
- [ ] Actual uploaded pixels are read; extracted content can be corrected.
- [ ] The instruction changes the research or revision behavior.
- [ ] A finding links to the correct page/panel or explicitly page-level location.
- [ ] The evidence passage supports or challenges the exact claim shown.
- [ ] A proposed correction includes a meaningful before/after diff.
- [ ] Protected text stays unchanged and conflicts are surfaced.
- [ ] Acceptance changes canonical scene text and creates a new version.
- [ ] Recheck covers changed/new claims; removed claims are not called verified.
- [ ] Pending artwork changes remain visibly pending.
- [ ] An unresolved item stays unresolved without a forced success state.
- [ ] Export matches the accepted version and includes citations and remaining work.
- [ ] JSON export contains the full handoff and excludes owner/session/access-control fields.
- [ ] Evidence retained across recheck is identified by origin run and source ID.
- [ ] Every evidence tuple resolves to an included source record, including earlier-run accepted-change evidence.
- [ ] A claim added only to canonical scene text appears in recheck coverage; zero extraction calls cannot pass this gate.
- [ ] Missing or version-mismatched recheck cannot display a completed current handoff.
- [ ] Preview, TXT, PDF, and JSON share one handoff ID and scene version; a later edit cannot mix new text with old findings.
- [ ] Complete non-claim dialogue survives comic extraction; original artwork remains accessible and labeled unchanged.
- [ ] “Keep as written” appears recorded only after server persistence.
- [ ] The exact expiry is visible; access returns an expired state at 24 hours; edits do not extend it.
- [ ] Execution shows actual calls, self-tests, and configuration distinctly.
- [ ] Provider failure preserves user material and never loads fixture results.
- [ ] Source assets cannot be opened from an unrelated session.
- [ ] Keyboard, narrow-screen, and print workflows remain usable.

The current three-minute beat sheet is in sol.md section 14: scene requirements; three options and their evidence; changed producer constraint; selection; production brief and runtime proof. [demo_scene_video.md](demo_scene_video.md) expands it into the live acceptance test and keeps LAST LIGHT as a separate revision regression.

Retain screenshots or a recording from the implemented build. Mark this checklist only after verification. Documentation, static mockups, and initialized agents are not evidence that the workflow works.
