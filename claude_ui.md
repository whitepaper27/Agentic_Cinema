# claude_ui.md — StudioClear UI, built to feel like a real product

Companion to: `SOL.md` (frozen product / execution plan)  
Frontend: `app/frontend/index.html`  
Status: **FINAL UI BUILD SPEC**  
Purpose: define the frontend experience for a real, user-driven StudioClear product — not a canned demo.

---

# 0. Product experience we are building

StudioClear is not a static demo that only replays `Midnight Signal`.

The real product flow is:

```text
USER UPLOAD
    ↓
OPTIONAL RESEARCH INSTRUCTION
    ↓
STUDIO POLICY
    ↓
GOOGLE ADK AGENTS
    ↓
PARALLEL RESEARCH
    ↓
SOURCE-BACKED FINDINGS
    ↓
POLICY TRIAGE
    ↓
HUMAN DECISION
    ↓
TRACEABLE REPORT
```

The deterministic demo fixture still exists, but only as a **judge-safe fallback**.

The product must prove:

> **The judge can upload their own script, give StudioClear a research focus, and watch the same real pipeline run on new input.**

---

# 1. UI principles

The UI should feel like enterprise studio software that could be used Monday morning.

It must not feel like:

```text
a black AI dashboard
a hackathon control panel
a scripted demo
a chatbot
a table with hidden backend complexity
```

It should feel like:

```text
professional
light
calm
production-ready
evidence-driven
human-controlled
enterprise-governed
```

The default user story is:

> **Upload a script. Tell StudioClear what to focus on. Review what the agents found. Make the decision.**

---

# 2. Visual identity

## 2.1 Palette

Use a professional light enterprise visual system.

```text
Background       #F7F8FA
Surface          #FFFFFF
Primary text     #18212F
Secondary text   #667085
Border           #E4E7EC
Primary accent   #2457C5 or similarly restrained enterprise blue

CLEAR             #2F7A4F
REVIEW            #A8780A
ESCALATE          #B23A2E
INSUFFICIENT      #6B5B95

ALLOW             #2F7A4F
DENY              #B23A2E
RUNNING           #2457C5
```

Color is used for state, not decoration.

## 2.2 Type

```text
UI / reading      system sans-serif
Script excerpts   Courier / monospace
IDs / trace IDs   monospace
```

No external font dependency required.

## 2.3 Avoid

```text
✕ neon
✕ glowing nodes
✕ particle backgrounds
✕ agent avatars
✕ excessive cards
✕ giant metrics wall
✕ fake terminal animation
✕ fake "AI thinking"
```

---

# 3. Entry / enterprise trust screen

The first screen establishes that this is real studio software.

```text
┌──────────────────────────────────────────────────────────────┐
│ StudioClear                                      Google Cloud│
│                                                              │
│              Script clearance intelligence                   │
│                                                              │
│  Upload a production script.                                 │
│  Let agents research what needs attention.                   │
│  Keep final decisions with the studio.                       │
│                                                              │
│                [ Continue with Google ]                       │
│                                                              │
│                         or                                   │
│                                                              │
│                [ Open Demo Workspace ]                        │
│                                                              │
│      Governed agents · source-backed evidence · audit        │
└──────────────────────────────────────────────────────────────┘
```

Important:

- Judges must never be blocked by authentication.
- `Open Demo Workspace` must work without provisioning.
- If real login exists, use it.
- If login is not fully implemented, do not fake enterprise authentication.

---

# 4. Enterprise workspace shell

After entry:

```text
┌──────────────────────────────────────────────────────────────────────┐
│ StudioClear        Demo Studio ▾                Search      User ▾   │
├──────────────────┬───────────────────────────────────────────────────┤
│                  │                                                   │
│ + New clearance  │                                                   │
│                  │                                                   │
│ Projects         │                                                   │
│ Runs             │                                                   │
│ Reports          │                                                   │
│                  │                                                   │
│ Evidence         │                                                   │
│ Agents           │                                                   │
│                  │                                                   │
│ Governance       │                                                   │
│  Policy          │                                                   │
│  Access & roles  │                                                   │
│  Audit           │                                                   │
│                  │                                                   │
└──────────────────┴───────────────────────────────────────────────────┘
```

