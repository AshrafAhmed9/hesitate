# Hesitate — submission plan

Written and revised September 12–13, 2026 by Ashraf, ahead of building. This is the specification
the rest of the repository implements — see `COMPETITION.md` for what's actually been built and
proven against it, including what changed along the way.

**Target:** YC Fall 2026 × Moss: The Zero Latency Builder Sprint.

**Assessment:** first-place competitiveness depends on demonstrated depth, customer value, and
execution, not on the plan alone. The specification below is the target; see `COMPETITION.md` for
the honest record of how much of it actually got built and proven.

## 1. Product and competitive thesis

Hesitate checks a clinic voice agent's administrative answers against versioned policy facts before speech synthesis. Keep the clinic setting, output gate, and visible evidence trace. Restore all six original claim families: preparation duration, arrival offset, source-defined coverage statements, required documents, quoted cost, and appointment windows. Add site/location, opening hours, and cancellation rules to exercise entity, temporal, and conditional reasoning. Use fictional clinics and explicitly synthetic policies. Sections 9–22 define the full coverage, operational lifecycle, research depth, competitive proof, and delivery contracts.

Proposed headline: **“Catch a clinic agent's wrong instruction before it is spoken.”**

Preparation-duration and insurance/cost cases verify consistency with explicitly fictional supplied policies. They do not establish medically appropriate preparation, real insurance eligibility, or an actual price for a patient. Do not invent patient-harm stories or use real patient data. No diagnosis, treatment recommendation, or real-world clinical-safety certification is claimed. This boundary preserves domain depth without presenting synthetic consistency checks as medical truth.

The user hypothesis is a front-desk coordinator maintaining instructions that vary by site and change over time. The buyer hypothesis is a clinic operator or voice-agent implementer. Neither is validated. Do not invent call volumes, customer incidents, savings, adoption, or willingness to pay.

In parallel with the build, Ashraf should seek at least three short conversations with a coordinator or operations worker: which administrative mistakes create repeat work, how policies change, and what would make this prototype useful or unacceptable. Record anonymized observations and the resulting product decision. If unavailable, disclose that and run a labeled proxy usability test; it is not customer validation. No automated outreach is authorized by this plan.

**The hardest alternative is structured lookup plus approved templates.** For a small static FAQ it may be simpler, safer, and faster. Build that baseline. Hesitate earns its complexity only through measured value in paraphrased/multi-question interaction or as a reusable speech boundary for an existing agent. If it adds no value on static questions, report that result and test the full policy-change, ambiguity, handoff, and multi-turn workload before judging the product thesis. Use approved templates where they work best while completing the deeper verification and operational scope.

For Moss, the proposed first-place advantage is a complete, understandable workflow with unusually inspectable evidence about what reaches speech. Sponsor retrieval must materially serve that workflow. “Only possible with Moss” is not a defensible premise.

## 2. Judging fit and coherent experience

Official Moss judging weights: Product & UX 35%, Technical Execution 30%, Speed & Latency 20%, Demo & Presentation 15%. Sources and administrative requirements are in `COMPETITION.md`. The idea fits conversational AI and agent reliability. Do not speculate about competitors' quality or field size.

| Criterion | Evidence to produce |
|---|---|
| Product & UX | A complete question-to-answer flow, useful decline, one observed usability test, honest customer-validation status |
| Technical execution | Actual Moss calls, applicability-aware policy resolution, enforced TTS boundary, cancellation/error tests, reproducible evaluation |
| Speed & latency | Actual search and whole-gate timing, paired end-to-end measurements, accuracy and latency beside a simple baseline |
| Demo | Audible useful answer, clearly labeled blocked draft, applicable source, conflict case, measured results and limits |

Primary call screen: choose a fictional site, start a browser voice session, ask a question, hear the approved answer, inspect the source. Provide three suggested questions. Main states: “Checked against current policy,” “Draft corrected,” and “Needs staff review.” Keep stage timings expandable. Never use a universal “safe” badge.

Only the observer trace shows the blocked draft. The caller hears the approved answer. Distinguish proposed text from speech actually released. An unresolved-question record feeds the staff resolution workflow in Section 12. Before an actual assignment or action succeeds, do not claim anyone was contacted or a callback booked.

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

Load the active versioned Moss policy release at worker startup; staging, retained snapshots, and per-session indexes follow Sections 11 and 13. Readiness requires a successful load and known query. Pin tested packages; current Moss docs advise SDK 1.9.0 or later. Do not copy the cookbook's log-and-continue behavior after a failed policy load. Verify where embedding and retrieval execute; startup downloads/hydration are not warm-query time.

Use explicit conversation state plus a separate per-call semantic memory index for provenance-aware recall and handoff. Section 13 defines why both exist and how they stay separate from authoritative policy. Caller statements and model drafts are untrusted context, never policy evidence. Persist only the consented/redacted evaluation or operational records required by the workflow. Keep credentials server-side; issue short-lived room-scoped tokens and enforce duration/concurrency/input bounds. Do not log raw audio or identifiers by default.

Repository shape: `agent/`, `web/`, `corpus/`, `bench/`, `docs/`. Create modules only when they implement actual behavior.

## 4. Verification contract

### Canonical policies

Author readable synthetic passages and manually reviewed structured records. Fields: `policy_id`, `source_id`, `source_span`, `site`, `service`, `attribute`, `value`, `unit`, `polarity`, `conditions`, `effective_from`, `effective_to`, and explicit `supersedes` where relevant. State that facts are curated; do not imply automatic verification of arbitrary documents. Each decision records the corpus hash/version.

At ingestion validate schema, scope, units, and overlapping effective records. Maintain an exact map of all applicable records per key. Moss retrieves candidates from natural-language questions/claims; resolve each candidate's key against the complete applicable set. Top-k must not hide a conflict. Missing or ambiguous candidates cause refusal, not automatic approval.

Supersession must be explicit, not highest similarity or latest upload. Superseded facts are not current authority. Equally applicable conflicting policies without a precedence rule make the key conflicting. Pin the call snapshot and use it consistently within each turn; Section 11 specifies ordinary publication, explicit refresh, and urgent revocation.

### Claims and decisions

Compare `(site, service, attribute, normalized value/unit, polarity, conditions, effective time)`. Inherit pronoun scope only from explicit confirmed session context; otherwise ask for clarification. Normalize only declared number, time, range, and unit forms. Appointment windows must declare their timezone and whether each boundary is inclusive; ambiguous times require clarification. Absence of a record is not proof of a negative statement.

Use typed parsers for structured claims and a separately calibrated semantic verification path for eligible nonnumeric claims, as specified in Section 10. Every original claim family is included; a new parser or NLI model cannot weaken the shared release rule. Account for every factual clause: one true number cannot approve a mixed sentence. Residual unsupported factual wording makes the entire sentence unverified. Only an audited allowlist of fixed conversational phrases is exempt. Measure the resulting coverage loss.

