# PLAN.md — Hesitate

**Project:** Hesitate — a clinic voice agent that verifies every factual claim before it is spoken.
**Competition:** YC Fall 2026 × Moss: The Zero Latency Builder Sprint.
**Builder:** Ashraf, solo.
**Status of this document:** authoritative. Any agent working on this repo reads this file first and
does not deviate from it without written amendment here.

---

## 0. How to use this document

- Sections 1–4 are context and must not be changed by an agent.
- Sections 5–12 are executable tasks with acceptance criteria. A task is done only when its
  acceptance criteria are met and verified by running something, not by reading code.
- Section 13 is the list of things that must NOT be built. Adding anything on that list requires
  Ashraf's written approval recorded in `COMPETITION.md`.
- When a task is blocked, record the blocker in `COMPETITION.md` and move to the next independent
  task. Do not silently substitute scope.
- Never invent a measured number. Any figure in the README, video, or PRD must come from a script
  in `bench/` that can be re-run.

---

## 1. Context

Moss (YC F25) is a Rust/WASM semantic search runtime that runs in-process: P50 ~3ms versus ~430ms
for hosted vector databases. Moss's own documentation ships finished cookbooks for a voice support
agent, an airline agent, a candidate screener, a mortgage agent, a travel planner, and an FAQ
agent. Most of the 119 registrants will submit a variation on one of those, where Moss makes an
existing thing faster.

This project takes the opposite position: build the thing that **cannot exist at 400ms retrieval**,
so the Speed criterion is proven by the product working at all rather than by a benchmark
screenshot.

## 2. Confirmed competition facts

| Fact | Value |
|---|---|
| Submission deadline | Sep 20, 2026, 11:59 PM IST |
| Finalists announced | Sep 23, 2026 |
| Grand Finale | Sep 26, 2026, OJone, Bengaluru (Ashraf attending) |
| Team size | Solo or 2; building solo |
| Mandatory | Moss in the retrieval layer; own work |
| Deliverables | GitHub repo with setup instructions, deployed link to working agent, architecture diagram showing retrieval flow, PRD, demo video |

**Judging weights — these drive every prioritisation decision in this document:**

| Criterion | Weight |
|---|---|
| Product & User Experience | **35%** |
| Technical Execution | 30% |
| Speed & Latency | 20% |
| Demo & Presentation | 15% |

Product & UX is the largest criterion and outweighs Technical Execution. Craft is scored. When
technical depth competes with an interface a clinic manager could read unaided, the interface wins.

**Prize buckets — all must be entered:**

| Bucket | Requirement | Action |
|---|---|---|
| ₹50,000 cash, top 5 | The submission | Primary |
| ₹5,000, Top 10 Social Media Builders | Public build-in-public posts during the sprint | Start day 1; cannot be earned retroactively |
| ₹3,000, Top 20 Referrers | Referrals | Costs minutes; do it day 1 |
| Swag, credits, books, certificates | Qualifying submission | Automatic |

**Base rate:** 119 registrants; expect 15–35 genuine submissions; 5 cash prizes. Honest estimate
with this plan executed well: ~50–65% Top 10, ~25–35% in the money, ~10–15% first. If the Product
& UX work (Task 5) is skipped or rushed, subtract roughly ten points from each.

## 3. The product

A live voice agent for outpatient clinic intake. As the LLM streams its reply, each sentence is
intercepted **before it reaches TTS**. Check-worthy claims are verified against the clinic's source
documents via Moss. Unsupported claims are suppressed mid-stream; the agent corrects itself aloud
or declines to assert. The patient never hears the wrong number.

**Persona (use this exact framing in the PRD):** a front-desk coordinator at a multi-site
outpatient clinic, whose day is 60+ calls asking the same eleven questions about insurance
eligibility, fasting instructions, and what to bring — where one wrong answer means a patient
arrives having eaten before a fasting blood draw and the appointment is wasted.

**Gallery headline:**

> Your clinic's voice agent is about to tell a patient to fast for 12 hours. It's 8. We catch it in
> 31ms — before the patient hears a sound.

**The headline number** (fill in real figures from `bench/` after Task 8; never invent):

> **188 of 200 planted errors caught before the patient heard them, in 31ms — with no measurable
> change to how the conversation feels.**

The three-part shape is deliberate: *caught* answers Product, *31ms* answers Speed, *no change to
how it feels* pre-empts the only hostile question that matters.

