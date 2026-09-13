# Hesitate — reviewed submission plan

Reviewed September 12–13, 2026. Builder: Ashraf, solo. This replaces the original plan, preserved unchanged in `docs/review/PLAN.opus.original.md` for comparison, not execution. The user's review request authorizes amendments, including the original locked sections.

**Target clarification pending:** this repository targets YC Fall 2026 × Moss; the supplied attachment targets CALL-E. These amendments repair the existing Moss proposal without selecting an event on Ashraf's behalf. Do not begin sponsor-specific implementation until the target is resolved. This is not a CALL-E submission plan. See `COMPETITION.md` for verified requirements and the mismatch.

**Assessment:** the original plan had blocking correctness problems. The revised concept is testable and substantially narrower. First-place competitiveness still depends on user evidence, implementation, and measured results; there is no defensible numerical win probability.

## 1. Product and competitive thesis

Hesitate checks a clinic voice agent's administrative answers against versioned policy facts before speech synthesis. Keep the clinic setting, output gate, and visible evidence trace. Cover three attributes: arrival offsets, required administrative documents, and published appointment windows. Use fictional clinics and explicitly synthetic policies.

Proposed headline: **“Catch a clinic agent's wrong instruction before it is spoken.”**

Remove fasting/medication instructions, diagnosis, individual insurance eligibility, patient-specific pricing, and the invented patient-harm story. No real patient data. This is a bounded administrative prototype, not a clinically validated safety system. Do not claim to verify every factual statement in arbitrary conversation.

The user hypothesis is a front-desk coordinator maintaining instructions that vary by site and change over time. The buyer hypothesis is a clinic operator or voice-agent implementer. Neither is validated. Do not invent call volumes, customer incidents, savings, adoption, or willingness to pay.

Before expanding the build, Ashraf should seek one short conversation with a coordinator or operations worker: which administrative mistakes create repeat work, how policies change, and what would make this prototype useful or unacceptable. Record anonymized observations and the resulting product decision. If unavailable, disclose that and run a labeled proxy usability test; it is not customer validation. No automated outreach is authorized by this plan.

**The hardest alternative is structured lookup plus approved templates.** For a small static FAQ it may be simpler, safer, and faster. Build that baseline. Hesitate earns its complexity only through measured value in paraphrased/multi-question interaction or as a reusable speech boundary for an existing agent. If it adds no value, prefer deterministic answers and describe the gate as a bounded integration/evaluation contribution.

For Moss, the proposed first-place advantage is a complete, understandable workflow with unusually inspectable evidence about what reaches speech. Sponsor retrieval must materially serve that workflow. “Only possible with Moss” is not a defensible premise.

## 2. Judging fit and minimum experience

Conditional on the Moss target: Product & UX 35%, Technical Execution 30%, Speed & Latency 20%, Demo & Presentation 15%. Sources and administrative requirements are in `COMPETITION.md`. The idea fits conversational AI and agent reliability. Do not speculate about competitors' quality or field size.

| Criterion | Evidence to produce |
|---|---|
| Product & UX | A complete question-to-answer flow, useful decline, one observed usability test, honest customer-validation status |
| Technical execution | Actual Moss calls, applicability-aware policy resolution, enforced TTS boundary, cancellation/error tests, reproducible evaluation |
| Speed & latency | Actual search and whole-gate timing, paired end-to-end measurements, accuracy and latency beside a simple baseline |
| Demo | Audible useful answer, clearly labeled blocked draft, applicable source, conflict case, measured results and limits |

One screen: choose a fictional site, start a browser voice session, ask a question, hear the approved answer, inspect the source. Provide three suggested questions. Main states: “Checked against current policy,” “Draft corrected,” and “Needs staff review.” Keep stage timings expandable. Never use a universal “safe” badge.

Only the observer trace shows the blocked draft. The caller hears the approved answer. Distinguish proposed text from speech actually released. A local unresolved-question summary records the site, question, and reason. Do not claim anyone was contacted or a callback booked.