| Evidence | Decision |
|---|---|
| Same applicable key, conditions, polarity, and normalized value | Supported |
| Same applicable key, incompatible value/polarity | Contradicted |
| Missing scope/evidence, unsupported wording, incomplete parse | Unverifiable |
| Unresolved applicable authorities disagree | Conflict |

Release the original sentence only if **every** atomic claim is supported. Correct contradictions using audited deterministic templates populated solely from validated records. No unchecked LLM-generated correction; semantic replacements may be drafted only through the bounded re-verification path in Section 10. If a complete replacement cannot be established, decline. On conflicts, parsing failure, absent evidence, or timeout say: “I can't confirm that from this clinic's policy. Please check with the front desk.” This does not promise a handoff.

The structural guarantee is that no candidate bypasses the gate. The accuracy of decisions remains empirical and domain-bounded. Curated source errors, parsing gaps, and speech recognition errors remain limitations.

### Stream lifecycle

One bounded buffer and ordered release per turn. Handle decimals, abbreviations, compound clauses, and final unpunctuated text. Final flush goes through the same gate. Set explicit buffer/verification timeouts; discard unapproved text and decline on failure. Tag work by session/turn; cancelled turns cannot release late results or queued audio. Clear pending work on interruption/disconnect. Test interruption behavior.

Never send unchecked text to TTS to hide latency. Connection prewarming is allowed; speculative synthesis is outside scope. Instrument actual TTS input and audio release, not only dashboard verdicts.

## 5. Evaluation and proof

Start with a 200-case contract suite: 100 development and 100 held out, each with 40 supported, 25 contradicted, 20 unverifiable, and 15 conflict cases. Then complete the larger independent evaluation program in Section 14; the starter suite is not the final evidence package. Separate paraphrase families and policy variants across partitions; include an unseen fictional site with normally loaded records and no parser changes. Independently human-review labels. These are planned counts, not completed work.

Lock the holdout hash before tuning. If a holdout failure leads to a fix, retain that result, move the exposed case to regressions, and add fresh evaluation cases. Never describe repeatedly tuned examples as untouched evidence.

Cover site/service swaps, stale policy, conflict outside top-k, mixed claims, negation, units/ranges, missing evidence, unseen wording, ambiguous pronouns, caller policy-overrides, final flush, malformed data, retrieval errors/timeouts, and cancellation. Unknown claims silently classified nonfactual count as failures. Tests inspect text handed to TTS; end-to-end recordings/traces connect approved text to audio.

Publish counts and denominators: unsafe releases/unsafe candidates, unnecessary suppressions/supported candidates, correct completed answers/answerable questions, extraction coverage, full verdict confusion matrix, corrected versus declined outcomes. Separate fault-injection results from natural model behavior. Zero observed escapes in finite testing is not universal safety.

### Baselines

Compare ordinary RAG, RAG plus Hesitate, and structured lookup plus templates on identical questions/policies. Report correctness, completion, response time, and policy-update effort. Do not sabotage baseline prompts or sources to manufacture a difference.

For retrieval attribution compare Moss against small local keyword/exact lookup. Exact lookup may win known-key cases; say so. Complete the multi-backend comparison in Section 14: Moss, local exact/keyword, local vector search, Chroma, pgvector, and Pinecone. Match corpus, filters, embedding model where possible, top-k, hardware/region, and quality; disclose mismatches. Backend count alone is not the result: attribution and comparable retrieval quality are required. Artificial delays are labeled simulations, never vendor measurements.

### Timing

Record end-of-user-speech, first LLM token, sentence completion, gate duration, embedding/search duration where exposed, TTS submission, first audio frame, client playout, and first useful answer. Use synchronized clocks or report server/client intervals separately. Report both buffering overhead and verification overhead. Use paired gate on/off runs with identical pipeline settings and randomized order; also show the ordinary ungated experience if buffering differs.

Report cold/warm p50/p95, sample count, hardware, corpus size, model/SDK versions, and failures. Omit p99 without enough data. Initial **targets**, not results: warm gate p95 ≤60 ms and added first-useful-answer p95 ≤200 ms. Before publishing, aim for 1,000 warm gate evaluations and 30 paired voice turns. These sample counts do not prove perceived equivalence. If buffering dominates, improve segmentation/scheduling and measure the tradeoff without dropping claim families; do not exclude buffering from the story. Measure latency on a named environment, not fragile shared-CI timing assertions.

Internal release targets: all boundary/authority/cancellation regressions pass, zero unsafe releases in locked safety cases, ≥90% correct completion on answerable held-out questions, and ≤10% unnecessary suppression of supported candidates. These are prototype targets, not clinic acceptance standards. Publish actual results; a failed target requires a fix, narrowed claim, or an explicit unready verdict.

## 6. Team execution without automatic scope cuts

Use the dependency-based work packages in Section 16. Do not silently downgrade to one attribute, remove semantic verification, drop cross-domain evidence, or replace the live product with a recording because of an assumed time budget. A failed gate calls for diagnosis, additional help, and an explicit status update. It does not authorize deletion of the full target.

The official event deadline remains an external fact: the Moss deadline is September 20, 2026, 23:59 IST. The event is confirmed; implementation remains outside the current planning-only authorization. Plan staffing against the remaining calendar once contributor availability is known; do not pretend help makes dependencies instantaneous. Maintain a current manifest of implemented, verified, and remaining work. If full scope is not delivered, state that rather than marking an incomplete version complete.

Build and integrate a vertical slice first, then complete all work packages. Core behavior freezes after correctness gates pass; evidence, UX, and documentation continue in parallel. Record a release candidate and perform a full rehearsal before submitting. The public submission must meet the confirmed deadline; a recorded fallback supports demonstration reliability but never substitutes for implementation.

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

## 8. Scope ownership and completion

The full scope includes typed and semantic verification, every original claim family, policy ingestion and approval, source conflict analysis, atomic policy updates, per-call memory, staff resolution, operational history, multiple retrieval backends, held-out evaluation, a second domain, and a reusable integration package. These are planned deliverables, not a stretch list.

Do not add unrelated services or product lines. Use the simplest implementation that completes each contract; a single service and ordinary persistence can support substantial depth. Add isolated workers only when measured resource contention warrants them. Do not introduce a new database or AI agent merely to make the architecture diagram larger.

Use `COMPETITION.md` for administrative evidence and the capability matrix below for product completion. Scope changes must be visible to Ashraf, with the competitive consequence explained; do not automatically apply the former solo-MVP cuts. The user's depth instruction supersedes those earlier recommendations. Claims of correctness, user value, performance, or completion still require evidence.

## 9. Full product scope and judge-visible proof