**Hard constraint:** only public, synthetic, or self-authored patient-facing documents. No real
patient data, ever. State this explicitly in the README.

## 4. Architecture

```
Caller ──▶ LiveKit room ──▶ STT ──▶ LLM (streaming)
                                      │
                                      ▼
                            ┌─────────────────────┐
                            │  Verification gate  │
                            │  sentence buffer    │
                            │  claim extraction   │
                            │  Moss × N parallel  │  ~3ms each, in-process
                            │  tiered support test│
                            └─────────┬───────────┘
                             pass ────┴──── fail
                               │              │
                               ▼              ▼
                              TTS      suppress + correct/hedge
                                              │
                                              ▼
                                      grounded restatement ──▶ TTS

Moss grounding index: clinic policy corpus, client.load_index() once at call start
Moss session index:   live transcript, session.add_docs() per turn, embedded locally
```

**Stack (fixed, do not substitute):** Python LiveKit Agents worker deployed on Render or Fly;
Next.js dashboard deployed on Vercel; Moss Python SDK (`pip install moss`). Follow
`docs.moss.dev/docs/build/live-call-context.md` for the dual-index pattern and
`docs.moss.dev/docs/integrations/livekit.md` for the agent wiring. Reuse those patterns; the only
novel code is the verification gate.

**Repo layout:**

```
/agent          LiveKit worker, the verification gate
/agent/gate     claim extraction, tier logic, support tests
/web            Next.js dashboard
/corpus         clinic documents + provenance list
/bench          benchmark, calibration sweep, ablation — every published number originates here
/docs           PRD, architecture diagram, technical report
COMPETITION.md  tracker
PLAN.md         this file
```

---

## 5. Tasks

Each task states acceptance criteria. A task is not done until they are verified by execution.

### Task 1 — Day 1: tracker, admin, and de-risking

1. Create `COMPETITION.md` from the competition skill's template, populated with Section 2 of this
   file: headline, base rate, criteria weights, prize buckets, claims table, freeze date Sep 17.
2. Create the project `CLAUDE.md` containing exactly:

   ```markdown
   ## Competition
   This project is a judged submission. Read `COMPETITION.md` and `PLAN.md` before doing anything
   else — they hold the rubric, the prize buckets, the claims and their proofs, and the freeze
   checklist. Keep `COMPETITION.md` current.
   ```
3. Enter the social-media pool: post the first build-in-public update. Enter the referral pool.
4. Create a Moss account. Read `docs.moss.dev/docs/pricing.md` and record the free-tier quota in
   `COMPETITION.md` alongside projected judging traffic. If the quota cannot support a public
   judged demo, plan the constrained-demo path from Task 6 now rather than later.
5. Ask the organisers whether more than one submission per participant is permitted. Record the
   answer.
6. Spend 20 minutes on why previous HiDevs hackathon winners won. Record the traits in
   `COMPETITION.md`; compare against them again at freeze.

**Acceptance:** `COMPETITION.md` and `CLAUDE.md` exist and are populated. Both prize pools entered.
Moss quota recorded as a number.

### Task 2 — Day 2: voice loop and the latency budget

1. Build the LiveKit voice loop end to end with no verification: STT → LLM → TTS, with Moss
   `load_index` for grounding and `client.session(call_id)` for the live transcript.
2. **Measure the latency budget.** Instrument the exact interval between "sentence text is
   complete" and "TTS begins producing audio." Record p50/p95 in `COMPETITION.md`.

**Acceptance:** a real call can be held with the agent. The measured pre-TTS slack is written down
as a number. If slack is under 50ms, note in `COMPETITION.md` that the gate must overlap TTS warmup
and design Task 3 accordingly.

**Hard cutoff:** if the voice pipeline is not working by end of day 2, switch to the fallback in
Section 12.1 and do not spend day 3 on infrastructure.

### Task 3 — Day 3: the verification gate, Tier 1

This is the make-or-break task. Read Section 6 in full before writing code.

**Acceptance:** on a live call, a sentence containing a numeric claim contradicted by the corpus is
suppressed before audio is produced, reproducibly, and the contradiction is logged with the
claim slot, the source passage, and per-stage timings.

### Task 4 — Day 4: correction behaviour, corpus, deploy

