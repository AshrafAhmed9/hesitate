# PRD — Hesitate

Mandatory submission deliverable (PLAN.md section 23: "PRD should explain the problem, target users, solution, and key product requirements").

## Problem

A clinic front-desk voice agent answers administrative questions — fasting duration, arrival time,
coverage, required documents, cost, appointment windows. When policy changes (a stale document
still in the retrieval index, a superseded instruction sheet), a standard RAG agent can retrieve
and repeat the wrong figure with full confidence, because retrieval grounds the model's *input*,
not its *output*. Nothing stops the model from asserting a number the current policy contradicts.

## Target users

- **Primary:** the clinic's front-desk coordinator, whose day includes 60+ repetitive calls about
  the same eleven administrative questions, and who is accountable when a patient arrives having
  gotten the wrong instruction.
- **Secondary:** the clinic operator or voice-agent implementer deciding whether to trust an
  agent with unsupervised administrative answers.

**Validation status:** hypothesis, not yet confirmed with a real coordinator or operator. Per
PLAN.md section 1, real conversations with clinic staff are called for in parallel with the build;
none have occurred at the time of this document. This PRD does not claim customer validation it
does not have.

## Solution

Every factual clause in the agent's outgoing sentence is checked against a curated, versioned,
structured policy record **before** it reaches text-to-speech. Four possible outcomes per claim,
matching PLAN.md section 4's decision table exactly:

| Outcome | What happens |
|---|---|
| Supported | The sentence is spoken as generated |
| Contradicted | The sentence is corrected using a template populated only from the current policy record's own value — never the model's wrong number |
| Unverifiable | The agent declines: "I can't confirm that from this clinic's policy. Please check with the front desk." |
| Conflict | Multiple equally-applicable current records disagree with no supersession between them — same decline, because picking one by similarity is exactly the failure mode this product exists to prevent |

## Key product requirements (from PLAN.md, in priority order for the vertical slice)

1. No candidate sentence bypasses the verification gate (structural guarantee — section 4).
2. Corrections are built solely from validated policy records, never from unchecked model output
   or from re-prompting the LLM (section 4).
3. Supersession is explicit — never "latest upload" or highest retrieval similarity (section 4).
   An unresolved conflict between equally-applicable current records is its own outcome, distinct
   from "no evidence found."
4. Every claim family originally scoped (fasting duration, arrival offset, coverage, required
   documents, cost, appointment windows) is covered by the typed route; nonnumeric/untyped claims
   route to a genuine local entailment model, not a similarity threshold (section 10).
5. The gate's own latency is measured, not asserted (section 5) — currently typed-route p50/p95
   sub-millisecond, semantic-route warm p50 ~7ms model-only, in-process, on real benchmark cases
   defined in `bench/`.

## What this PRD does not claim

No customer interviews have happened yet. No deployed link exists yet. No end-to-end voice call has
been run. No claim in this document is a substitute for the evidence still required by
`COMPETITION.md`'s ledger — that ledger, not this PRD, is the source of truth for what is proven.
