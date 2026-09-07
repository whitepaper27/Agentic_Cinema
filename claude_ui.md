# claude_ui.md — StudioClear UI, built to be judged

Companion to: `SOL.md` (frozen build contract)
Frontend: `app/frontend/index.html` — one file, no framework, no build step
Status: BUILD SPEC — sized for one day (Sep 7), freeze at end of day
Supersedes: `sol_ui_win.md` where the two disagree

---

## 0. The bet this spec makes

Judges score four equal criteria. A UI can win or lose exactly one of them outright — **Design: "a complete, coherent product experience, not a technical proof of concept."** It can also quietly _lose_ Technological Implementation if anything on screen looks scripted.

So this spec optimizes for two things and nothing else:

1. A producer can finish their job on the default screen without reading anything.
2. Every technical claim on screen is one click from the data that proves it.

The agent graph is not the hero. The evidence is. A judge who clicks CLR-009 and sees three real Parallel sources with real timestamps and a policy rule that explains the verdict has just verified Gemini, Parallel, policy, and traceability in one motion. No graph does that.

---

## 1. Three views, one default

```text
[ Decision desk ]   [ Run ]   [ Report ]
```

- **Decision desk** — default. The producer's work surface.
- **Run** — how the agents did it. Graph, trust, audit. For technical judges.
- **Report** — the deliverable. Printable. This is what "leaves with the script."

No fourth tab. No settings. No login screen.

---

