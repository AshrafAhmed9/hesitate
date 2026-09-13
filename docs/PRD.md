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
5. The gate's own latency is measured, not asserted (section 5) — typed-route p50/p95
   sub-millisecond, semantic-route warm p50 ~7ms model-only, in-process, on real benchmark cases
   defined in `bench/`. In the one live end-to-end run, the gate resolved a real Moss + real Groq
   turn in 9.76ms.

## What's proven since this PRD was first written (updated 2026-09-13)

- **Deployed and live:** https://hesitate-api.onrender.com
- **The core premise is proven true against the real sponsor service:** real Moss retrieval,
  queried against a real project, ranks a stale policy document above the current one for the
  natural patient question (confirmed twice, live) — exactly the failure this product exists to
  catch, not a constructed scenario.
- **The full loop has run live, once, end to end:** real Moss retrieval → real Groq LLM → the gate
  → a real correction, all real, nothing mocked (`tests/test_end_to_end_live.py`).
- **A real production bug was found and fixed live:** a factual claim phrased as a vague range
  ("fast for 8-12 hours") produced zero typed claims and silently passed as supported. A
  completeness check now catches this class of gap.
- **Reusability is demonstrated, not asserted:** the identical gate runs unmodified inside a second,
  non-voice text agent (`examples/text_chat_agent.py`).

## What this PRD still does not claim

**No customer interviews have happened yet** — still the single largest unvalidated assumption in
this document. **No real human has joined a live call via browser and microphone and spoken to the
agent** — the voice pipeline's individual pieces (LiveKit connection, Deepgram STT, silero VAD) are
each confirmed live and working, but a real end-to-end voice turn has not been observed; a gap was
found in a synthetic-audio test script (not the production path) and is tracked in
`COMPETITION.md`, unresolved. No claim in this document substitutes for the evidence in
`COMPETITION.md`'s ledger — that ledger, not this PRD, is the source of truth for what is proven.