Offer a normal live-agent mode and a visibly labeled fault-injection mode. Injection makes the verification demonstration repeatable; it must never be presented as a spontaneous model error.

## 3. Architecture and trust boundaries

```text
Browser mic → LiveKit/STT → LLM text stream
                                ↓
                     bounded sentence buffer
                                ↓
                 parse every supported factual clause
                                ↓
                 Moss candidate policy retrieval
                                ↓
             exact scope / version / conflict resolution
                                ↓
            release / deterministic correction / decline
                                ↓
                sole TTS entry point → caller audio
                                ↓
                 decision, evidence, release trace
```

Keep Python LiveKit worker and Next.js client; select one worker host after a deployment smoke test. Use an STT→LLM→TTS pipeline, not a speech-to-speech model. LiveKit's documented `tts_node` is a candidate interception point; verify behavior in the pinned version. Every application speech path must use the boundary, including corrections, tool replies, and explicit speech calls. Only audited fixed nonfactual phrases may skip factual comparison.

Load one versioned Moss policy index at worker startup. Readiness requires a successful load and known query. Pin tested packages; current Moss docs advise SDK 1.9.0 or later. Do not copy the cookbook's log-and-continue behavior after a failed policy load. Verify where embedding and retrieval execute; startup downloads/hydration are not warm-query time.

Use ordinary in-memory conversation state. Cut the second transcript index and cloud transcript persistence. Caller statements and model drafts are untrusted context, never policy evidence. Keep credentials server-side; issue short-lived room-scoped tokens and enforce duration/concurrency/input bounds. Do not log raw audio or identifiers by default.

Repository shape: `agent/`, `web/`, `corpus/`, `bench/`, `docs/`. Create modules only when they implement actual behavior.

## 4. Verification contract

### Canonical policies

Author readable synthetic passages and manually reviewed structured records. Fields: `policy_id`, `source_id`, `source_span`, `site`, `service`, `attribute`, `value`, `unit`, `polarity`, `conditions`, `effective_from`, `effective_to`, and explicit `supersedes` where relevant. State that facts are curated; do not imply automatic verification of arbitrary documents. Each decision records the corpus hash/version.

At ingestion validate schema, scope, units, and overlapping effective records. Maintain an exact map of all applicable records per key. Moss retrieves candidates from natural-language questions/claims; resolve each candidate's key against the complete applicable set. Top-k must not hide a conflict. Missing or ambiguous candidates cause refusal, not automatic approval.

Supersession must be explicit, not highest similarity or latest upload. Superseded facts are not current authority. Equally applicable conflicting policies without a precedence rule make the key conflicting. Pin one corpus snapshot per turn; do not mix versions during an update.

### Claims and decisions

Compare `(site, service, attribute, normalized value/unit, polarity, conditions, effective time)`. Inherit pronoun scope only from explicit confirmed session context; otherwise ask for clarification. Normalize only declared number, time, range, and unit forms. Appointment windows must declare their timezone and whether each boundary is inclusive; ambiguous times require clarification. Absence of a record is not proof of a negative statement.

Use a bounded parser for the three administrative attributes. No general NER/NLI model in the MVP. Account for every factual clause: one true number cannot approve a mixed sentence. Residual unsupported factual wording makes the entire sentence unverified. Only an audited allowlist of fixed conversational phrases is exempt. Measure the resulting coverage loss.

| Evidence | Decision |
|---|---|
| Same applicable key, conditions, polarity, and normalized value | Supported |
| Same applicable key, incompatible value/polarity | Contradicted |
| Missing scope/evidence, unsupported wording, incomplete parse | Unverifiable |
| Unresolved applicable authorities disagree | Conflict |

Release the original sentence only if **every** atomic claim is supported. Correct contradictions using audited deterministic templates populated solely from validated records. No unchecked LLM-generated correction. If a complete replacement cannot be established, decline. On conflicts, parsing failure, absent evidence, or timeout say: “I can't confirm that from this clinic's policy. Please check with the front desk.” This does not promise a handoff.

