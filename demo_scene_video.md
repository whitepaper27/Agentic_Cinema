# StudioClear — LAST LIGHT live demo and video test

**Status:** Test script for use only after the workflow repairs below are complete. It is not evidence that the current hosted app works, and it must not be used to label a simulated run as live.

**Demo pack:** [LAST LIGHT README](demo/last-light/README.md), [scene text](demo/last-light/scene.txt), [page prompts](demo/last-light/comic-prompts.md), and private [reviewer notes](demo/last-light/reviewer-notes.md).

**Goal:** Prove one coherent filmmaking workflow: original comic pages are read, a factual issue receives evidence, a filmmaker approves one minimal revision, the changed scene is re-extracted and rechecked, and one version-consistent handoff is exported.

## 1. Do not start recording until these gates pass

- [ ] Three original final comic pages exist as separate PNG/JPEG/WebP files, have no third-party characters/logos, and have documented creation/tool provenance.
- [ ] The live app accepts the pages in order without using the pasted script to conceal a failed image extraction.
- [ ] Full dialogue/captions, page locations, visual descriptions, and candidate claims are retained separately. A claim list is not being used as the transcript.
- [ ] A confirmed canonical scene version is the only source for research, revisions, recheck, screen view, TXT, PDF, and JSON.
- [ ] Research records actual Gemini/Parallel operation outcome, time, query/operation identifier, and provider mode. A live-provider failure remains a failure; it never receives fixture data.
- [ ] The page 2 accepted revision has applicable evidence, cites at least one stored source passage, and has a specific version-bound target.
- [ ] Exact dialogue locks are enforced by the server. A matching phrase elsewhere cannot satisfy a changed protected occurrence.
- [ ] Recheck calls extraction on the accepted scene version, then researches changed and newly added claims or explicitly records a skip/failure.
- [ ] Every accepted-change evidence tuple `{origin_run_id, source_id}` resolves to exactly one source record in the handoff snapshot, including sources from before recheck.
- [ ] A handoff with no recheck, a failed/pending recheck, or a version mismatch is labeled **Accepted revision — recheck incomplete**, never **Production handoff**.
- [ ] Screen, TXT, printable PDF, and JSON come from one server-generated handoff ID and identical scene version.
- [ ] A separate regression test adds a new claim after acceptance and proves it appears in recheck coverage. Do not test this destructive variation during the filmed showcase run.
- [ ] The 24-hour expiry and private-asset behavior have passed their own smoke test.

If any box is unchecked, record the failure for debugging but do not use that run in the submission video.

## 2. Test data and expected boundaries

Use the scene's exact research instruction:

> This is grounded historical fiction set in 1935, not time travel. Check the depicted equipment and factual narration against that setting. Preserve all spoken dialogue exactly. Propose only evidence-backed caption or action-description changes. Do not invent an identity or permission status for the door symbol. Separate pending artwork changes from applied text changes.

Lock all five dialogue lines named in `demo/last-light/README.md` before research.

The prepared test inputs are intentional; they are not verdicts the system may hardcode:

| Material | Desired demonstration | Boundary |
| --- | --- | --- |
| Page 1 compact digital camera with screen in 1935 | A page/panel-linked period concern and a pending art note | Text revision does not alter original comic pixels or establish a replacement prop/rights clearance. |
| Page 2 narration saying 1868 for the first transatlantic cable | Evidence-backed, minimal correction if live evidence supports it | Do not change dialogue or add unsupported historical detail. |
| Page 2 ambiguous door mark | Honest uncertainty/restraint | No inferred real identity, owner, permission, or “cleared” result. |

The likely source leads in `reviewer-notes.md` are only rehearsal leads. The runtime must make its own actual Parallel request and retain the returned passage. If its evidence differs, show the real result rather than forcing this planned result.

## 3. Live acceptance test — run before filming

### A. Start clean

1. Use a fresh browser session. Capture app build/revision, UTC start time, and the source-page file hashes in a local test record.
2. Select **Storyboard / comic pages**. Upload the three pages, verify their previews/order, and enter the instruction above.
3. Click **Read my scene** in live mode. Record the returned scene ID/version and actual mode. Stop if it says simulated, example, mock, missing provider, or has no real provider operation.

**Pass:** Every page is retained and visible, no fixture material appears, and the app shows a recoverable error instead of substituting a demo on failure.

### B. Confirm what the system read

4. Review page by page. Confirm that all five dialogue lines remain in the transcript, even though they are not all research claims.
5. Confirm the setting, electronic camera/screen, page 2 narration, and door mark are described at page/panel level only where the system has reliable location data.
6. Correct any transcription mistake in the canonical scene, then save it. Confirm a new scene version exists and any draft findings/proposals are invalidated.
7. Apply exact dialogue locks to the current version. Confirm lock feedback names the text and version.

**Pass:** The app does not treat a concatenated list of claims as the comic's transcript. The edit/research target and visible source are the same version.