The central workflow is **source → reviewed policy → verified conversation → staff resolution → new policy release → regression evidence**. The technical contribution is enforcing and inspecting that workflow at the speech boundary while maintaining useful conversation.

| Capability | Full required behavior | Demonstrable completion |
|---|---|---|
| Policy workspace | Import Markdown/text, structured JSON, and text PDFs; preserve originals; propose typed facts; show source spans for review | Reviewer can identify and correct a deliberately mis-extracted field before publication |
| Authority management | Site/service/audience scope, effective dates, explicit precedence, exceptions, supersession and unresolved conflicts | Wrong-site, obsolete, and equally authoritative contradictory records cannot silently authorize an answer |
| Publication | Validate, stage, activate, retire/revoke, and roll back immutable releases | Update changes subsequent answers; failed activation retains the previous working release |
| Full claim coverage | All six original families plus location, hours, and cancellation conditions; numeric and semantic claims | A multi-question conversation completes across multiple sites without excessive refusal |
| Speech assurance | Every factual clause checked; original and correction paths share enforcement | A rejected claim is absent from actual TTS input and caller audio |
| Conversation memory | Resolve context, remember explicit caller selections and distinguish untrusted assertions from approved facts | A caller correction updates site context without becoming policy evidence |
| Staff operations | Persisted inbox, assignment, resolution, case-specific replies, and reviewed policy-change proposals | A real in-app item progresses from open to resolved and links to the relevant call |
| Decision inspection | Search by call, source version, verdict, reason; inspect sources and audio events | Staff explains a decline and identifies the exact faulty policy without reading code |
| Evaluation workbench | Compare candidate releases, expose changed answers/regressions, reproduce baseline results | A release that breaks an affected case is blocked or explicitly resolved before publication |
| Reusable integration | Versioned gate interface, packaged example, a second compatible text-stream agent | Another worker invokes the same core without copying clinic logic |
| Cross-domain pack | Fictional insurance servicing policy pack using the same core and explicit adaptation contract | Run coverage limits, deadlines, required documents, exceptions, and ambiguous applicability cases |
| Deployment operations | Staff permissions, isolation, dependency health, resource bounds, recovery and observability | Concurrent calls remain isolated; a dependency failure produces truthful degraded behavior |

“Insurance coverage” means whether a supplied fictional policy explicitly describes a benefit/condition, not a determination about a real person's benefits. “Preparation duration” means fidelity to a fictional instruction record, not medical advice. “Cost” includes currency, service, effective date, tax/fee inclusion, and conditionality; a bare matching number is insufficient.

Every capability is required in the intended completed project. Showing five capabilities in a short video does not remove the others from delivery. Keep deeper evidence accessible from the deployed product and repository.

## 10. Deep verification architecture

### Claim representation and routing

A `CandidateUnit` records session/turn/unit sequence, exact text and character spans, resolved caller context with provenance, policy snapshot, and generation metadata. Decompose it into `AtomicClaim` records with subject, predicate, object/value, polarity, quantifier, modality, conditions, time, and source text spans. Record unclassified spans explicitly. Full character coverage alone is insufficient: check whether all propositions and qualifications were represented.

Routes are `typed`, `semantic`, `approved_phrase`, and `unclassified`. Use model-assisted decomposition for flexible language, but treat its output as untrusted. Validate references to original spans; compare number/entity/negation/conditional markers in the original against the decomposition; reject omitted qualifications or malformed outputs. Include a separately implemented completeness check and label its errors in evaluation. A decomposition confidence score is not a release authorization. The semantic route remains probabilistic; do not imply exhaustive natural-language understanding has been proved.

Typed modules cover numeric values and units, monetary amounts/currencies, local dates and intervals, required-document sets, categorical coverage statements, conditional obligations, and site/service identity. Include set relationships: “bring ID” does not establish “bring only ID.” Distinguish `may` from `will`, `usually` from `always`, and permitted from required. If a condition cannot be resolved from authoritative policy plus explicit context, request clarification or decline.

### Semantic verification

Use a local entailment model selected by measured domain accuracy, latency, memory, and license. A generic relevance reranker is not an entailment model. For each eligible nonnumeric claim:

1. Retrieve evidence with its resolved scope, preserving top candidates and search configuration.
2. Resolve active authority and conflict status before model scoring.
3. Score entailment, contradiction, and insufficient support; inspect applicable opposing evidence.
4. Require a sufficient source span or a declared composition rule. Concatenating unrelated passages must not create apparent support.
5. Apply calibrated class thresholds and an abstention region. Store model/version and raw scores internally; do not present scores as calibrated truth probabilities unless calibration supports that interpretation.
6. Aggregate every claim's outcome into the sentence decision. Typed contradictions, authority conflicts, unresolved scope, and incomplete decomposition cannot be overridden by NLI.

The typed path does not wait for NLI if it has completely handled the unit. Mixed units await all required decisions, with a bounded deadline and no early release of a conditional prefix. Evaluate typed and semantic p95 separately; a fast typed path cannot hide a slow semantic path in an overall average.

Use development data for extraction design, a separate calibration split for thresholds, and locked test data for claims. Select thresholds against error-versus-completion curves. Document what the model newly supports, which new errors it introduces, and how much additional latency it costs. No fixed “15 ms NLI” claim without measurement.

### Rich corrections and answer relevance

Typed corrections use reviewed templates. Semantic corrections may use one bounded generation attempt, then traverse the entire gate with fresh decomposition and evidence checks. A failed correction falls back to approved clarification/decline text. Never recursively generate corrections without a bound. Preserve original→replacement links.

Verify relevance to the user's original question as a separate product measure. A true statement about opening hours does not complete a question about required documents. For mixed questions, provide the supported answers and explicitly mark the unresolved portion only after reconstructing a complete, checked replacement unit. Do not silently omit the hard part and count the task complete.

### Decisions and auditability

A `Decision` contains a unique ID, original/replacement text hashes, policy snapshot, atomic verdicts/reasons, evidence record IDs and spans, context dependencies, typed-rule or model versions, stage timings, and terminal disposition. `AudioEvent` references that decision and records submitted, queued, playing, interrupted, and finished states. Distinguish audio generated by the server from client-confirmed playout; neither alone proves what a human perceived.

Retain exact source text for reproducibility within the chosen retention policy. Hashes help identify versions; they do not make a malicious server trustworthy or make logs tamper-proof. A downloadable redacted trace should reproduce the verifier decision using the pinned corpus and configuration. Replaying a model may be nondeterministic; preserve original model outputs and distinguish decision replay from fresh model inference.

## 11. Policy ingestion, publication, and revocation

Lifecycle: `uploaded → parsed → extracted → reviewed → validated → staged → active → retired`; revocation is a separate immediate restriction on a record/release. Failed parsing/extraction/staging has an explicit retryable error state. A document upload never becomes trusted solely because a model extracted it.