The structural guarantee is that no candidate bypasses the gate. The accuracy of decisions remains empirical and domain-bounded. Curated source errors, parsing gaps, and speech recognition errors remain limitations.

### Stream lifecycle

One bounded buffer and ordered release per turn. Handle decimals, abbreviations, compound clauses, and final unpunctuated text. Final flush goes through the same gate. Set explicit buffer/verification timeouts; discard unapproved text and decline on failure. Tag work by session/turn; cancelled turns cannot release late results or queued audio. Clear pending work on interruption/disconnect. Test interruption behavior.

Never send unchecked text to TTS to hide latency. Connection prewarming is allowed; speculative synthesis is outside scope. Instrument actual TTS input and audio release, not only dashboard verdicts.

## 5. Evaluation and proof

Plan 200 labeled cases: 100 development and 100 held out, each with 40 supported, 25 contradicted, 20 unverifiable, and 15 conflict cases. Separate paraphrase families and policy variants across partitions; include an unseen fictional site with normally loaded records and no parser changes. Independently human-review labels. These are planned counts, not completed work.

Lock the holdout hash before tuning. If a holdout failure leads to a fix, retain that result, move the exposed case to regressions, and add fresh evaluation cases. Never describe repeatedly tuned examples as untouched evidence.

Cover site/service swaps, stale policy, conflict outside top-k, mixed claims, negation, units/ranges, missing evidence, unseen wording, ambiguous pronouns, caller policy-overrides, final flush, malformed data, retrieval errors/timeouts, and cancellation. Unknown claims silently classified nonfactual count as failures. Tests inspect text handed to TTS; end-to-end recordings/traces connect approved text to audio.

Publish counts and denominators: unsafe releases/unsafe candidates, unnecessary suppressions/supported candidates, correct completed answers/answerable questions, extraction coverage, full verdict confusion matrix, corrected versus declined outcomes. Separate fault-injection results from natural model behavior. Zero observed escapes in finite testing is not universal safety.

### Baselines

Compare ordinary RAG, RAG plus Hesitate, and structured lookup plus templates on identical questions/policies. Report correctness, completion, response time, and policy-update effort. Do not sabotage baseline prompts or sources to manufacture a difference.

For retrieval attribution compare Moss against small local keyword/exact lookup. Exact lookup may win known-key cases; say so. One hosted comparator is optional after the core product and artifacts pass. Match corpus, filters, embedding model where possible, top-k, hardware/region, and quality; disclose mismatches. Cut the five-database ablation. Artificial delays are labeled simulations, never vendor measurements.

### Timing

Record end-of-user-speech, first LLM token, sentence completion, gate duration, embedding/search duration where exposed, TTS submission, first audio frame, client playout, and first useful answer. Use synchronized clocks or report server/client intervals separately. Report both buffering overhead and verification overhead. Use paired gate on/off runs with identical pipeline settings and randomized order; also show the ordinary ungated experience if buffering differs.

Report cold/warm p50/p95, sample count, hardware, corpus size, model/SDK versions, and failures. Omit p99 without enough data. Initial **targets**, not results: warm gate p95 ≤60 ms and added first-useful-answer p95 ≤200 ms. Before publishing, aim for 1,000 warm gate evaluations and 30 paired voice turns. These sample counts do not prove perceived equivalence. If buffering dominates, shorten output units or narrow scope; do not exclude it from the story. Measure latency on a named environment, not fragile shared-CI timing assertions.

Internal release targets: all boundary/authority/cancellation regressions pass, zero unsafe releases in locked safety cases, ≥90% correct completion on answerable held-out questions, and ≤10% unnecessary suppression of supported candidates. These are prototype targets, not clinic acceptance standards. Publish actual results; a failed target requires a fix, narrowed claim, or an explicit unready verdict.

## 6. Conditional Moss schedule and cutoffs

