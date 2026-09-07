# StudioClear — Final UI and Interaction Specification

**Revised:** September 7, 2026

**Status:** Implementation target; the new workflow is not yet shipped.

**Product/API authority:** [sol.md](sol.md).

**Implementation:** app/frontend/index.html; existing vanilla JavaScript and CSS.

**Current hosted app:** https://studioclear-602811764567.us-central1.run.app/

This replaces the earlier Agent Operations Desk specification and conflicting UI directions in claude_ui.md and the prior scene-revision proposal. Preserve useful existing evidence, policy, decision, and print components. Historical test counts, deployment revisions, and “all data is real” claims are not verification of this design.

## 1. Experience objective

A filmmaker brings a storyboard or scene, directs a research task, inspects evidence, chooses a small revision, and exports the revised text with production notes.

The source material and the creative decision are the visual center. Agent execution and governance are accessible supporting information.

**Five-second comprehension test:** On arrival, a user can tell what to upload, what instruction to give, and what they will receive.

**End-to-end test:** With unfamiliar material, a user can reach an exported, rechecked revision without knowing what ADK, a provider, an audit hash, or a policy engine is.

Opening copy:

> **Make the smallest change your scene needs.**

> Bring a storyboard or paste a scene. Investigate factual details, compare evidence-backed revisions, and keep your creative intent.

Primary action: **Analyze a scene**.

Secondary action: **Try an example**.

Do not promise legal clearance, automatic comic redrawing, guaranteed accuracy, or a finished film.

## 2. Information architecture

Keep four views:

| View | Purpose | Availability |
| --- | --- | --- |
| Analyze a scene | Material, instruction, preview, extraction confirmation | Default entry |
| Scene desk | Findings, evidence, proposal, acceptance, recheck | After confirmed material has a research run |
| Handoff | Accepted scene text, revision notes, evidence, unresolved work, export | Once a run exists; label incomplete rechecks |
| Execution | Actual operations, provider modes, tool events, errors, policy, audit | Secondary navigation for the active run |

Use a compact project header: StudioClear, editable title, scene version, and actual run status. “New scene” starts a separate workspace; do not discard unsaved material without a clear discard action.

The user-requested analysis tab is the front door. “Analyze a scene” reflects both pasted scripts and comic pages; do not hide upload behind a developer/demo menu.

Remove the ADK checkbox from the normal user journey. Runtime routing is an implementation choice and remains visible in Execution.

## 3. Desktop layout

At approximately 1200–1440 px, use a restrained header and a two-column scene workspace. Reserve about 45% for material and 55% for the active investigation. Avoid an additional narrow third column.

~~~text
StudioClear   Project title                     Scene v2   Recheck pending
Analyze a scene       Scene desk       Handoff                 Execution

Instruction: Check historical details. Preserve the joke and ending.
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

## 4. Analyze a scene: input and intent

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

Label: **What should we investigate or preserve?**

Example: “Check historical accuracy. Preserve the characters, joke, and ending.”

Optional suggestion buttons populate an editable instruction: “Check factual details,” “Investigate this reference,” and “Preserve my dialogue.” They must correspond to supported research behavior.

Allow selecting exact transcript/text spans to protect after extraction. Do not claim the app can deterministically preserve a semantic quality such as humor.

### Privacy and action

Before upload, show the configured retention and processing disclosure in plain language. The target policy is session-private material retained for 24 hours, with a delete action; only show that promise once its enforcement and any backup/soft-delete limits match sol.md.

The user should understand that uploaded material is processed with Gemini and research questions are sent to Parallel. Keep credential names and setup instructions out of this flow.

Primary button: **Read my scene**.

Busy label: **Reading your scene…**

On success, continue to Confirm extraction. Reading material does not silently initiate full research before the user checks it.

## 5. Confirm extraction

Show source and extracted content side by side:

- Page thumbnail/preview and page number.
- Candidate panel labels and editable dialogue/captions.
- A separate description of visible action; distinguish transcription from model interpretation.
- Candidate references and factual claims tied to their text/page.
- An option to correct misreads.
- Exact-text lock controls.
- Current instruction, still editable.
- Primary action: **Confirm and research**.

Suggested correction copy: “Check that we read this correctly before researching it.”

Visual references remain candidates. Do not infer identity, ownership, permission, or definitive character likeness from a drawing.

If a page is unreadable, identify it and offer replace/remove. To continue with readable pages, require an explicit choice and carry the omitted-page note into the report.

If no candidate claims are found, show “No researchable claims found in this extraction.” Let the user edit the transcript, clarify the task, or provide another scene. Do not show a clean bill of health or substitute demo findings.