For each source store original bytes/hash, format, provenance/license, organization/site, parser version, extraction version, and review status. Bound file size and parsing time; reject unsupported/encrypted files clearly. For scanned PDFs, report that OCR is required rather than returning an empty successful extraction. Text-PDF support is the committed input contract; add OCR only with a measured extraction-quality contract.

The review UI shows each proposed fact beside its original passage, with scope, units, effective time, and unresolved ambiguity. Reviewer edits are auditable. Facts without resolvable supporting spans cannot enter an approved release. Treat source text as data, never executable instructions. Reviewer approval establishes local policy authority, not factual truth about the world.

Validation checks include missing scope, incompatible units, timezone/boundaries, impossible intervals, duplicate identity, supersession cycles, nonexistent references, overlapping applicable values, exception precedence, and unsupported conditions. Preserve conflicts; do not erase inconvenient records. Specificity/precedence rules are explicit and versioned, with fixtures for ties. No hidden “newest wins” heuristic.

Compile both the retrieval index and exact authority map from the same immutable manifest. Stage, run known and changed-key regressions, perform retrieval-health probes, then atomically swap the active manifest pointer. Readers see a complete old or complete new release. Failure retains the previous active release; incomplete staged resources can be cleaned without deleting active data. Rollback activates a retained valid snapshot through the same checks.

**Version semantics:** pin a snapshot for each call to preserve conversational consistency. Ordinary publication applies to new calls; show the active call's version. A user-requested refresh starts a new turn using a new snapshot after disclosing changed policy where relevant. An explicit urgent revocation overrides snapshot pinning: before TTS submission and before dispatch of queued audio, check referenced records against the revocation generation. Cancel affected pending output, load a valid replacement and reverify, or decline. Already-played audio cannot be recalled; record the exposure and issue a checked correction if the session is still active. Revocation acceptance and new output admission must share an atomic generation check/lock; a check followed by an unguarded send leaves a race. On accepted revocation, broadcast invalidation to active sessions and stop affected playing/queued output. Network/client-buffered audio can remain in flight: measure maximum post-revocation playout and do not promise zero-delay revocation. If the runtime cannot enforce this, report the limitation and keep the release gate unpassed. Recheck effective-time applicability at output admission even on a pinned snapshot, including expiry and a call crossing midnight.

Test publication/rollback concurrently with reads; revocation during verification, synthesis, queueing, and playback; crashes during staging/activation; and eventual cleanup. Do not claim updates are atomic merely because an SDK has a refresh method. If the SDK lacks a necessary swap operation, own the immutable snapshot reference in application code.

## 12. Staff resolution and operational product

Create three task-oriented views beyond the primary call screen: policy workspace, staff inbox, and decision/evaluation history. Each exists for an actual task rather than decorative analytics. Keyboard access, readable focus/error states, source inspection, and sensible empty states are acceptance requirements.

A `Case` links call/turn, unresolved question, confirmed site/service, reason, relevant evidence, policy snapshot, creation time, assignment, and status. State transitions: `open → assigned → resolved`, with explicit reopening and cancellation. Distinguish `recorded`, `assigned`, and `resolved`; a persisted inbox item does not prove a human has read it. Caller-facing language reflects only completed transitions.

Case creation uses an idempotency key based on call/turn/reason; retrying a callback cannot create duplicates. Assignment and resolution use optimistic version checks to prevent two staff actions silently overwriting one another. Persist a decision/event trail and show who changed the state. A repeated call may link an existing case only with a valid session/case reference; do not identify callers by speculative voice matching.

A resolution can be a one-off reply scoped to the case or a proposed policy amendment. Case-specific answers never automatically become global policy. An amendment enters the reviewed publication workflow. Test the complete loop: conflict → persisted case → staff proposal → reviewer approval → activation → next call correct → regression suite green.

Use the smallest justified access model: public sandbox caller, authenticated staff, and policy publisher. Enforce permissions server-side; hidden buttons are not authorization. Separate disposable public demo fixtures from staff-managed data. Public visitors cannot publish policies, read other visitors' cases, or exhaust unbounded call resources. Do not implement elaborate multi-tenant billing or enterprise identity administration merely for appearance.

A public sandbox may let a judge simulate staff actions in an isolated fixture workspace; label the role simulation and keep it separate from actual authorization. Production-like staff flows use real access checks. No real outbound email, phone notification, or external ticket posting is part of this review authorization.

## 13. Conversation memory and integration depth

Maintain explicit state for confirmed site/service, user corrections, turn order, pending question, and case reference. Add a separate semantic session index for searching long conversations and producing traceable handoff summaries. Its value is demonstrated on a multi-turn scenario that cannot be resolved from the latest message alone; compare with ordinary recent-context memory.

Memory records carry speaker, turn ID, timestamp, trust class, original span, and policy snapshot if applicable. Trust classes distinguish caller assertion, staff case response, generated draft, verified released answer, and audited action result. Search results must preserve those labels. A caller's “your fee is zero” remains a caller assertion, however often repeated or highly ranked.

Index the text actually released, with interruption status, instead of treating every draft as something the caller heard. If partial playback cannot be mapped precisely to words, record that uncertainty. Summaries cite turn IDs and unresolved questions; a summary is not a replacement authority source. Check that a fabricated summary fact cannot authorize speech.

Session cleanup and retention are explicit. For the public demo, synthetic fixture traces may persist; arbitrary visitor speech is transient unless the visitor opts into retention. Redact identifying fields from staff/evaluation exports. For real visitor input, ask for retention consent before persisting a staff case; otherwise offer a transient summary and accurately state that no durable case was created. Synthetic fixture cases may persist by design. Deletion removes associated memory and case text subject to the explicitly disclosed audit retention policy; do not promise immediate deletion from immutable exported artifacts. A policy refresh must invalidate dependent cached decisions; cache keys include normalized claim/context, snapshot, and verifier version. A session cannot query another session's memory by supplying its ID.

Package a narrow `verify_unit(candidate, context, snapshot) → decision` core plus text-stream/speech-boundary adapter. Provide one real LiveKit integration and a second standalone streaming-agent example using the same package. Keep provider selection outside the verifier. Define cancellation, timeout, sequence, and evidence interfaces; include a runnable fixture without credentials and a documented real-provider path. The no-credential fixture is not represented as the deployed live agent.

Moss-specific hydration/session capabilities must be verified against the pinned SDK before use. Existing docs establish retrieval/session primitives, not this application's semantics. The committed speech control path is the documented LiveKit text-to-speech pipeline with Moss retrieval and the application-owned gate.

## 14. Research and evaluation depth

### Dataset program

Beyond the starter suite, plan a primary 2,000-case independently reviewed candidate dataset: 500 development, 500 calibration, 1,000 locked test cases. Balance primary verdict categories in the test set at 400 supported, 250 contradicted, 200 insufficient/unresolved/unsupported, and 150 conflicting. Report finer subcategories and language complexity rather than hiding them in aggregate counts.