1. Implement the three outcomes: **supported** → speak; **contradicted** → suppress, then speak a
   grounded restatement; **unverifiable** → suppress, then hedge ("I don't want to guess — let me
   check that with the front desk").
2. Ingest the real corpus into `/corpus` with a provenance list. Include the planted stale
   document described in Section 8.
3. Deploy both halves publicly. The deployed link is a mandatory deliverable and must not slip.

**Acceptance:** the public URL works from a phone on mobile data, not only from the dev machine.
All three outcomes reachable on a live call.

### Task 5 — Day 5: design day (the 35% criterion)

This is a design task, not a wiring task. It gets the full day.

Build the dashboard: the live call view, the per-turn verification trace with per-stage timings,
the end-of-call unverified-claims report, and the empty, loading, failure, and degraded states.

**Acceptance:** a person who is not an engineer can watch the screen during a live call and
correctly describe what the system just did, without narration. Test this on an actual person. If
they cannot, the task is not done.

### Task 6 — Day 6: the proof suite

Parallelisable. See Section 11 for what may and may not be parallelised.

1. **200-claim benchmark** across multiple clinic corpora, expected verdicts declared in the file
   *before* the run. Publish the confusion matrix.
2. **Calibration sweep**: precision and recall against the hybrid `alpha` and the support cutoff.
   Publish the curve and state where the operating point sits and why.
3. **Unnecessary-hedge rate**, measured and published next to precision and recall.
4. **Multi-backend ablation**: identical code path against Moss, Pinecone, Chroma, pgvector, and a
   naive in-memory baseline. Publish p50/p95/p99 and total turn time for each.
5. **Cross-domain generalisation**: run the unmodified gate against a lending or insurance corpus.
   Publish the result whether it holds or degrades.
6. **Failure taxonomy** from real runs: unsupported-numeric, stale-policy, entity swap,
   overconfident hedge, compound claim with one true half. State which are caught and which are not.
7. Run the adversarial-review skill against the working build from the Competition Judge and
   Production Failure perspectives. Fix what it finds before freeze.

**Acceptance:** every number that will appear in the README, PRD, or video is produced by a script
in `bench/` that can be re-run from a clean checkout.

### Task 7 — Day 7: FREEZE

No new functionality after this day. Record the freeze in `COMPETITION.md`. Remaining days are
proof, artifacts, and rehearsal only.

### Task 8 — Day 8: submission artifacts

Video, PRD, architecture diagram, README, repo setup instructions. See Sections 9 and 10.

**Acceptance:** all five mandatory deliverables exist. Every claim in Section 10's table is visible
in the video or description, not only in the repo.

### Task 9 — Day 9: freeze checklist and submit

Run the competition skill's freeze checklist, items 0–17, in full, with a real written answer per
item in `COMPETITION.md`. An item that cannot be satisfied is recorded as an accepted risk, never
dropped. Re-count the field and record the crowding decision. Then submit.

Sep 20 is buffer. It is not workspace.

### Task 10 — Sep 21–25, only if shortlisted

Three or four timed pitch run-throughs delivered aloud, standing, the last two to a real person.
Prepare the three hostile questions from Section 7. Test the offline fallback demo.

---

## 6. The verification algorithm

**The trap:** retrieval similarity does not tell you a claim is supported. A passage about fasting
scores high whether it says 8 hours or 12. Ranking by hybrid score and thresholding would approve
the hallucination, because the retrieved chunk is topically perfect and factually contradictory.
**Any design that treats "high score = grounded" is wrong.** The gate compares values, not scores.

### Three tiers, evaluated in order, first match wins

**Tier 1 — typed slot comparison. Deterministic, target ~5ms. The headline path.**

Define a claim schema for the domain: `fasting_duration`, `arrival_offset`, `coverage_status`,
`required_document`, `cost_amount`, `appointment_window`. Extract typed slots from the outgoing
sentence using regex plus a light NER pass — no model call. Query Moss for candidate passages, then
run the *same* extractor over each retrieved passage. Compare slot to slot:

| Condition | Verdict |
|---|---|
| Same attribute, same value | supported |
| Same attribute, different value | **contradicted** — the demoable case |
| Attribute absent from all retrieved passages | fall through to Tier 3 |

**Tier 2 — local entailment for untyped claims. Target ~15–25ms.**

"You'll get a confirmation email" has no slot. A small cross-encoder or NLI model running locally
scores entailment between the sentence and the top Moss passages. Must stay strictly off the Tier 1
path so the fast case stays fast. Measure its precision and recall separately.

**Tier 3 — unverifiable, so hedge.**

Nothing retrieved addresses the claim; the agent does not assert it. This is the refusal behaviour
and it is a feature, but it has a cost: hedge too often and the agent is useless in a clinic.
Measure the unnecessary-hedge rate and publish it. A verifier that refuses everything scores
perfectly on catching errors and would be thrown out in a day — say this out loud in the video.

### Calibration

The operating point is a values call, not a search problem. For clinic intake, accept false
positives (an unnecessary "let me check") and refuse false negatives (a wrong fasting window spoken
aloud, and a wasted appointment). State this asymmetry explicitly.

---

## 7. Hostile questions — prepare exact answers

**"Isn't this just RAG with extra steps?"** RAG grounds the **input**. This verifies the
**output**. They fail differently: a model handed perfect context still produces unsupported
numbers, because retrieval is a suggestion to the generator, not a constraint on it. Standard RAG
has no step that can say no. Every clinic FAQ agent in this hackathon is RAG, and most will
hallucinate on camera if pushed.

**"So you made your agent slower."** Give the measured delta from Task 2 and Task 6. If the gate
costs ~40ms on a ~700ms turn and overlaps TTS warmup, that is a winning answer. If the honest
number is 300ms, fix the architecture before freeze — better to learn that on day 6 than on stage.

**"What's your false-positive rate and what does it cost the patient?"** Give the measured
unnecessary-hedge rate, then the asymmetry argument from Section 6.

---

## 8. Demo determinism — the failure mode where the demo breaks by succeeding

LLMs hallucinate nondeterministically. Run the live demo and the model may simply be right that
time, leaving no catch to show — a silent failure with no error message.

**Engineer the provocation:** plant a genuinely stale document in `/corpus` (an outdated prep sheet
saying 12 hours alongside the current 8), so the model reliably retrieves and repeats the wrong
figure. This is not cheating — it is the real scenario, and it is the adversarial corpus.

**Verify reproducibility across 20 consecutive runs before recording or presenting.** Automate this
check in `bench/`.

Also plant genuine contradictions *between* source documents (prep sheet versus confirmation email
disagreeing on the fasting window) and show that the system refuses rather than picks. Almost
nobody tests retrieval against a self-contradicting corpus.

---

## 9. The story — video, PRD, and pitch all run this arc

**1. The cost, in one human sentence.** Not a market-size slide. *"A patient fasted for twelve
hours because a voice agent told them to. It was eight. They took the morning off work, arrived
having drunk water at hour nine, and the draw was cancelled. The agent was confident. It was wrong.
Nobody found out until the patient was already in the waiting room."*

**2. Why every existing fix fails.** Post-call evals find it tomorrow. A supervisor LLM costs 400ms
and the conversation falls apart. Prompt engineering reduces it and never removes it. The industry
accepts that you cannot check a claim inside a conversational turn, so it checks afterwards — which
is the same as not checking.

**3. The unlock, named precisely.** Retrieval moved in-process and dropped to 3ms. Not a little
faster — a different category. Show the catch. Let the silence land.

**4. What it means if this is normal.** Every voice agent in healthcare, lending, and insurance
ships with the same accepted risk: it will occasionally say something confidently wrong to someone
who trusts it. This says agents should be structurally incapable of asserting what they cannot
support.

Open the video on beat 1. No logo, no title card, no "hi, I'm Ashraf and today I'll be showing
you." The first spoken words are the story.

**Fixed first 90 seconds:**

| Time | Content |
|---|---|
| 0:00–0:10 | The number, spoken, over the audible catch-and-correct |
| 0:10–0:40 | One full live turn with the verification trace ticking beside it |
| 0:40–1:00 | The refusal, and the unverified-claims report |
| 1:00–1:20 | The ablation: same code, hosted vector DB, turn time collapses, feature dies |
| 1:20–1:30 | Second corpus, unmodified, proving it is a system |

**Prior art — state this honestly in the README, do not claim to be first.** Real-time voice
guardrails exist as closed enterprise products (Modulate, Replicant's supervisor LLMs, Giga,
Hamming). All use the supervisor-LLM or post-hoc pattern. The narrow, defensible claim: **open,
sub-turn, pre-speech, with no second model on the critical path.**

---

## 10. Claims and their proof

Every claim needs proof a judge sees in the video or description. Assume the judge spends minutes
and never opens the repo.

| Claim | Proof | Where a judge sees it |
|---|---|---|
| Catches wrong claims before audio | 200-claim benchmark, verdicts pre-declared, real corpus | First 30s of video; line 1 of description |
| Verification costs < 60ms p95 | Per-stage timing trace rendered live in the dashboard | On screen while the agent talks |
| Only possible because of Moss | Multi-backend ablation, published side by side | Dedicated 20s video segment |
| Stays usable while strict | Unnecessary-hedge rate next to precision/recall | One line in video, one chart in README |
| Knows its limits | Refusal case plus per-call unverified-claims report | Shown, not described |
| Is a system, not a demo | Same gate, unmodified, on a second corpus | Two clips in the video |

**Publish mistakes.** When the verifier produces a false positive during tuning, put it in the
README with the test that caught it and the fix. Nearly nobody does this and it reads as rigor.

---

## 11. Parallel agents — scope and limits

The deadline is hard; "no time limit" is not available. Parallel agents buy throughput on
independent, verifiable work. They do not change what decides this competition.

**Parallelise these:** benchmark construction and runs, the multi-backend ablation, corpus
collection and provenance, the calibration sweep, Tier 2 entailment with its own evaluation, the
cross-domain run, and the written technical report.

**Do not parallelise these — they stay Ashraf's:** the design work in Task 5 (judged by eye, and
more agents produce more interface, not better interface); the calibration operating point (a
values call about patients); integration debugging (unsupervised agents make it worse); and his own
understanding, because he answers for the threshold on stage on Sep 26.