Editing confirmed text creates a new version and invalidates dependent findings/proposals. Make that consequence visible near the save action.

## 6. Scene desk: findings and evidence

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
- **Keep as written** records a user decision with optional notes; it does not change the factual assessment.

Show an explanation when revision is unavailable: “We need applicable evidence before proposing a factual correction.”

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

Primary action: **Accept text revision**.

Secondary action: **Reject proposal**.

Rejecting retains the scene and records the decision. Editing a proposal manually creates a new proposal requiring validation; do not let a client-side edit bypass evidence/lock checks.

For an exact-lock conflict, show the conflicting span and require the user to explicitly change the lock or request another proposal. Never silently unlock text.

A stale proposal receives: “This scene changed after the proposal was created. Review a new proposal for the current version.” Do not offer acceptance against an obsolete version.

After acceptance, show **Scene v2 saved. Recheck needed.** Start the separate recheck operation once acceptance succeeds. If the browser loses the response, recover the operation before retrying.

## 9. Recheck behavior

Recheck is about the revised scene, not a higher source-count score.

Show the accepted text while the backend re-extracts and evaluates the changed scene. A compact comparison reports:

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

Page title: **Production handoff**.

Lead with the deliverable:

- Current accepted scene text.
- Scene/project title, source version, export time, and instruction.
- Accepted changes with original/proposed text, user decision, and evidence.
- Page/panel-specific art instructions that remain to be applied.
- Unresolved, mixed, stale, and not-researched findings.
- Human review notes.
- Source index with URLs and retrieved times.
- Actual run mode and policy version in a compact footer.

Actions: **Download scene text**, **Print / Save PDF**, **Download research JSON**.

A report without an accepted revision is labeled **Research draft**. A report with a failed recheck is labeled **Accepted revision — recheck incomplete**.

Print layout must preserve readable quotes, page numbers, version, source references, and unresolved work. Hide navigation and interactive controls. Expand required evidence in print even if it was collapsed on screen. Include text equivalents for all essential image annotations.

Do not put authorization self-tests or large agent diagrams ahead of the revised scene. Raw audit history belongs in the structured export or Execution view.

## 11. Execution: verifiable supporting detail

This secondary view answers “What actually ran?” for technical judges and debugging.

Show actual operations: extraction, planning, search, evidence assessment, revision, acceptance, and recheck. Each row identifies component type, status, actual time when captured, tool/provider, and result/error.

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
| Recheck accepted scene | POST /scenes/{scene_id}/recheck | Claim lineage, new/current findings, completion/error |
| Preview stored page | GET /scenes/{scene_id}/assets/{asset_id} | Session-authorized asset |
| Recover uncertain operation | GET /operations/{operation_id} | Persisted result or current/error status |
| Open/export handoff | GET /report/{run_id} | Exact accepted version, evidence, remaining work |
| Delete material | DELETE /scenes/{scene_id} | Confirmed deletion/access removal under retention policy |

Minimal frontend state: active scene/version/run, source mode, unsaved draft, selected page/finding, pending operation, proposal, recheck, and authoritative provider metadata.

Do not implement verdicts, lock validation, policy evaluation, or version acceptance in client-only code. Derive summary counts from authoritative findings rather than maintaining a second optimistic status model.

## 17. Build order

1. Add Analyze a scene with working paste/image preview, instruction, and real extraction.
2. Add confirm/correct extraction and exact locks.
3. Connect evidence-aware research to the source-centered Scene desk.
4. Add proposal comparison and server-validated acceptance/rejection.
5. Add changed-scene recheck and before/after claim states.
6. Complete Handoff exports and honest Execution details.
7. Verify loading, failures, private assets, mobile/keyboard behavior, and print.

Integrate the backend evidence fixes first. Do not put new trust labels on old source-count conclusions.

## 18. Acceptance walkthrough and video

Use an original storyboard with a researched factual mismatch and an ambiguous second detail.

- [ ] A new visitor finds upload/paste and understands the output immediately.
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
- [ ] Execution shows actual calls, self-tests, and configuration distinctly.
- [ ] Provider failure preserves user material and never loads fixture results.
- [ ] Source assets cannot be opened from an unrelated session.
- [ ] Keyboard, narrow-screen, and print workflows remain usable.

The three-minute beat sheet is in sol.md section 14: upload and intent; evidence; constrained revision; recheck; export and brief runtime proof.

Retain screenshots or a recording from the implemented build. Mark this checklist only after verification. Documentation, static mockups, and initialized agents are not evidence that the workflow works.