Use at least six fictional sites, multiple services, and several historical policy releases. Split by policy/scenario family as well as paraphrase; reserve unseen sites and policy changes for test. Cover each original claim family, semantic statements, and mixed typed/semantic sentences. Fixture generation can be assisted, but the verifier must not generate its own expected labels. Two reviewers independently label the locked set; adjudicate disagreements and preserve their original judgments. Label quality matters more than mechanical case count; disputed cases remain visible.

Add 200 multi-turn task scenarios that exercise clarification, site changes, contradictory caller assertions, policy revocation, actual case resolution, and interruptions. Distinguish scripted conversation fixtures from natural human conversations. Add randomized token/chunk-boundary tests, property-based state-machine tests, and mutation tests that deliberately remove authority checks, skip clauses, or release cancelled work. Tests should fail for those mutations. A large dataset without boundary tests is insufficient.

A separate second-domain pack contains 400 cases: 100 development, 100 calibration, 200 held out. Use fictional insurance servicing documents with deadlines, policy limits, exclusions, and required evidence; do not perform real underwriting or eligibility decisions. Report zero-shot transfer, configured domain-pack transfer, and any code/calibration changes separately. A new schema and templates mean configured portability, not zero-change generalization. Test transfer first with the shared release/authority core unchanged. If findings require a shared-core correction, version it, report the change as adapted transfer, and rerun both domains; do not preserve a bug to claim portability.

### Comparative experiments

| Experiment | Compared systems | Question answered |
|---|---|---|
| Fixed-candidate factual checking | Typed only, typed+semantic, one reproducible alternative output verifier | Does semantic depth improve useful coverage without unacceptable new escapes? |
| End-to-end conversation | Ordinary RAG, stronger-prompt RAG, templates, full Hesitate | Does the caller complete the task correctly? |
| Authority ablation | Full model versus no authority/version/conflict checks in isolated test mode | Which failures require more than retrieval or NLI? |
| Retrieval ablation | Moss, exact/keyword, local vector search, Chroma, pgvector, Pinecone | What are accuracy, warm/cold latency, update, memory and operational tradeoffs? |
| Session-memory ablation | Recent context only versus provenance-tagged session retrieval | Does memory help long-dialogue/handoff tasks without contaminating policy? |
| Update lifecycle | Baseline approved-answer maintenance versus versioned publication/regression flow | Does a policy owner complete updates accurately with less rework? |

Never run disabled safety ablations in public normal mode. Match generation inputs for gate experiments and label workload differences in product experiments. Use equivalent filtering, index size, text/vector inputs, top-k, and embedding models where supported. Separate raw search from query embedding and total verifier time. Where APIs/features differ, report the difference rather than manufacturing an apples-to-apples claim.

Use a real curated workload for quality results. Separately use scale fixtures at 100, 1,000, and 10,000 policy records and declared concurrent-call loads for performance; label synthetic scale data and do not count repeated templates as independent correctness evidence. Measure index build/load/update time, memory, cold starts, resource contention, tail latency, and cost. Do not choose a distant hosted region to force a result. Record tested configurations and unsuccessful runs. If a backend is unavailable, mark that experiment incomplete rather than substituting a sleep or inventing data.