**The specific risk of extra capacity:** volume that reads as machine-generated. The rules require
the work to be his own, and a judge who opens a sprawling repo of unexplained abstractions marks it
down. **Every expansion must be measurement, evidence, or documentation — never new product
surface.** Section 13 does not relax because throughput went up; it gets stricter.

---

## 12. Contingencies — pre-agreed, with dates

**12.1 — Voice pipeline not working by end of day 2.** Drop to a browser chat agent whose replies
stream to TTS and play aloud. The premise survives completely: the claim is still verified before
it is spoken, the catch is still audible, the demo still works. Only telephony realism is lost, and
no criterion scores it. Do not spend day 3 on infrastructure.

**12.2 — Tier 1 not working by end of day 3.** Narrow the claim schema to numeric and date slots
only: fasting duration, arrival time, cost, appointment window. That subset carries the entire demo
and most of the real value, because numbers are what hurt patients. Tier 2 is cut without regret.

**12.3 — Deployed agent fragile or expensive.** Ship a deployed link that opens a scripted,
rate-limited demo session rather than an open-ended agent, with a status banner that explains what
happened if a limit is hit rather than failing blank. A judge who reaches a working constrained
demo scores it; a judge who reaches a quota error scores nothing. Never let the public link be the
thing that breaks.

**12.4 — Live finale, venue wifi fails.** Local-only demo mode: Moss index cached on disk, recorded
STT transcript replayed, and a pre-rendered video on the laptop as last resort. Rehearse the
failure, not just the demo.

---

## 13. Explicitly not building

Pre-cut. Re-adding any of these requires Ashraf's written approval recorded in `COMPETITION.md`:

multi-tenant auth · user accounts · settings or config UI · pluggable LLM or TTS backends ·
telephony/PSTN · a second sponsor integration for its own sake · Docker or devcontainer polish ·
tests beyond the verification gate and the benchmark · analytics beyond the live trace.

**Rule:** if a feature does not make the catch-and-correct moment more provable, it is out.

---

## 14. Verification

- `pytest` over the 200-claim benchmark with pre-declared expected verdicts. It must fail loudly
  when the support threshold is wrong.
- Timing assertions in CI: verification p95 under budget, measured rather than asserted in prose.
- The 20-run demo reproducibility check from Section 8, automated.
- Manual: place a real call to the deployed URL from a phone on mobile data and walk the whole flow
  — grounded answer, caught hallucination, refusal — before recording anything.
- Freeze checklist items 0–17, in full, on day 9, with a real written answer per item.

---

## 15. First action

Create `COMPETITION.md` and the project `CLAUDE.md` per Task 1, before any code.