Do not execute this schedule for CALL-E. If target confirmation arrives later, cut scope rather than squeeze every task into the final day. No implementation is claimed by this file. September 12 has elapsed; start with one attribute and one site, adding the other two attributes only if the public slice works by September 14. If that cutoff slips, retain the one-attribute scope and protect the artifact/submission buffer.

| IST date | Work and completion evidence |
|---|---|
| Sep 13 | Confirm target and registration route; prioritize Moss load/query and rejected-candidate interception spike; tiny curated policy pack; begin user validation |
| Sep 14 | Public voice→gate→audio slice; authority, compound-claim, cancellation tests; lock evaluation partitions |
| Sep 15 | Finish one-screen workflow; observe first-time user and fix clearest confusion |
| Sep 16 | Baselines, holdout, latency; publish failures and narrow scope if needed |
| Sep 17, 18:00 | Feature freeze; review release blockers |
| Sep 18 | README/setup, PRD, diagram, video; clean-checkout and fresh-browser verification |
| Sep 19, 18:00 | Submit through verified platform(s); retain receipt and links; rehearse |
| Sep 20 | Deadline buffer/permitted corrections; official deadline 23:59 IST |

If voice fails by Sep 14, use browser text-input→verified-speech with live Moss/gate execution and disclose the reduced interaction. If semantics fail, narrow to arrival offset and one site without weakening release rules. If latency fails, retain correctness and remove unsupported speed claims. If basic release checks fail, the work is unready.

Parallel agents may independently review fixtures, research, and documentation; one owner integrates the gate. Ashraf must understand the authority rules, parsing limits, measurements, and simpler alternatives.

## 7. Demo, claims, and judge questions

Use a synthetic administrative example: current arrival offset 15 minutes, injected candidate 30 minutes. Label both synthetic policy and injection. The caller hears only the approved instruction. Do not fabricate a patient outcome.

| Approximate time | Show |
|---|---|
| 0:00–0:15 | One-sentence problem and labeled correction moment |
| 0:15–0:55 | Normal live question, useful audible answer, applicable source |
| 0:55–1:20 | Conflict/ambiguous site, useful decline and unresolved record |
| 1:20–1:50 | Small architecture view, actual Moss retrieval and TTS boundary |
| 1:50–2:20 | Measured quality/latency beside simplest baseline |
| 2:20–2:45 | Actual user observation if obtained, reuse and limits |
| 2:45–3:00 | Working links and concise close |

Run fault injection 20 consecutive times without escape; separately log 20 natural turns including correct answers with nothing to catch. These prove observed behavior, not model determinism. Preserve traces/scenario IDs. Mark recorded/replayed fallback explicitly; it accompanies a working deployment.

Do not publish sample numbers as headlines. Use `[measured result pending]` until scripts generate results. No “only possible with Moss,” “all existing fixes fail,” “every claim verified,” or “no change to how it feels.” Use measured added latency, scoped accuracy, and actual observations.

**Why not templates?** They may be best for static FAQs. Show task comparisons; claim value only where observed.

**Is it novel?** Open-source output guardrails already exist, including NeMo buffer-before-release checks. The contribution is this policy-aware voice workflow, implementation, and evidence, not invention of output verification.

**Wrong retrieved policy?** Retrieval selects candidates; exact applicability and full-key conflict resolution govern support. Ambiguity leads to clarification/refusal.

**What still fails?** Source curation, parsing, ASR, and unsupported language. Explain limits without claiming certification.

**Does it slow speech?** Show full paired results including buffering, not only search time.

## 8. Scope and final review

Cut accounts, settings, extra dashboards, transcript search, clinical advice, NLI, lending/insurance generalization, multiple vector adapters, and PSTN for the Moss variant. Keep necessary environment/deployment configuration and integration tests. They are part of demonstrating a working product.

Use the concrete checklist in `COMPETITION.md`. The installed competition skill has neither the original plan's alleged tracker template nor numbered freeze checklist. Do not reference nonexistent requirements.

The next valuable evidence is a working vertical slice and user feedback. Stop speculative expansion when proof, usability, and reliable submission have higher expected value. A plan is not a completed winning submission.