Left navigation is persistent.

Do not create empty pages just to look enterprise.

Only show sections with real data.

---

# 5. New Clearance — default screen

This is the single most important change from the prior UI.

The product starts from **real user input**, not from a fixed demo.

```text
New clearance


1  Upload production material

┌───────────────────────────────────────────────────────┐
│                                                       │
│             Drop your screenplay here                 │
│                                                       │
│                   PDF · TXT                           │
│                                                       │
│                  [ Browse files ]                     │
└───────────────────────────────────────────────────────┘


2  Research instructions (optional)

┌───────────────────────────────────────────────────────┐
│ Focus on factual claims, living people, brands,      │
│ historical references, and medical statements.       │
└───────────────────────────────────────────────────────┘


3  Studio policy

[ Production Standard v1 ▾ ]


                [ Start research ]


──────────────────── or ────────────────────

             [ Try Midnight Signal ]
```

This screen proves StudioClear is not hard-coded.

---

# 6. Research instruction examples

The prompt does **not** rewrite the script.

It changes the research focus.

Examples:

```text
"Check every scientific claim."

"Focus on brands and living people."

"Verify historical references with at least two sources."

"Find all medical claims that need producer review."

"Research every real-world location."

"Prioritize references that could require human/legal review."
```

The prompt should influence the ADK Planner.

Example:

```text
USER INSTRUCTION

"Focus on scientific and medical claims."

        ↓

ADK PLANNER

Batch A
Scientific claims      6

Batch B
Medical claims         3

Batch C
People / brands        lower priority
```

The run plan should visibly differ when the instruction differs.

---

# 7. Supported input scope

For the hackathon P0:

```text
PDF screenplay
TXT script
```

Only show additional formats if the backend actually supports them.

Do not advertise:

```text
comic
storyboard
image
FDX
DOCX
```

unless those paths really work end to end.

---

# 8. Main project navigation

Once the run starts:

```text
Decision desk
Run
Report
```

No fourth tab.

No settings tab.

No architecture tab.

Technical details live in `Run`.

---

# 9. Decision Desk — default project view

This is where the producer works.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ StudioClear                                          Midnight Signal · v1    │
│ Script clearance research desk                      Run 009 · completed      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Analyzer ✓ 14 items   Planner ✓ 3 batches   Parallel ✓ 28 sources           │
│ Policy ✓ 14 evaluated   Authorization · 1 denied   Waiting on you: 5         │
│                                                                              │
├───────────────────────────────────────────────┬──────────────────────────────┤
│ Items needing your decision                   │                              │
│                                               │ CLR-009                      │
│ CLR-009  Historical claim      REVIEW         │ Historical claim             │
│ CLR-011  Living person         ESCALATE       │ Scene 6                      │
│ CLR-003  Song reference        REVIEW         │                              │
│ CLR-014  Medical claim         INSUFFICIENT   │ Script context               │
│ CLR-007  Brand reference       REVIEW         │ "..."                        │
│                                               │                              │
│ Clear to continue (9)                    ▸    │ Recommendation               │
│                                               │ REVIEW                       │
│                                               │                              │
│                                               │ Policy basis                 │
│                                               │ historical_claim             │
│                                               │ minimum_sources = 2          │
│                                               │                              │
│                                               │ Parallel evidence            │
│                                               │ 3 sources                    │
│                                               │                              │
│                                               │ Your decision                │
│                                               │ [Clear to continue]          │
│                                               │ [Send to legal]              │
│                                               │ [Override recommendation]    │
└───────────────────────────────────────────────┴──────────────────────────────┘
```

Rules:

- Sort by **needs human decision** first.
- Collapse already-clear items.
- Selecting a row updates the right pane.
- No modal required.
- `Waiting on you: N` is prominent.
- Every visible count comes from real run data.

---

# 10. Evidence pane — hero technical proof

This is the strongest product surface.

For every item show, in this order:

## 10.1 Script context

```text
Scene 6

