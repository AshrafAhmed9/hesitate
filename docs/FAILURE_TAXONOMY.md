# Failure taxonomy

PLAN.md section 6 (depth work): "A failure taxonomy from real runs... Say which categories are
caught, which are not, and why." This is compiled from actual failures found during development —
via live LLM output, live NLI model behavior, and live cross-domain testing — not invented for
completeness. Each entry links to where it was found and its current status.

| # | Category | Example | Caught? | Root cause | Status |
|---|---|---|---|---|---|
| 1 | Superseded/stale document repeated as fact | LLM says "fast for 12 hours" from a stale prep sheet Moss ranks *above* the current one | **Yes** | Typed comparison against the resolved (non-superseded) `PolicyRecord`, not the retrieved passage's text | Closed — this is the core mechanism |
| 2 | Wrong numeric value (cost, duration) | "$200" vs the real $150; "30 minutes" vs the real 15 | **Yes** | Same typed comparison | Closed |
| 3 | Wrong polarity on a categorical claim | "your plan does not cover this" when it does | **Yes** | Polarity is a first-class field in the comparison key | Closed |
| 4 | Unresolved conflict between equally-current records | Two active records for the same key disagree, neither supersedes the other | **Yes** | Explicit `CONFLICT` decision distinct from `UNVERIFIABLE` — never picked by similarity | Closed |
| 5 | Vague/range claim with no clean typed value | "fast for 8-12 hours" | **Yes, as of 2026-09-13** | Was silently defaulting to SUPPORTED (zero claims extracted); a completeness heuristic (`agent/gate/completeness.py`) now flags number+unit spans no typed pattern consumed | Closed same day it was found — see `bench/cases.py` regression case |
| 6 | Factual claim with no number in it at all | "you'll get a text message confirmation" | **No** | Neither the typed route nor the completeness heuristic can detect a claim that has no number/unit signature | **Open** — needs the model-assisted decomposition PLAN.md section 10 specifies, which requires an LLM call |
| 7 | Off-topic passage mistaken for contradiction (Tier 2 only) | NLI model scored 89% confident CONTRADICTED between two topically unrelated sentences | **No, in isolation** | Small NLI models can be overconfident on out-of-domain pairs. Mitigated in practice because Moss retrieval should only ever return topically relevant candidates, but that mitigation is unverified end-to-end | **Open**, mitigation unverified |
| 8 | Domain-specific vocabulary gap | "police report" not recognized as a required-document type (insurance domain) | **No** | `_extract_required_document`'s vocabulary is hardcoded from the clinic domain | **Open** — silent zero-claim result, not a crash; found via the cross-domain test |
| 9 | Condition-dependent facts in a new domain | "deductible for collision" vs a generic "$500" claim with no condition | **No** | `extract.py` never resolves `conditions` from sentence text or caller context — always defaults to `()`. Costless in the clinic domain (mostly unconditional facts); costly in insurance (routinely conditional) | **Open** — a pre-existing, now-quantified gap |
| 10 | Voice pipeline: real audio not producing a transcript | Synthetic caller speaks; Deepgram connects; no transcript observed | **N/A — infrastructure, not a gate failure** | Two hypotheses ruled out (byte layout, identity collision); root cause still unknown | **Open**, blocking a full live voice demo |

## What this table is for

Six of ten categories are closed, with the newest (#5) closed same-day. Four remain open, each with
a stated reason rather than a vague "known limitations" disclaimer. This is the honest answer to
"what does it not catch" that PLAN.md section 6 and the demo script's Segment 5 both require.