Select the alternative verifier using official documented support for output verification; run its comparable mode, including buffering if required. NeMo provides such a baseline family, but support differs by library/engine/version. See [current output streaming documentation](https://docs.nvidia.com/nemo/guardrails/latest/configure-guardrails/yaml-schema/streaming/output-rail-streaming). Pin the tested configuration and report configuration work, not just package import.

### Results and uncertainty

Report applicable-evidence recall, fact extraction coverage, missed propositions, verdict confusion matrices, false releases, false suppressions, correct corrections, complete task success, escalation correctness, policy-update errors, and cross-session leakage. Separate typed, semantic, mixed, and shifted-domain results. Correct support with irrelevant answers is not task success.

Provide uncertainty intervals and sample sizes; when cases share templates/sources, use group-aware uncertainty estimates or disclose dependence. No finite result supports “cannot hallucinate.” Time first useful content, full answer, clarification, correction, and interruption stop separately. Compare fixed-stream replay with real calls; replay isolates runtime overhead but omits generation/ASR variability.

All experiment scripts emit a manifest with corpus/dataset hashes, source revision, hardware/region, SDK/model versions, configs, seed where meaningful, timestamp, failures, and raw event paths. Keep dev/calibration/test separation enforceable in the harness. Provide one command per suite plus a report build that consumes existing artifacts without rerunning paid calls. Never embed credentials in manifests.

## 15. Reliability, security, and release mechanics

The speech unit state machine is `buffering → complete → verifying → approved/replaced/declined → queued → playing → finished`, with cancellation/error terminal branches. One ordered release queue prevents later statements overtaking an unresolved earlier unit. All transitions include session, turn, unit, decision, and snapshot IDs. Duplicate completion callbacks are idempotent. Interruption clears pending generation, verification, and queued audio; already-played audio is recorded, not erased.

Fault tests cover partial tokens, malformed Unicode, decimals, abbreviations, long unpunctuated output, stream disconnect, parser/NLI timeout, missing model, index load failure, worker termination, TTS failure, duplicate events, staff-save failure, and policy revocation at every release transition. Warmup cannot bypass readiness. Dependency errors produce distinct operational reasons while caller language remains understandable.

Instrument active sessions, queue depth, gate-stage latency, decision reasons, resource usage, dependency status, and failed case persistence. Use ordinary structured logs and a small health/status view. Start with one service and durable persistence supporting the actual concurrency model; choose deployment topology based on measurements. If NLI blocks voice processing, move it to a bounded worker pool and measure the scheduling cost. Do not run unbounded per-claim parallel requests.

Define explicit deployment limits from load tests and provider quotas; test overload rejection and recovery. Restore a policy release, staff case, and evaluation manifest from backup and verify referential integrity. Public demonstration resets operate only on isolated fixtures. No arbitrary file paths, cross-session IDs, or document content may reach privileged operations unchecked.

Security verification focuses on real surfaces: staff authorization, publisher permission, upload parsing, prompt injection in documents and memory, secrets, session isolation, and retained records. Avoid broad compliance claims. Published source documents and recordings require clear provenance and permission; synthetic artifacts remain labeled.

## 16. Work packages, ownership, and dependency gates

These packages preserve full scope. Assign actual helpers rather than assuming unlimited people. Contributor arrangements must comply with the confirmed competition's team/ownership rules; “help available” does not establish eligibility. No actual contributors beyond Ashraf are assumed in the tracker.

| Package | Owner role to assign | Contract and evidence | Dependencies |
|---|---|---|---|
| W0 Contracts | Ashraf/integration lead | Versioned fact, snapshot, candidate, decision, audio and case schemas; shared fixtures | Confirmed Moss target; domain contracts |
| W1 Domain/user evidence | Product/domain lead | Policy sources, interview records, labeled claim families, task scripts | W0 |
| W2 Policy lifecycle | Policy engineer | Ingestion, review, authority, staging/activation/revocation/rollback tests | W0; W1 fixtures |
| W3 Verification | Verification engineer | Typed routes, decomposition/completeness, calibrated NLI, correction checks | W0; W2 interface |
| W4 Voice runtime | Voice engineer | Sole TTS boundary, ordered release, cancellation and playout evidence | W0; W3 interface |
| W5 Staff product | Product engineer | Access-controlled policy/inbox/history views and resolution workflow | W0; W2/W4 events |
| W6 Evidence | Evaluation lead | Independent labels, test isolation, all baselines/ablations, raw reports | W0; integrate W2–W4 |
| W7 Portability | Integration engineer | Second-domain pack and second-agent integration | Stable W2–W4 contracts |
| W8 Operations | Reliability owner | Deployment, isolation, load/failure recovery and cost evidence | First integrated slice |
| W9 Story/review | Ashraf plus independent reviewer | User-task study, short/full demos, source/setup/PRD, final attack | Verified outputs from all |

A helper can own multiple packages; these roles are not a requirement for a ten-person team. Parallel agents can review schemas, construct independent fixtures, and work on isolated modules. Shared interface changes require fixture updates and integration-owner review. UI can start against contract fixtures but is not complete until connected to live state. No late merge of independently invented authority semantics.

Gates: G0 confirmed Moss target, registration/contributor checks, and contracts; G1 correct policy→candidate→audio slice; G2 complete typed/semantic and full policy coverage; G3 publication→case→resolution lifecycle; G4 memory/portability and concurrent deployment; G5 independent comparative evidence; G6 user tasks, artifacts, and final adversarial review. Packages overlap where dependencies permit. G1 is a foundation, not the intended final submission.

If a gate fails, report its cause, affected downstream packages, owner, next experiment, and impact on submission readiness. Add help or repair the design; do not quietly relabel unfinished scope “future work.” Official dates are tracked separately from engineering estimates. Before any deadline, report the actual release state, not assumed completion.

## 17. User evidence and layered demonstration

Obtain three distinct kinds of evidence: problem interviews with relevant operators/builders, task-based tests of policy publication and case resolution, and blind listening comparisons. Initial recruitment targets: three relevant stakeholder interviews, five observed product-task sessions, and ten listeners on randomized paired clips. These are recruitment targets, not significance guarantees. Report actual participation, expertise, sampling limits, and nonresponses.

Task scripts: publish a site-specific change without affecting another site; diagnose a refusal; resolve a conflict through review; complete a multi-question call; interrupt a pending answer; locate the version authorizing an earlier answer. Capture success/failure, assistance needed, elapsed time, and changes made after observation. Compare with the ordinary policy/FAQ workflow where possible. No fabricated quotes or ROI extrapolation.

Build three presentation depths:

- **Short submission video:** one unmistakable catch before speech, a useful conversation, and the conflict→staff resolution→new answer loop, then measured evidence. Use roughly three minutes as an editorial target; the inspected Moss pages do not establish a three-minute maximum. Check the submission form for any format/size limits. Clearly label injection, time cuts, and replay.
- **Interactive judge walkthrough:** source review, semantic claim, policy revocation during a call, interruption, provenance inspection, case resolution, and second-domain example. Suggested questions remain editable; normal generation stays available.
- **Technical evidence package:** full uncut recorded runs, independent results, errors, source manifests, component ablations, portability log, and reproducible scripts. A short video does not need every chart, but the evidence must exist.

The most valuable advanced demonstration is a changed policy taking effect correctly while preserving the history of what authorized an earlier statement. Combine this with a semantic claim that cannot be reduced to one number and a resolved operational case. That demonstrates depth across reasoning, state, and product outcome.

Keep the earlier three-minute script as an introductory outline; incorporate the completed operational loop rather than using the entire middle for architecture. No unsupported claim that this exact mix guarantees victory. Explain where simpler templates win and where the full workflow measurably helps.

## 18. Full-depth acceptance and final adversarial pass

Completion requires every Section 9 capability, all W0–W9 deliverables, the competitive/customer protocols in Sections 19–22, published experiment statuses, and the confirmed event's mandatory artifacts. Documentation length or a large architecture does not satisfy a capability. Record code paths, runnable checks, deployed interactions, and evidence URLs for each. An unrun experiment is incomplete, not a favorable assumed result.

Attack the final implementation from five perspectives: a policy owner maintaining changing instructions; a caller asking ambiguous compound questions; an engineer integrating a second agent; an operator handling failures and revocations; and a judge comparing the simplest competing solution. Use independent reviewers with distinct tasks. Resolve material findings and rerun affected evidence; do not repeat unchanged suites ceremonially.

Specific release questions:

1. Can a claim from the wrong site, stale policy, caller memory, or revoked record reach speech?
2. Can a true clause, favorable NLI score, or correction hide another unsupported proposition?
3. Can cancellation, duplication, or concurrent publication make the trace disagree with released audio?
4. Does staff resolution actually persist and affect subsequent calls only through proper review?
5. Does the full workflow improve useful task completion, policy maintenance, or integration over templates and stronger RAG?
6. Does the second-domain result honestly separate unchanged core, configuration, and code changes?
7. Can a first-time user understand the value and use the deployed flow without a narrated rescue?
8. Are performance, costs, failure rates, and measured limitations reproducible and fairly compared?

This is the intended high-depth submission. Keep its breadth while implementing it with disciplined interfaces and proof. Any remaining first-place assessment must be based on the actual full product and competing evidence, not confidence in the plan alone.

## 19. Establish a defensible reason to choose Hesitate

**Planning-only authorization:** this amendment specifies future experiments, acceptance gates, and submission strategy. It does not authorize starting implementation, recruiting participants, placing calls, publishing, or submitting. No planned outcome below is an observed result.

The competitive thesis is: **a voice-agent operator can maintain changing policies, prevent selected unsupported statements from reaching speech, and resolve exceptions with an inspectable history—without sacrificing useful conversation.** This is a hypothesis to test, not submission copy to publish before evidence exists.

Name the initial adopter precisely: an operator or implementer already responsible for a generative clinic-information agent and its policy updates. A clinic with a small static FAQ may prefer templates. Test both groups and do not conceal that distinction. The initial adoption path is adding the gate to an existing compatible text-to-speech pipeline, importing reviewed policy, and using the case workflow for exceptions. A second reusable integration and measured setup work demonstrate whether this path is credible.

### Strongest competing solutions

Expand the existing comparison to include a well-maintained approved-answer system and a strong existing output-guardrail configuration, not just naive RAG. Give each system the same approved sources, effective dates, scopes, and access to structured facts. The template baseline may use a capable intent router, clarification questions, and a basic staff-case workflow. The guardrail baseline may use its supported fact-checking and buffering features. Record all configuration and tuning effort. Do not attribute a benefit to the gate if the baseline was denied the metadata or workflow producing that benefit.

A competent reviewer should inspect baseline configuration before locking evaluation. If an existing tool can implement the whole workflow comparably, report the integration/maintenance difference rather than falsely claiming absent functionality. Package import, intentionally weak prompts, distant server placement, stale baseline data, or a missing baseline exception path do not establish superiority.

Use three workload strata, reported separately:

1. **Static approved facts:** direct and paraphrased questions with sufficient context. Establish whether added verification imposes unnecessary friction.
2. **Changing and conditional policies:** site-specific exceptions, temporal boundaries, urgent revocation, and compound questions. Measure the errors prevented and the maintenance work required.
3. **Operational exceptions:** missing context, source conflict, case-specific staff response, reviewed amendment, and subsequent correct calls. Measure task completion and accurate status reporting.

Weight an overall score only using a declared distribution justified by stakeholder observations. Until such evidence exists, report per-stratum results and an explicitly synthetic balanced aggregate. Do not choose weights after seeing where Hesitate wins.

### Preregistered primary comparison

Before the locked evaluation, create an experiment protocol naming the hypothesis, primary measure, data split, baseline configuration, acceptable error/latency bounds, exclusion rules, analysis method, and reviewer. Preserve its hash with the results. Exploratory findings may motivate a later fresh experiment; they cannot retroactively become the original primary result.

Primary product measure: **correct complete task outcome**, including all requested answers or a properly created/resolved exception, without an unsupported spoken fact or a false action-status claim. A refusal alone is not task completion when the question is answerable. Staff intervention, elapsed time, and caller turns are recorded, not hidden inside “success.”

Secondary measures: unsupported facts actually released, policy-update errors, operator active time, clarification/escalation burden, integration effort, resource cost, and first-useful-answer latency. Count source authoring, structured-fact review, baseline configuration, and labeling work in maintenance/setup comparisons. Expensive manual curation cannot disappear from the claimed benefit.

Proposed internal competitive targets, to finalize with stakeholders **before** the locked run:

- At least a 10-percentage-point improvement in correct completion on the changing-policy/exception workload over the strongest baseline, **or** at least a 20% reduction in operator active time on equivalent correctly completed maintenance tasks.
- No observed increase in unsupported spoken facts on the matched evaluation; report paired differences and uncertainty, not just this pass/fail statement.
- Static-workload correct completion within 5 percentage points of the strongest baseline, with the full per-route response-time budget from Section 5 reported.
- No critical authority, cross-session, cancellation, or false-action-status failure in the deterministic regression suite.

These are decision thresholds, not predictions, validated clinical standards, or permission to hide smaller useful effects. Use paired/group-aware intervals to judge how uncertain an apparent advantage is. If the sample cannot distinguish improvement from noise, call the result inconclusive. A point estimate exceeding a target is not alone sufficient for a strong superiority claim.

If Hesitate fails to establish additional value, keep the full scope and diagnose the mechanism: parsing loss, excess clarification, cumbersome policy review, integration cost, or a genuinely equivalent competitor. Improve the failing workflow, retest with new held-out tasks, and update the competitive claim. Do not respond by adding unrelated capabilities, weakening the baseline, or silently dropping a required component. If equivalence persists, explicitly report that the winning thesis remains unresolved; no honest plan can guarantee eliminating every reason to prefer a competitor.

## 20. Customer evidence that changes the product

Extend Section 17's recruitment targets with a concrete evidence protocol. Plan interviews with both clinic operations staff and voice-agent implementers. Ask for a recent policy-change/incorrect-answer incident, the current workaround, who maintains the source, how an exception is resolved, and what adoption would require. Avoid leading questions such as “Would a hallucination blocker help?” Distinguish firsthand examples from opinions and hypothetical interest.

For every material assumption, record: source role, firsthand/hypothetical status, anonymized observation, current workflow, implication for a specific capability, and what would falsify the assumption. An interview is useful when it confirms, rejects, or changes a decision—not merely when someone compliments the demo. Do not request real patient information to validate the workflow.

Plan observed tasks with counterbalanced system order so learning does not always favor Hesitate. Use equivalent task variants rather than letting a participant repeat an already-solved case. Record time spent understanding the tool, source preparation, execution, errors, moderator assistance, and recovery. Freeze the task script before the comparison; keep exploratory usability sessions separate from the final evaluation.

The evidence package should include at least one actual before/after product decision: observed confusion or workflow failure, resulting design change, and a subsequent comparable task result. If relevant users cannot be recruited, label all proxy evidence and leave the customer-validation gate incomplete. Additional fictional personas cannot replace it.

Plan an adoption test with an independent developer: given the package and documentation, integrate the gate into the second compatible agent without author assistance. Record time, errors, changed files, and intervention. A working example maintained by the original author does not by itself prove integration usability. Request a specific next-step commitment only during later authorized user research; do not interpret interest as adoption or revenue.

## 21. Judge objections mapped to visible evidence

This matrix is the acceptance contract for the story. Each response requires a real artifact, not a rehearsed unsupported answer. Assign an evidence owner in W1/W6/W9. Until generated, the status of every artifact is **pending**.

| Credible reason to choose another project | Evidence required to address it | Where judges should encounter it |
|---|---|---|
| The problem is hypothetical | Firsthand workflow observation and the resulting product decision; validation limitations | Opening problem statement and linked user-study note |
| Templates already solve this | Fair approved-answer baseline with matched metadata and exception handling; stratum-level results | Main comparison and full baseline protocol |
| Existing guardrails already do this | Reproducible strong guardrail configuration; measured workflow/integration difference | Prior-art section and evidence page |
| The model only fails because you sabotaged it | Separate natural-generation runs, fixed-candidate experiments, and visibly labeled injection | Labels during the demo and raw run manifest |
| It refuses too much to be useful | Complete multi-question conversation and completion/escalation denominators | Audible live sequence and results |
| It is a benchmark with no product | Policy publication → conversation → staff resolution → approved update → next-call outcome | Main product demo |
| Moss is decorative | Real Moss policy retrieval on the voice verification path; matched ablation and user-visible contribution | Moss runtime trace, latency results, and architecture |
| Fast search hides slow conversation | Full end-of-speech-to-useful-answer timing, semantic/typed tails, interruption behavior | Results and uncut recording |
| It checks one number but misses meaning | Negation, conditional exception, mixed sentence, scope and semantic examples | Judge-controlled scenarios and failure taxonomy |
| Policy updates make it inconsistent | Historical source trace, ordinary snapshot behavior, revocation race test and known in-flight limit | Interactive walkthrough and technical evidence |
| Staff handoff is a fake message | Persisted case, actual state transition, scoped resolution and publication audit | Main operational loop |
| It only works on one staged corpus | Unseen policy families, second-domain transfer breakdown, independent integration attempt | Portability evidence |
| The public app will fail when tested | Fresh-browser verification, bounded concurrency, truthful degraded states and judging-access plan | Deployed product and setup/status instructions |
| The impressive claims are unsupported | Reproducible artifacts, published counterexamples, uncertainty and measured scope | Evidence ledger linked beside each claim |

Create a compact evidence index with links grouped by these questions. A judge should reach a specific proof in one click rather than search a large repository. The index is navigation, not another product dashboard. Show actual status when an experiment or capability remains incomplete.

## 22. Competitive readiness review and submission decision

Maintain three separate verdicts: **technical correctness**, **customer/competitive advantage**, and **event/submission fit**. A clean technical plan cannot imply the other two are clean. Do not average a mandatory failure away with excellent scores elsewhere. The overall readiness verdict cannot be stronger than an unresolved mandatory blocker.

Before final endorsement, have independent reviewers compare the deployed product, evidence package, and strongest baseline, with the order randomized where practical. Give each reviewer the same task brief and official rubric. Ask for their preferred solution and the strongest reason to reject Hesitate before explaining the intended pitch. Record objections, evidence they inspected, and whether the objection was resolved by a product change, better proof, or clearer presentation. Unresolved objections stay in the tracker.

Use a simple internal rubric: 0 = missing, 1 = asserted, 2 = demonstrated once, 3 = independently reproduced, 4 = demonstrated comparative advantage where applicable. Score problem relevance, complete workflow, verification depth, usability, comparative evidence, sponsor contribution, reliability, and presentation. These are internal evidence levels, not official judging scores or a mathematical estimate of winning. Qualitative user observations do not become statistically proven market demand at level 4.

A strong-contender endorsement requires the full Section 9 capability contract, completed comparative/customer protocols, no unresolved critical technical or eligibility finding, accessible working submission artifacts, and a defensible answer to the leading baseline objection. If evidence is mixed, state exactly where the advantage exists. If only the plan exists, the verdict remains “planned, not demonstrated.”

**Event fit:** Moss is confirmed. Section 23 maps the full plan to its published themes, rubric, and mandatory artifacts. Administrative registration/contributor checks and implementation evidence remain pending; target uncertainty is no longer a blocker.

The desired result is to remove every material, addressable weakness we can identify. Judges can still prefer a different problem or an exceptional competing implementation. Preserve ambition without promising control over those unknowns. Further improvement should address observed objections and results while completing the full-depth target—not manufacture confidence through more feature names.

## 23. Moss alignment contract — confirmed target

Sources rechecked September 13: [official overview](https://yc-fall-2026-x-moss.devpost.com/), [rules](https://yc-fall-2026-x-moss.devpost.com/rules), and [resources](https://yc-fall-2026-x-moss.devpost.com/resources). The proposal directly combines the overview's real-time voice and agent reliability/security/evaluation themes. Explain that connection in the PRD; do not claim endorsement or investment by YC.

### Make Moss's contribution explicit

The deployed default retrieval backend is Moss. Chroma, pgvector, Pinecone, and local alternatives are experimental comparators, not dependencies required to run the submitted agent. An ordinary durable store may support cases/authentication without replacing Moss's retrieval role.

Moss retrieves applicable candidate evidence for free-form questions/claims; the exact authority map validates scope, version, and conflicts. Preserve this division in code, diagrams, and explanations: fast similarity search is not factual verification. Session retrieval supports long-dialogue context while remaining separate from authoritative policy.

For a demonstrated uncached live turn, show actual Moss query input, corpus release, returned source IDs, retrieval timing, the downstream decision, and eventual approved speech. Run the measured comparison with the same candidate stream and record both retrieval and full response differences. Cache hits are legitimate but identified; do not present them as fresh measured search.

The product claim to establish is that local retrieval makes repeated policy checks/context access responsive enough for this useful voice workflow. Report typed, semantic, and complete-turn latency separately, including embedding, buffering, and cold-start costs. If Moss only improves search and total latency barely changes, state that and investigate the bottleneck. Do not assign Moss credit for deterministic comparison, fabricate a remote delay, or claim the system is impossible with other local retrieval. A nominal import is insufficient to satisfy this plan's integration gate.

### Rubric-to-delivery mapping

| Dimension | Main judge-facing proof | Supporting depth |
|---|---|---|
| Product/UX, 35% | Useful conversation and policy-conflict-to-resolution loop | Observed user tasks, maintenance comparison, coherent staff workflow |
| Technical, 30% | Correct before-speech decision linked to current evidence | Typed/NLI coverage, revocation, cancellation, source lineage, portability |
| Speed, 20% | Visible measured Moss contribution and full response latency | Backend parity, cold/warm tests, update/load/resource measurements |
| Demo, 15% | Clear problem, real interaction, source-backed correction, measured outcome | Uncut runs, evidence index, reproducible setup and failure disclosures |

Retain all full-depth capabilities. Give the short video a clear voice/retrieval narrative; policy administration and benchmarks support that narrative rather than obscuring it. A larger evidence package remains accessible for technical inspection.

### Mandatory artifact ownership

| Deliverable | Planned artifact | Acceptance |
|---|---|---|
| Source repository | GitHub repository plus README/setup | Source present, pinned environment, required credentials documented, clean setup works |
| Working deployment | Public agent URL | Fresh browser completes live Moss-backed workflow; replay visibly distinct |
| Architecture diagram | `docs/architecture` artifact | Retrieval, authority map, gate, speech boundary, memory, and state flows accurately labeled |
| PRD | `docs/PRD.md` | Problem, intended users, theme fit, solution, requirements, success criteria and limits |
| Demo video | Accessible video URL | Working product and actual Moss contribution clearly shown |

These paths and URLs are planned artifacts, not files already built. W9 owns packaging; W2/W3/W4/W6 provide verified diagram and performance evidence. The official resources link the [HiDevs event page](https://app.hidevs.xyz/hackathons/yc-fall-2026-moss-zero-latency-builder-sprint); its authenticated submission form was not inspected. Register and submit through HiDevs as required, then verify any additional form instructions. Retain a receipt.

Team participation is limited to solo or two members under the published rules. W0–W9 are work responsibilities, not ten authorized entrants. Record who the actual contributors are and resolve any helper arrangement outside the published team model with the organizer before relying on it; do not assume an unlimited human team is permitted. This does not reduce the requested technical scope.

**Plan-alignment verdict:** aligned with the published Moss themes, judging dimensions, and specified deliverables. This is not confirmation that registration, contributor eligibility, runtime performance, or submission completion has been verified. No implementation is authorized by this alignment check.