## 2. Decision desk (default screen)

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│ StudioClear                                          Midnight Signal · v1      │
│ Script clearance research desk                       Run 009 · completed 14:02 │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  Analyzer ✓ 14 items   Planner ✓ 3 batches   Parallel ✓ 28 sources             │
│  Policy ✓ 14 evaluated   Authorization · 1 request denied   Waiting on you: 5  │
│                                                                                │
├───────────────────────────────────────────────┬────────────────────────────────┤
│  Items needing your decision (5)              │                                │
│                                               │   CLR-007  Brand reference     │
│  CLR-007  Brand reference   sc.4   REVIEW     │   Scene 4                      │
│  CLR-011  Living person     sc.6   ESCALATE   │                                │
│  CLR-012  Living person     sc.9   ESCALATE   │   ┃ "...she slams the         │
│  CLR-003  Song reference    sc.2   REVIEW     │   ┃  [brand] on the counter   │
│  CLR-014  Medical claim     sc.11  INSUFF.    │   ┃  and says it's worthless" │
│                                               │                                │
│  Cleared to continue (9)                 ▸    │   Recommendation               │
│                                               │   ┌──────────┐                 │
│                                               │   │  REVIEW  │  brand_disp... │
│                                               │   └──────────┘  → human review│
│                                               │                                │
│                                               │   Evidence — 2 sources         │
│                                               │   via Parallel Search, 14:01   │
│                                               │   1  <title>                   │
│                                               │      <excerpt>                 │
│                                               │      example.com  · 14:01:22   │
│                                               │   2  <title>                   │
│                                               │      <excerpt>                 │
│                                               │      example.org  · 14:01:23   │
│                                               │                                │
│                                               │   Your decision                │
│                                               │   [Clear] [Send to legal]      │
│                                               │   [Override recommendation…]   │
│                                               │                                │
└───────────────────────────────────────────────┴────────────────────────────────┘
```

Rules for this screen:

- The list is sorted by **what needs the producer**, not by item ID. Items already CLEAR are collapsed under one row. The producer's queue is the first thing on screen.
- Selecting a row loads the right pane. No modal, no drawer animation. Click, read, decide.
- The status strip (row 3) is the _only_ place the agent pipeline appears on this screen. Each chip is a link into the Run view at that node. It is the entire "this is agentic" argument on the producer's screen, and it is enough.
- "Waiting on you: 5" is the single number that tells a judge this is a human-in-the-loop product, not an autopilot.

### 2.1 The evidence pane is the hero

This pane is where Design and Technological Implementation are both won. It must show, in this order:

1. Script context — the actual text span, quoted, with scene number. Set in the screenplay face.
2. Recommendation — one verdict stamp, plus the policy rule ID that produced it and the rule's action in plain words ("brand disparagement → human review"). Clicking the rule ID opens the policy table filtered to that rule.
3. Evidence — every source: title, excerpt, domain, retrieval time, a real link. Header says _via Parallel Search_ with the batch ID. If evidence is insufficient, say so and show what was searched.
4. Your decision — three actions. "Override recommendation…" requires a reason field before it enables. After any decision the stamp updates and a line appears at the bottom: _Recorded · audit #051 · 14:07:12_.

Nothing on this pane is decorative. If a field has no data, hide it rather than show a dash.

### 2.2 Copy rules

- Buttons say what happens: "Send to legal", not "Escalate"; "Clear to continue", not "Approve".
- The system never says _cleared_, _legal_, _safe_, or _approved_ about itself. Agents _recommend_. Producers _decide_.
- Sentence case everywhere. No tracked-out uppercase labels except the verdict stamps.
- Empty and error states give the next action: "No script loaded. Upload a PDF or load the demo script." / "Parallel search timed out on batch B. Retry batch."

---

## 3. Run view

Two columns. Left: what the agents did. Right: what they were allowed to do.

```text
┌──────────────────────────────────────┬─────────────────────────────────────────┐
│  Execution                           │  Authority                              │
│                                      │                                         │
│  Script upload            ✓  14:00:41│  Acting as                              │
│    │                                 │    producer_123 → run_009 → researcher  │
│  Script analyzer          ✓  14:00:58│                                         │
│    14 items · Gemini <model>         │  Effective access = intersection of     │
│    │                                 │    user · script · agent · tool · IAM   │
│  Research planner         ✓  14:01:03│                                         │
│    ├─ Batch A  brands/orgs   4 items │  Researcher may                         │
│    ├─ Batch B  people/events 5 items │    ✓ parallel.search.public_web         │
│    └─ Batch C  facts/medical 5 items │    ✓ evidence.write                     │
│    │                                 │    ✕ final_legal_clearance              │
│  Authorization gate                  │    ✕ iam.modify                         │
│    ✓ parallel.search    ALLOW        │                                         │
│    ✕ legal_database     DENY 14:01:04│  Denied this run                        │
│    │                                 │    unapproved_legal_database.search     │
│  Parallel Search          ✓  14:01:31│    tool_not_authorized · audit #049     │
│    3 calls · 28 sources · 14/14 items│    Planner replanned → Parallel         │
│    │                                 │                                         │
│  Reviewer / policy        ✓  14:01:38│  Cloud IAM (service identity)           │
│    9 clear · 3 review · 2 escalate   │    studioclear-researcher@…             │
│    │                                 │    ✓ Secret Manager: parallel-api-key   │
│  Human decisions          ● 5 waiting│    ✕ <resource outside project>         │
│                                      │                                         │
├──────────────────────────────────────┴─────────────────────────────────────────┤
│  Audit — 51 events                                              [Show raw JSON]│
│  #049  14:01:04  authz.deny      researcher  unapproved_legal_database.search  │
│  #050  14:01:05  plan.replanned  planner     batch_b → parallel.search         │
│  #051  14:07:12  human.override  producer    CLR-003  reason: "…"              │
└────────────────────────────────────────────────────────────────────────────────┘
```

Rules:

- The execution column is a **vertical list with real timestamps**, not a canvas graph. It is derived entirely from the audit events. It is buildable in two hours and cannot be accused of being scripted. If the full node graph gets built later (P2), it replaces this column; the data is the same.
- Every node line shows the count that proves it ran. Every count comes from the report or audit objects (see §7).
- The DENY appears in the execution column, the authority column, and the audit table — one event, rendered three ways. Do not invent a second denial for effect.
- StudioClear AuthZ and Cloud IAM are separate blocks with separate headings. Never merge them; the distinction is the architectural point.
- The audit table is the source of truth. Raw JSON is one click away, never the default.

### 3.1 Live run vs. replay

Two entry points, clearly labeled:

- **Load demo run** — instant. Shows a completed run 009 from stored data. This is what a judge sees at t+0 when they open the hosted URL. It is real data from a real run; the header says _completed 14:02, Sep 8_.
- **Run live** — kicks off a real pipeline on the demo script with live Parallel calls. The status strip and execution list update by polling `/run/{id}` every 2s. Nodes turn from pending to running to done as events arrive. No fixed cadence. If Parallel takes 20 seconds, the UI waits 20 seconds and says _searching batch B…_.

Never animate ahead of data.

---

## 4. Report view

A single scrolling document, printable to PDF from the browser.

```text
Script clearance research report
Midnight Signal · v1 · run 009 · generated <timestamp>