"..."
```

## 10.2 Agent recommendation

```text
REVIEW
```

Plus:

```text
policy rule
plain-English action
```

Example:

```text
historical_claim
→ verify with at least 2 independent sources
```

## 10.3 Parallel evidence

```text
via Parallel Search
Batch C

Source 1
Title
Excerpt
Domain
Retrieved 14:01:22
[Open source]

Source 2
...
```

No fabricated URL.

No source appears unless it exists in backend data.

## 10.4 Human decision

```text
[ Clear to continue ]
[ Send to legal ]
[ Override recommendation ]
```

Override requires a reason before submission.

After action:

```text
Recorded
audit #051
14:07:12
```

---

# 11. Copy rules

Use human language.

Preferred:

```text
Clear to continue
Send to legal
Needs review
Not enough evidence
Try again
Retry research
```

Avoid:

```text
Approve
Legal
Legally cleared
Safe from liability
AI approved
```

The system recommends.

The human decides.

---

# 12. Run view — real AI working

This is the technical judge view.

Two columns:

```text
Execution
Authority
```

Example:

```text
┌──────────────────────────────────────┬─────────────────────────────────────────┐
│ Execution                            │ Authority                               │
│                                      │                                         │
│ Upload                    ✓ 14:00:41 │ Acting as                               │
│   │                                  │ producer_123 → run_009 → researcher    │
│ Analyzer                  ✓ 14:00:58 │                                         │
│   14 items · Gemini                  │ Effective access                         │
│   │                                  │ user ∩ script ∩ agent ∩ tool ∩ IAM     │
│ Planner                   ✓ 14:01:03 │                                         │
│   ├ Batch A brands        4 items    │ Researcher may                          │
│   ├ Batch B people        5 items    │ ✓ parallel.search.public_web            │
│   └ Batch C facts         5 items    │ ✓ evidence.write                        │
│   │                                  │ ✕ final_legal_clearance                 │
│ Authorization                       │ ✕ iam.modify                            │
│   ✓ Parallel            ALLOW       │                                         │
│   ✕ legal_database      DENY        │ Denied this run                         │
│   │                                  │ unapproved_legal_database.search        │
│ Parallel Search           ✓         │ reason: tool_not_authorized             │
│   3 calls · 28 sources             │                                         │
│   │                                  │ Cloud IAM                               │
│ Reviewer                  ✓         │ service identity                        │
│   9 clear · 3 review · 2 escalate │ ✓ Secret Manager                        │
│   │                                  │ ✕ unrelated project resource           │
│ Human                     ● waiting │                                         │
├──────────────────────────────────────┴─────────────────────────────────────────┤
│ Audit — verified                                                           │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

# 13. Execution trace rules

The execution list must come from real events.

Possible states:

```text
pending
running
done
denied
waiting
error
```

Do not animate ahead of backend state.

For live mode:

```text
poll /run/{run_id}
```

or use an existing stream if implemented.

For completed demo mode:

- replay real stored events;
- label it `Completed demo run`;
- do not pretend it is executing live.

---

# 14. Agent detail inspector

Clicking a run stage may show:

```text
RESEARCHER

Runtime
Google ADK

Model
<actual model>

Input
14 research items

Plan
3 batches

Tool calls
Parallel Search: 3

Sources
28

Authority
✓ parallel.search.public_web
✓ evidence.write
✕ final_legal_clearance
✕ iam.modify
```

Do not show private chain-of-thought.

Show structured operational facts only.