### C. Research and review

8. Click **Confirm and research** in live mode. In Run details, check actual Gemini extraction/assessment and Parallel Search events separately from policy, self-test, and audit rows.
9. Open the camera finding. Read the researched question, visible passage, limitation, and page/panel reference. Record any art correction as pending; do not say artwork changed.
10. Open the page 2 historical narration finding. Verify the full caption/context and the precise returned passage before offering a revision.
11. Open the door-mark finding, if present. Confirm its treatment stays limited to the available context. If no finding is extracted, do not fabricate one for the video.

**Pass:** The user can understand the issue, exact evidence, and uncertainty without reading raw JSON. An authorization self-test is not presented as proof of research execution.

### D. Revision and recheck

12. Request a small revision only for the historical caption. Check that the original target appears exactly once in the current version, evidence references are nonempty/applicable, and the diff changes only the supported date/detail.
13. Accept the revision. Confirm a new scene version and that all five locked dialogue lines are byte-for-byte unchanged.
14. Start recheck. Confirm it first re-extracts the accepted version, then shows retained, modified, added, and removed claim coverage with actual operation results.
15. If recheck fails, retain the accepted scene but stop the showcase run. The correct label is **Accepted revision — recheck incomplete**.

**Pass:** A successful recheck names the accepted scene version and still leaves the camera art note/ambiguous mark honestly unresolved where applicable.

### E. Handoff integrity

16. Open the server-generated handoff. Verify its handoff ID, scene version, run/recheck lineage, accepted caption, locks, pending art note, unresolved work, and exact provider mode.
17. For every accepted-change evidence reference, open the included source record. Verify origin run, source ID, URL, passage, query, and retrieval time resolve correctly.
18. Download TXT, Print/Save PDF, and JSON. Compare handoff ID and scene version across all three. Confirm PDF includes the supporting passage, full citation, original/proposed text, instruction, decisions, pending art work, and unresolved work.
19. Refresh the page and reopen the saved scene/run. Confirm the same version-bound handoff is returned before expiry.

**Pass:** Nothing mixes old findings with newer scene text; no owner/session/access data appears in JSON.

## 4. Separate regression test — never hide this behind the showcase

Run this after the clean demo, in a new test scene or copy:

1. After an accepted revision, append a new factual sentence to canonical scene text through the normal editor.
2. Save the new version and run recheck.
3. Assert the extraction operation is called on that new version.
4. Assert the new claim appears as added and is researched, skipped with reason, or failed with error. A generic **complete** state is not enough.
5. Assert old accepted-change citations remain resolvable in the new handoff.

Record results in an automated regression test and keep a screenshot or JSON artifact. This test addresses the pre-repair defect where zero re-extraction calls still produced a “complete” result.

## 5. Three-minute public video beats

Use a real, previously verified live run. Waiting may be edited only if the footage remains faithful and the displayed result is not substituted. If a clip is a replay, label it **Recorded live run** with original date/provider provenance. Never use the simulated example as the proof run.

| Time | Footage | Say/show |
| --- | --- | --- |
| 0:00–0:20 | Three original LAST LIGHT pages and the instruction | “A production researcher needs to catch factual problems without rewriting the scene’s emotional core.” |
| 0:20–0:50 | Confirm extraction: full dialogue, 1935 context, page locations, locks | “We confirm what Gemini read before research. These dialogue lines are protected.” |
| 0:50–1:30 | Historical caption finding, Parallel source passage, camera art note | “The evidence challenges this caption. The camera remains a pending artwork issue, not a falsely edited image.” |
| 1:30–2:05 | Small diff and acceptance | “The filmmaker chooses one minimal, evidence-backed caption correction. Dialogue stays unchanged.” |
| 2:05–2:30 | Recheck coverage for the new version | “StudioClear reads the revised scene again and reports what was rechecked and what remains unresolved.” |
| 2:30–2:50 | Matching production handoff, PDF/TXT/JSON, source passage | “The handoff keeps the accepted change, evidence, decision, and remaining art work together.” |
| 2:50–3:00 | Brief Run details | “This run records actual Gemini and Parallel operations. Configuration, self-tests, and audit integrity are supporting details.” |

Do not make claims about legal clearance, automatic comic-image editing, generated video, perfect truth, measured cost/time savings, or an assured hackathon win.

## 6. Evidence to keep beside the submission

- Live run/recheck IDs, handoff ID, UTC timestamps, and build commit.
- Original page files and non-sensitive provenance; do not publish private source drafts unless intended.
- Screenshots of full extraction, evidence passage, accepted diff, recheck coverage, and matching exports.
- A short actual-user observation: task, participant role, completion result, duration, and limitation. Do not invent metrics.
- Public repository/runtime proof that Gemini and Parallel Search are imported and actually called in the submitted application.
- Final rules check: hosted URL, public repo/license, original content, English public video at most three minutes, and correct track submission.

Rules reference: https://agentic-cinema.devpost.com/rules