References detected     14
Evidence-backed         14
Independent citations   28
Clear to continue        9
Review                   3
Escalate                 2
Human decisions          5   (1 override)
Unauthorized tool calls  1 blocked

────────────────────────────────────────────────
CLR-007  Brand reference                     Scene 4
Script:   "…"
Recommendation:  REVIEW  —  brand_disparagement → human review
Evidence:  [1] title · domain · retrieved 14:01:22
           [2] title · domain · retrieved 14:01:23
Decision:  Sent to legal · producer_123 · 14:05:40 · audit #050
────────────────────────────────────────────────
… 13 more
```

Footer: _Agents research and recommend. The studio clears._ — the only place the tagline appears in the product.

Every summary number is computed client-side from `report.items[]`, never typed in.

---

## 5. Visual identity

Ground it in the object this replaces: the clearance binder that sits on a production coordinator's desk — script pages, a rubber verdict stamp, a sources log.

**Palette**

| Role         | Hex       | Note                           |
| ------------ | --------- | ------------------------------ |
| Paper        | `#F3F4F1` | cool archival white, not cream |
| Ink          | `#1C2331` | navy-black for text and rules  |
| Rule         | `#BFC4BD` | dividers, disabled             |
| Clear        | `#2F7A4F` |                                |
| Review       | `#A8780A` |                                |
| Escalate     | `#B23A2E` |                                |
| Insufficient | `#6B5B95` |                                |

Color is reserved for **state**: verdicts, allow/deny, running. Nothing else is colored. A judge's eye lands on stamps and denials because nothing competes.

**Type**

- UI: IBM Plex Sans, 15px base, weights 400/600 only.
- Script excerpts and item IDs: Courier Prime — the screenplay face, used only where the content _is_ screenplay or an ID. Not for labels, not for numbers, not for "cinematic" flavor.

**The one memorable element**

The verdict stamp. Rendered as a bordered rectangle, 1.5px ink-colored border in the verdict color, slight rotation (−1.5°), letterspaced uppercase. It is the only uppercase, the only rotated element, and the only thing on the page that looks like an object. When a producer clicks a decision, the stamp changes — that is the one moment of motion in the product.

**Do not**

- No cards-with-shadows grid. Content is separated by rules and whitespace.
- No page-load fade-ins, no pulsing nodes, no particle backgrounds, no avatars.
- No provider logos anywhere in the UI. Parallel, Gemini, ADK, Cloud IAM appear as text in the status strip and Run view.
- No middle-dot chains in headings. Dots are allowed in metadata lines only (timestamps, domains).

---

## 6. Demo-safe mode

`?demo_safe=1` (also default when hostname is the Cloud Run URL):

- Source domains are shown; page titles and excerpts are shown; no favicons or logos fetched.
- Demo script uses real, neutral, well-sourced entities for facts / locations / organizations, and fictional names for the "negative context" items. Fictional items resolve to INSUFFICIENT EVIDENCE → ESCALATE, which is the honest and correct behavior.
- No item in the demo script portrays a real person or brand negatively. (Rules prohibit disparaging content and third-party trademarks in the video.)

Live Parallel calls are unaffected.

---

## 7. Data contract

Every number on screen maps to a field. If the field doesn't exist, the number doesn't appear.