---

# 15. Dynamic planning proof

The run view should make the user's optional research instruction visible.

Example:

```text
Research instruction
"Focus on science and medical claims."

Planner output

Batch A   Science        6
Batch B   Medical        3
Batch C   Other          5
```

This is the proof that the judge's own input changes the run.

---

# 16. Parallel visibility

Parallel must be visually unmistakable.

Show:

```text
Parallel Search

3 research batches
14 items researched
28 source citations
14 / 14 evidence-backed
```

When clicked:

```text
Batch C
Facts / medical

Queries
...

Items
...

Sources
...
```

No provider logo required.

Text is enough.

---

# 17. Governance / authority

StudioClear AuthZ and Cloud IAM must stay separate.

## 17.1 StudioClear AuthZ

```text
Can this user / agent / project use this capability?
```

## 17.2 Cloud IAM

```text
Can the running workload access this Google Cloud resource?
```

Do not combine them into one generic "security" status.

---

# 18. Effective Access

Show the permissions-only-shrink idea.

```text
Effective Access

User
Producer
    ∩
Script
Midnight Signal
    ∩
Agent
Researcher
    ∩
Tool
Parallel Search
    ∩
Cloud IAM
service identity
    ↓

ALLOWED
```

Denied:

```text
Researcher
    ↓
unapproved_legal_database.search
    ↓
Tool Registry
    ✕
    ↓
DENIED
```

---

# 19. Real DENY

The same denied event should appear in:

1. Execution
2. Authority
3. Audit

Example:

```text
DENIED

Agent
researcher

Capability
unapproved_legal_database.search

Reason
tool_not_authorized

Recovery
Planner replanned using Parallel

Audit
#049
```

One real event.

Never invent a second one for visual effect.

---

# 20. Access & roles

If the backend has real permission metadata, show a compact view.

```text
RESEARCHER

✓ script.read
✓ parallel.search
✓ evidence.write

✕ final_clearance
✕ policy.modify
✕ iam.modify
```

For the human:

```text
PRODUCER

✓ upload script
✓ review evidence
✓ clear to continue
✓ send to legal
✓ override with reason

✕ iam.modify
```

If this metadata does not exist, do not hardcode the page.

---

# 21. Audit view

Show a readable event list.

```text
#047 14:00:58  analysis.completed
#048 14:01:03  plan.created
#049 14:01:04  authz.deny
#050 14:01:05  plan.replanned
#051 14:07:12  human.override
```

If hash verification exists:

```text
Audit integrity
✓ verified
```

Raw JSON may be available behind:

```text
[View raw event]
```

but is never the default.

---

# 22. Report view

The report is the final studio deliverable.

```text
SCRIPT CLEARANCE RESEARCH REPORT

Midnight Signal · v1

References detected       14
Evidence-backed           14
Independent citations     28
Clear to continue          9
Review                     3
Escalate                   2
Human decisions            5
Unauthorized calls         1 blocked

--------------------------------------------------

CLR-009
Historical claim
Scene 6

Script
"..."

Recommendation
REVIEW

Policy
historical_claim
minimum_sources = 2

Evidence
Source 1
Source 2
Source 3

Human decision
Clear to continue

Audit
#051
```

Footer:

> **Agents research and recommend. The studio clears.**

---

# 23. Demo fixture

The demo remains:

```text
Try Midnight Signal
```

It uses a tested, real prior run.

Purpose:

```text
reliable judging path
fast initial experience
stable video recording
known evidence
known UI states
```

The demo is not proof of generality.

The **Upload your own** path is proof of generality.

---

# 24. Live vs demo

Make the distinction explicit.

```text
Demo run
Completed from a verified prior execution

Run live
Gemini + ADK + Parallel
```

Never label cached replay as live.

Never animate a replay as though API calls are currently running unless clearly marked `Replay`.

---

# 25. Demo-safe content

For the hosted/video fixture:

```text
real brands only in neutral context
real people only in neutral factual context
no logos
no slogans
fictional entity for negative-context example
```

If a fictional entity has no real-world evidence:

```text
INSUFFICIENT EVIDENCE
→ ESCALATE
```

This is an honesty feature.

---

# 26. Real data contract

Every visible field must map to backend data.

```text
script metadata          run / upload response
user instruction         run.research_instruction
summary counts           report.summary
items                    report.items[]
script context           item.text_span / scene
recommendation           item.recommendation
policy                    item.policy_rule_id + /policy
evidence                  item.evidence[]
batch                     item.batch_id → report.batches[]
agent model               run.agents[].model
execution                 audit.events[]
ALLOW / DENY              authz events
Parallel counts           actual research trace
IAM status                backend IAM check result
human decisions           item.human_decision / audit
report totals             computed from report.items[]
```

If the field does not exist:

```text
hide the UI
```

Do not invent data.

---

# 27. Empty / loading / error states

Examples:

```text
No script loaded.
Upload a PDF or TXT file, or try the demo.

Analyzing your script...

Planning research...

Researching batch B with Parallel...

Parallel search timed out.
[Retry batch]

Not enough evidence.
This item requires human review.

This file type is not supported.
Use PDF or TXT.

Authorization denied.
The agent replanned with an approved tool.
```

---

# 28. Three-minute demo

```text
0:00–0:12
StudioClear enterprise workspace.

0:12–0:25
New Clearance.
Upload script.
Show optional research instruction.

0:25–0:45
Start run.
Analyzer finds items.
Planner creates research batches.

0:45–1:10
Run tab.
Parallel researches live / verified run.
Show source count.

1:10–1:40
Decision Desk.
Open one item.
Show script context + policy + 2–3 real sources.

1:40–1:55
Open a human-only item.
Show ESCALATE.

1:55–2:10
Run tab.
Show real DENY → audit → replan.

2:10–2:35
Back to desk.
Clear one.
Send one to legal.
Override one with reason.

2:35–2:53
Report.
Show every item traceable to:
script → source → policy → human decision.

2:53–3:00
Close.
```

Closing line:

> **Agents research and recommend. The studio clears.**

---

# 29. Build priority

If time is limited:

```text
P0-1  Upload your own script
P0-2  Optional research instruction
P0-3  Start same real pipeline
P0-4  Evidence pane
P0-5  Decision actions
P0-6  Run view
P0-7  DENY + audit
P0-8  Report
P1    enterprise shell polish
P1    Access & roles
P1    agent inspector
P2    richer graph visualization
```

Do not trade P0 reliability for P2 visuals.

---

# 30. Definition of Done

The UI is done when a judge can answer YES:

```text
Can I upload my own script?                                  YES
Can I give StudioClear a research focus?                     YES
Does the run use that input?                                 YES
Do real agents perform the workflow?                         YES
Does Parallel run in the application?                        YES
Can I see real sources and timestamps?                       YES
Can I understand why each item was flagged?                  YES
Can I make the final decision myself?                        YES
Is an unauthorized agent capability visibly denied?         YES
Is that denial audited?                                      YES
Can the workflow continue after denial?                      YES
Can I see a final traceable report?                          YES
Can I also use a reliable demo fixture?                      YES
Does the product feel complete rather than scripted?         YES
```

If all are YES, stop adding UI features.

---

# 31. Final UI promise

StudioClear should make a skeptical judge understand this immediately:

```text
I can bring my own script.
The AI finds what needs investigation.
The agents plan the research.
Parallel provides verifiable evidence.
Policy tells me what needs attention.
The platform limits agent authority.
I make the final decision.
Everything is traceable.
```

Final product line:

> **Upload a script. StudioClear finds what needs investigation, agents research it, Parallel provides traceable evidence, policy tells you what needs attention, and the studio makes the final decision.**
