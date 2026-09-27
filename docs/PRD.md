# Product Requirements Document (PRD): Hesitate

## 1. Executive Summary
**Hesitate** is a real-time voice agent for healthcare administrative intake. Standard
retrieval-augmented (RAG) agents can confidently repeat outdated information. Hesitate adds a
mandatory **Verification Gate** that intercepts every sentence the model generates and checks its
factual claims against a live, versioned policy record, retrieved through **Moss**, before any audio
is synthesized. Patients should never receive an incorrect instruction about fasting, arrival,
insurance or cost.

## 2. Problem Statement
Clinic front-desk coordinators handle 60+ repetitive calls a day about administrative policy
(fasting duration, arrival times, insurance coverage). Standard RAG agents fail in three ways:
1. The model retrieves a stale document that was never removed from the index.
2. The model ignores the retrieved context and asserts a hallucinated figure.
3. The model picks one of two conflicting records by similarity rather than explicit supersession.

In healthcare, these errors lead to wasted appointments, patient frustration and administrative
liability.

## 3. Goals & Objectives
* **No wrong facts delivered:** no factual claim contradicting current policy reaches the caller.
* **Low latency:** verification overhead small enough for a live conversation.
* **Live policy authority:** staff can update policy mid-call with immediate effect.
* **Structural guarantee:** the gate is a hard boundary, not a best-effort check.

## 4. Target Users / Stakeholders
* **Primary:** clinic front-desk coordinators, accountable for patient instructions.
* **Secondary:** clinic operators deciding whether an automated voice agent is safe to deploy.
* **End user:** patients seeking accurate administrative information.

## 5. Functional Requirements

### 5.1 Voice Interaction & Processing
* **Real-time transcription:** caller speech to text with Deepgram STT.
* **Streaming response:** sentence-by-sentence generation with Groq (gpt-oss-20b) so each sentence
  can be verified before it is spoken.
* **Verified speech synthesis:** only approved or corrected text reaches ElevenLabs TTS.

### 5.2 The Verification Gate (Core Logic)
Every candidate sentence gets one of four outcomes:
1. **Supported:** the claim matches policy; the sentence is spoken as generated.
2. **Contradicted:** the claim is wrong; the sentence is replaced with a template correction filled
   only from the policy record's value.
3. **Unverifiable:** no policy exists for the claim; the agent declines and refers the caller to the
   front desk.
4. **Conflict:** multiple current records disagree; the agent declines rather than picking one.

* **Typed extraction:** routes for fasting duration, arrival offset, coverage, required documents,
  cost and appointment windows.
* **Untyped claims:** a separate, tested module using a local entailment model for claims not
  covered by typed routes (not yet wired into the live call path).

### 5.3 Policy Management (Policy Desk)
* **Live updates:** publish approved policies or drop unapproved documents.
* **Immediate sync:** uses the Moss SDK `add_docs` method; the next call uses the change.

## 6. Non-Functional Requirements
* **Latency:**
  * Moss retrieval: ~6.6–7 ms median.
  * Verification check: ~0.25 ms median, under 12 ms worst case.
* **Reliability:** no sentence can bypass the gate.
* **Resources:** the voice worker must accommodate VAD and streaming SDK memory needs.

## 7. System Architecture Overview
1. **Frontend:** vanilla HTML/JS client connects over WebRTC to LiveKit.
2. **Voice agent worker (local):** runs Silero VAD, Deepgram STT, Groq LLM and ElevenLabs TTS, and
   queries Moss on every turn.
3. **Verification Gate:** sits between the LLM and TTS.
4. **FastAPI backend (cloud):** issues tokens and hosts independent test endpoints.
5. **Moss:** managed semantic retrieval over the clinic's documents.

## 8. Tech Stack
* **Frontend:** vanilla HTML/JS, LiveKit JS SDK, WebRTC.
* **Backend:** Python, FastAPI, Pydantic.
* **LLM:** Groq (gpt-oss-20b).
* **Knowledge base:** Moss (managed vector search / semantic retrieval).
* **Verification model:** `cross-encoder/nli-deberta-v3-xsmall` via `sentence-transformers`.
* **Voice services:** Deepgram (STT), ElevenLabs (TTS), Silero VAD.
* **Deployment:** Render (web/API), local machine (voice worker).

## 9. Data Requirements
* **Policy records:** structured, versioned records with explicit supersession.
* **Claim extraction:** typed factual assertions.
* **Context retrieval:** live retrieval from Moss on every call turn (~7 ms).

## 10. API Specifications
* **`GET /gate/demo`:** runs the Verification Gate independently of the voice pipeline.
* **`GET /gate/live-demo`:** runs the gate against real, live Moss retrieval.
* **`GET /proof`:** serves the live A/B benchmark result.
* **`GET /token`:** issues LiveKit room tokens.
* **Moss SDK:** `query` for retrieval, `add_docs` for Policy Desk writes.

## 11. Security Requirements
* **Policy Desk access:** disabled on the public deployment; enabled only on the demo machine.
* **Transport:** caller audio over secure WebRTC.
* **Policy integrity:** explicit supersession, so only the current record is used for verification.

## 12. Deployment & Infrastructure
* **Web service:** FastAPI backend and frontend on **Render**.
* **Voice agent worker:** runs on a **local machine**. Deepgram, ElevenLabs, Groq and Silero VAD
  together exceed Render's free-tier memory.
* **Orchestration:** single FastAPI service.

## 13. Success Metrics
* **Wrong facts delivered:** 0 of 23 in the declared live benchmark (6 of 23 without the gate).
* **Correct answers wrongly blocked:** 0 of 23.
* **Latency:** median check overhead under 1 ms, excluding retrieval.

## 14. Timeline & Milestones
* **Complete:** live proof of concept on Render; stale-document failure reproduced and caught; live
  A/B benchmark; Policy Desk.
* **Planned:** wire the untyped-claim entailment route into the live voice path.
* **Planned:** interviews with clinic front-desk coordinators.

## 15. Open Questions & Risks
* **Local worker:** limits cloud-only deployment for now.
* **Coverage gaps:** claims without numbers ("you'll get a text message") and vocabulary outside
  the clinic domain are not yet covered (`docs/FAILURE_TAXONOMY.md`).
* **Validation gap:** no customer interviews yet.
