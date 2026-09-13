# Competition tracker

Updated September 13, 2026; event sources rechecked September 13; SDK/pricing evidence retains its stated check date. All implementation and submission checks remain pending. Initial workspace contained only `PLAN.md`, with no source code or Git metadata. This tracker records evidence, not completed work by implication.

## Confirmed competition

Ashraf explicitly confirmed YC Fall 2026 × Moss. The prior attachment mismatch is resolved and is retained only in historical review notes. This is a Moss-only, planning-only task.

Required event alignment is consolidated in PLAN.md Section 23, based on the [official overview](https://yc-fall-2026-x-moss.devpost.com/), [rules](https://yc-fall-2026-x-moss.devpost.com/rules), and [resources](https://yc-fall-2026-x-moss.devpost.com/resources). All runtime, registration, contributor, and submission checks remain pending unless marked otherwise.

## Moss administration

The [official rules](https://yc-fall-2026-x-moss.devpost.com/rules) confirm weights 35/30/20/15 for product/technical/speed/demo; September 23 finalist announcement; September 26 Bengaluru finale. They describe cash across five teams and separate social/referral reward pools. These are pools, not individual award amounts. Attendance, eligibility, registration, and optional-pool participation are unverified for Ashraf.

Use the more explicit 23:59 deadline in the rules rather than relying on the overview's midnight display. The earlier solo-build freeze dates are superseded by the full-depth dependency gates in PLAN.md. Preserve the official deadline; set the release-candidate/rehearsal schedule from actual staffing and progress without automatically deleting scope. The official resources identify the HiDevs event URL in PLAN.md Section 23. Its authenticated form was not inspected; verify its fields and any supplementary Devpost instructions before submission. Optional social/referral activity must not displace the main submission. Drafting public material is allowed; publishing or messaging is not authorized by this review request.

## Cost and integration evidence

**Live accounts confirmed working (Sep 2026), all keys stored in .env, never committed:**
- Moss: project connected, live retrieval confirmed (see Claims ledger).
- LiveKit: project connected, token issuance + authenticated API call confirmed live.
- Deepgram (STT): key verified (HTTP 200 on /v1/projects).
- ElevenLabs (TTS): key verified (HTTP 200 on /v1/user). **Free tier: 10,000 characters/month.**
  At roughly 150 words/minute spoken and ~5-6 characters/word, that's ~15-20 minutes of TTS audio
  TOTAL for the entire remaining build — dev testing, rehearsal, AND the judged demo combined.
  This WILL run out before Sep 26 if not budgeted. Action needed from Ashraf: either upgrade the
  ElevenLabs plan before heavy voice-loop testing starts, or move dev/rehearsal TTS onto a
  free/local alternative and reserve the ElevenLabs quota for the final recorded demo + live
  finale only. Not yet decided — flagging now, before the budget is silently spent on iteration.
- LLM: Groq (`openai/gpt-oss-20b`), key verified live. Ashraf has no OpenAI/Anthropic key; Groq is
  the deliberate substitute, and it works.

**THE full loop ran live for the first time (see `tests/test_end_to_end_live.py`)**: real Moss
retrieval returns the stale prep sheet as top-1 for "how long do I need to fast?" → real Groq LLM
is prompted to state it as fact and does ("You should fast for 12 hours...") → the gate resolves
the claim against the full candidate set in 9.76ms → CONTRADICTED against the current 8-hour
record → deterministic correction produced: "Actually — 8 hours, per your prep instructions." Every
piece of this is real: real sponsor retrieval, real LLM, real gate, real measured timing. This is
the actual demo, not a mockup of it.

**Measured finding**: `gpt-oss-20b` is a reasoning model that silently burns completion tokens on a
hidden reasoning field before producing content — 121 reasoning tokens / 581ms for a one-sentence
reply by default, dropped to 6 reasoning tokens / 361ms with `reasoning_effort: "low"` (now the
default in `agent/llm/groq_client.py`). `"none"` is not a valid value for this model (HTTP 400).
This is exactly the kind of measured-not-invented latency number PLAN.md section 5 requires.


The [Moss pricing page](https://docs.moss.dev/docs/pricing), checked September 12, lists Developer allowance: $5 monthly credits, 500 MB storage, 50 MB monthly ingest, 10 GB monthly egress, 60 voice-minutes monthly, one project, three indexes, and unmetered local queries. Confirm account-specific balances and what voice-minute metering covers before projecting capacity. This does not include LiveKit, STT, LLM, TTS, or hosting allowances. No actual account/quota inspection or spending occurred.

The [Moss LiveKit guide](https://docs.moss.dev/docs/integrations/livekit) documents Python loading/querying and advises SDK 1.9.0+. The [LiveKit node documentation](https://docs.livekit.io/agents/logic/nodes/) documents text processing at `tts_node`. These support a feasibility spike, not a claim that our interception, deployment, or latency already works. The original live-call-context Markdown link failed retrieval during this review; the [Moss documentation index](https://docs.moss.dev/llms.txt) still lists it. Do not treat a fetch error as proof the capability is absent.

Planned budget worksheet: total developer rehearsals + judge sessions × session duration; cost/minute for each provider; startup/hosting costs; available credit; enforced concurrency/duration; fallback behavior. Values pending a real account and deployment check. Budget active/staged/retained policy snapshots and separate session indexes explicitly. Verify quota behavior before claiming the full update/rollback/session workflow fits the account. Persist only consented/redacted records required by the operational workflow.

## Claims ledger

| Intended claim | Required evidence | Current status |
|---|---|---|
| Candidate cannot bypass speech boundary | TTS input tests and end-to-end audio trace including correction and cancellation | Not implemented — no LiveKit/TTS connection exists yet |
| Handles the declared administrative policy forms | Locked held-out outcomes, coverage and failure counts | Partial: 6 typed families implemented and tested (13/13 starter cases, `bench/cases.py` + `bench/run_benchmark.py`); 200-case locked holdout suite not built |
| Resolves current/stale/conflicting policy correctly | Applicability, supersession, full-key conflict tests | **Implemented and tested.** `agent/gate/resolve.py`: explicit supersession chain (`corpus/policy_records.py`), unresolved-conflict detection distinct from missing-evidence. 15/15 pytest incl. `test_contradicted_never_releases_original_text` |
| Moss contributes useful retrieval | Runtime trace and fair local baseline | **Live Moss account connected (project created by Ashraf), real proof measured**: for the exact patient question, real Moss retrieval ranks the STALE 12-hour prep sheet (score 0.99) above the CURRENT 8-hour one (score 0.975) — twice, on two separate runs. This is the product's entire premise, true on the actual sponsor service, not a constructed fixture. Live query round-trip measured at ~2-11ms including real network latency. See `tests/test_live_moss.py` (skips cleanly without credentials) and `agent/retrieval/live_moss.py`. Fair local baseline (Moss vs. alternatives) still not built |
| Remains usable | Correct completion/refusal metrics and observed user test | Not measured |
| Adds acceptable response delay | Paired full-turn timing including buffering | Partial: typed-route gate latency measured at p50=0.008ms p95=0.59ms on 13 cases (`bench/run_benchmark.py`, in-process, no network) — not the full-turn/buffering measurement section 5 requires, and n=13 is far below the 1,000-evaluation target |
| Has plausible customer value | Anonymized stakeholder observation; proxy clearly separated | Not validated |
| Semantic (nonnumeric) claims verified by genuine entailment, not similarity | Measured accuracy + latency of a real NLI model, separate from the typed route | **Model wired and benchmarked standalone**: cross-encoder/nli-deberta-v3-xsmall, 4/4 starter cases, warm p50=6.9ms/p95=8.7ms model-only (`bench/run_semantic_benchmark.py`). One real model limitation found and documented (89% confident false-contradiction on an off-topic pair — see `agent/gate/semantic.py`). **Not yet wired into the sentence-level gate**: needs a decomposition step (LLM call) that requires an API key/account decision |
| Retrieval-to-resolution adapter works, top-k can't hide a conflict | End-to-end test: retrieval surfaces multiple documents, all applicable records get resolved together | **Implemented and tested.** `agent/retrieval/adapter.py` + `agent/retrieval/mock_moss.py` (local embedding stand-in, NOT the real Moss SDK — swap point documented). 3/3 integration tests pass, including the real scenario: retrieval returns both the stale and current prep sheet for one query, resolution correctly picks current via supersession |
| Cross-domain generalization (second domain, same code) | Unmodified gate run against a second fictional policy pack | **Run, with two real findings published, not hidden**: (1) typed extraction generalizes structurally to an insurance domain with zero code changes; (2) it does NOT yet generalize functionally where conditions carry the meaning (insurance coverage/cost are routinely conditional; extract.py never resolves conditions from context, a pre-existing documented gap that costs real correctness here); (3) the required-document extractor hardcodes a clinic-specific vocabulary and silently extracts zero claims for "police report." See `bench/cross_domain_cases.py` and `tests/test_cross_domain.py` |

No 31 ms, 188/200, universal safety, exclusive feasibility, customer outcome, or placement probability is a measured fact. The only measured numbers as of this update are the ones stated above with their source file. Raw benchmark artifacts and hashes belong in `bench/` only when generated.

## Submission checklist

All unchecked. Record evidence paths/URLs and dates when completed; an accepted risk does not waive mandatory rules.

- [x] Event target explicitly resolved and recorded: Moss, confirmed by Ashraf.
- [ ] Eligibility, registration, submission route, and deadline verified.
- [ ] Required sponsor integration actually runs in the deployed workflow.
- [ ] Source/setup reproducible from a clean environment.
- [ ] Policy fixtures labeled synthetic with provenance/license status.
- [ ] Full speech-boundary, authority, failure, and cancellation checks pass.
- [ ] Held-out results and baseline comparison published with denominators.
- [ ] Latency includes buffering and user-visible response time.
- [ ] First-time user can explain the result; stakeholder evidence is honestly labeled.
- [x] Deployed application tested from fresh browser/mobile network. **LIVE: https://hesitate.onrender.com** — /health and /gate/demo confirmed 200 OK, real gate output (2026-09-13).
- [ ] Microphone denied, disconnect, loading, timeout, and quota states usable.
- [ ] Credentials protected; duration/concurrency/token limits verified.
- [ ] Budget and judging-access plan tested; replay clearly distinguished from live app.
- [ ] Required documents, public video, source links, and demo links verified.
- [ ] Claims match actual evidence; no unmeasured example numbers in submission copy.
- [ ] Final adversarial review of the implementation, not merely this plan.
- [ ] Submission completed on the correct platform(s), receipt retained.
- [ ] If Moss shortlisted, pitch and offline recording rehearsed; permitted changes verified.

## Current verdict

**ALIGNED at the plan level with published Moss requirements. CONCERNS for first-place readiness:** customer need and advantage over a template FAQ remain hypotheses. Plan-level correctness issues were amended; implementation evidence is wholly outstanding. The full-depth scope is specified in PLAN.md. When building is separately authorized, implement the vertical slice as the foundation for all work packages, not as a substitute for the complete submission.

## Full-depth mandate and completion ledger — September 13

Ashraf has help and explicitly rejects scope reduction based on assumed solo-build time. All PLAN.md Sections 9–22 are intended deliverables. No automatic one-site/one-attribute fallback, NLI cut, second-domain cut, or reduced benchmark is authorized by the earlier review. Official deadlines and contributor rules still apply; helper identities, roles, and availability remain to be recorded.

| Package | Required completion evidence | Status |
|---|---|---|
| W0 Contracts | Versioned schemas, shared fixtures, resolved sponsor control path | Pending |
| W1 Domain/product | All original claim families, source records, interviews and tasks | Pending |
| W2 Policy lifecycle | Import/review, publish, conflict, rollback, revocation race tests | Pending |
| W3 Verification | Typed + semantic metrics, decomposition failures, checked corrections | Pending |
| W4 Voice | Actual TTS/played-audio traces, interruption and ordering tests | Pending |
| W5 Staff workflow | Persisted isolated cases, permissions, assignment/resolution/update loop | Pending |
| W6 Evidence | 2,000 primary cases, 200 task scenarios, fair six-backend comparison and ablations | Pending |
| W7 Portability | Second-agent example, 400-case second-domain pack, adaptation log | Pending |
| W8 Operations | Concurrent deployment, resource bounds, restore, privacy and failure tests | Pending |
| W9 Presentation | User observations, short/full demonstrations, artifact links, final implementation review | Pending |

Counts are planned targets, never completed results. A package is complete only when its proof exists and passes. The full-depth design has received local consistency review; the attempted final independent review of the expanded file could not run because the review agents hit a usage limit. Their earlier technical/product recommendations informed the expansion, but their earlier CLEAN verdict applies only to the earlier smaller plan.

## Competitive-strengthening amendment — planning only

The user explicitly requested plan changes only, with no building. No application work or external action is authorized by this amendment. PLAN.md Sections 19–22 add the following mandatory evidence protocols; all remain pending.

| Requirement | Owner package | Current evidence |
|---|---|---|
| Strong approved-answer and existing-guardrail baselines with equal source metadata | W6 | Protocol planned; no run |
| Preregistered primary outcome, workload strata, target margins, uncertainty and exclusion rules | W6 | Specification only |
| Firsthand problem observations and observed before/after product change | W1/W9 | No participants or findings |
| Independent developer integration exercise | W7/W9 | No attempt performed |
| Judge-objection evidence index linking each claim to proof | W9 | Matrix planned; artifacts pending |
| Independent comparison using official rubric and strongest baseline | W9 | Not performed |
| Separate technical, competitive-value, and event-fit verdicts | Integration lead | Technical implementation absent; advantage unmeasured; Moss confirmed; administrative checks pending |

Planned decision thresholds must be finalized before locked evaluation; they are not observed performance. Failure does not authorize scope cuts or weaker baselines. Diagnose and improve the relevant workflow, then evaluate on fresh evidence. A persistent lack of comparative value remains a concern rather than being declared solved in prose.

## Moss-specific alignment verification

- Confirmed fit: real-time voice plus agent reliability/evaluation.
- Explicit default: Moss in deployed retrieval; alternative databases are benchmark configurations.
- All five mandatory artifact contracts and owners are in PLAN.md Section 23.
- Three-minute video length is our editorial target, not a verified Moss rule.
- Registration/form access and actual contributor eligibility remain pending; published team maximum is two.
- The complete plan preserves full scope. No building, registration, calls, or publication occurred.

## Published-rule coverage and remaining checks

This matrix separates planned coverage from actual compliance. Sources: official Moss overview/rules/resources linked above. No claim that every eligibility condition or authenticated form field has been satisfied.

| Rule/requirement | Plan coverage | Actual compliance status |
|---|---|---|
| Age of majority / eligible location | Verify participant eligibility before entry | Not verified |
| Solo or team of at most two | Work-package roles do not imply extra entrants; contributor review required | Actual helper arrangement not verified |
| Participant/team's own work | Record authorship, contributor roles, source/model licenses and attribution | Future artifacts not yet available to inspect |
| HiDevs registration | Explicit required administrative task | Not verified |
| Submit on HiDevs by September 20, 2026, 23:59 IST | Deadline and official event route recorded | Form not inspected; no submission |
| Meaningful Moss retrieval | Default live backend, evidence trace and matched performance comparison | Planned, not implemented |
| Functional theme-aligned application | Voice plus agent reliability/evaluation; complete operational flow | Planned, not implemented |
| GitHub source and setup | Section 23 artifact contract | Not created |
| Deployed working agent/application | Section 23 live-workflow acceptance | Not deployed |
| Diagram of architecture/retrieval | Section 23 diagram contract | Not created |
| PRD with problem/users/solution/requirements | Section 23 PRD contract | Not created |
| Working demo explaining Moss | Section 23 video contract | Not recorded |
| Additional submission form instructions/organizer updates | Check before final submission; do not infer absent constraints | Still to verify |

Conclusion: published project requirements are covered by the plan. Full entry compliance cannot be certified until the pending participant, form, and actual-deliverable checks are completed. The unresolved event mismatch is no longer a concern.