```text
status strip counts        report.summary.*
items table                report.items[]
script excerpt             item.text_span, item.scene
recommendation + rule      item.recommendation, item.policy_rule_id, policy.rules[id]
evidence                   item.evidence[] (source_url, title, excerpt, retrieved_at)
batch label                item.batch_id → report.batches[]
model name                 run.agents[].model   (never hardcoded)
execution list             audit.events[] filtered by type, ordered by ts
allow / deny               audit.events[] where type in (authz.allow, authz.deny)
IAM block                  run.iam_checks[]      (read-only; add to /run output if missing)
human decisions            item.human_decision + audit.events[] type human.*
report totals              computed from report.items[] in the browser
```

Backend additions permitted before freeze: **only** read-only fields on the existing `/run/{id}` response (`agents[]`, `iam_checks[]`) if they are not already there. No new endpoints. No pipeline changes.

---

## 8. Build order — Sep 7

Single `index.html`, vanilla JS, fetch against the existing API. Hours are estimates for one person.

| #   | What                                                                         | Hours | Done when                            |
| --- | ---------------------------------------------------------------------------- | ----- | ------------------------------------ |
| 1   | Shell: header, three-tab switch, status strip from `report.summary`          | 1.5   | Tabs switch, counts real             |
| 2   | Decision desk: queue table sorted by needs-decision, collapsed cleared group | 1.5   | Click row → pane loads               |
| 3   | Evidence pane: excerpt, stamp, rule, sources with links + times              | 2     | Judge can verify a Parallel source   |
| 4   | Decisions: three actions, override reason gate, audit line on success        | 1.5   | Stamp updates, audit grows           |
| 5   | Run view: execution list from audit, authority column, DENY in 3 places      | 2     | DENY visible with timestamp + reason |
| 6   | Report view + print stylesheet                                               | 1     | Prints to a clean PDF                |
| 7   | Load demo run / Run live with polling                                        | 1     | Cold URL shows data in <2s           |
| 8   | Demo-safe mode, empty/error states, keyboard focus                           | 1     | No dashes, no blank panes            |

**Freeze at end of step 8.** ~11.5 hours. If behind schedule at step 5, cut the authority column to a single DENY card and move on.

**Not built this hackathon:** canvas node graph, capability matrix, trace inspector, replay animation, architecture overlay (put the Mermaid in the README — judges read it there).

---

## 9. Three-minute demo on this UI

```text
0:00–0:15  Decision desk, empty. "Before a studio shoots, someone researches
           every name, brand, claim." Upload Midnight Signal.
0:15–0:40  Status strip fills as the live run progresses. Queue populates.
           "14 items. 5 need me. Parallel found 28 sources."
0:40–1:15  Click CLR-009 (historical claim). Read the excerpt. Show the rule:
           2 sources required. Show 3 sources, click one, it opens.
           "Every verdict shows me why, and where the evidence came from."
1:15–1:35  Click CLR-011 (living person). ESCALATE. "Policy says this is a human
           call. The system never clears it."
1:35–1:55  Run tab. Execution list. Point at the DENY: researcher asked for a
           tool outside its registry, denied, audited, planner replanned to
           Parallel. Authority column: what the agent may and may not do.
1:55–2:30  Back to desk. Clear one. Send one to legal. Override one with a
           reason. Audit count ticks each time.
2:30–2:50  Report tab. Scroll. "14 references, 28 citations, every decision
           traceable to a source, a rule, and a person."
2:50–3:00  "Agents research and recommend. The studio clears."
```

The Run tab gets 20 seconds. The producer's work gets 90. That ratio is the point.

---

## 10. How this scores

| Criterion                    | What the judge sees                                              | Risk if this spec is followed                     |
| ---------------------------- | ---------------------------------------------------------------- | ------------------------------------------------- |
| Technological implementation | Real sources, real timestamps, real DENY, model name from config | Low — nothing is animated ahead of data           |
| Design                       | A producer finishes a real task in one screen; report prints     | Low — this is the criterion the spec is built for |
| Potential impact             | "Waiting on you: 5" and the report make the workflow tangible    | Low                                               |
| Quality of idea              | Unchanged from SOL.md                                            | None added, none lost                             |

The only way this UI loses is if step 3 (evidence pane) is shipped half-done. Protect that step above all others.
