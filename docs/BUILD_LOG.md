# Build log

What was built, what broke while building it, and how each problem was found and fixed.
Measured results are in `bench/results/`; known gaps are in `docs/FAILURE_TAXONOMY.md`.

## Live voice pipeline test (2026-09-13)

Ran a real LiveKit agent worker (`python -m agent.voice.entrypoint connect --room hesitate-demo`)
against a synthetic caller (`scripts/synthetic_caller.py`) publishing real, locally-synthesized
speech (macOS `say` + ffmpeg, zero cost, no human needed) into the room. This is the first live
test of the actual voice pipeline, not isolated unit tests.

**Confirmed real and working:** LiveKit room connection, token issuance, silero VAD loading, a real
Deepgram STT WebSocket connection established against the live project. GuardedTTS's dev-mode
silence path (no ElevenLabs calls made — confirmed by log absence and by the standalone tests).

**Found, not fixed: no transcript ever appeared** after the Deepgram connection, across multiple
runs and two distinct hypotheses tried:
1. AudioFrame byte layout — verified correct (nbytes=640 for 320 int16 samples, itemsize=2, format='h').
2. Identity collision across repeated test runs (reusing the same `synthetic-caller` identity) —
   retested with a unique UUID identity and a brand-new room name each run; same result.

Diagnostic detail for whoever picks this up next: the RoomIO's audio input always attaches expecting
`participant=null` (any mic source) and never logs re-binding to the real caller's identity; the gap
between the caller finishing speech and session close is consistently ~20-30s, which may point to
`AgentSession`'s `user_away_timeout` (default 15s) rather than genuine STT processing.

**Stopped here** — two real debugging attempts without a fix is the point to report rather than keep
guessing, per instruction. **Next step: test via `call.html` with an actual human + browser
microphone**, which sidesteps the synthetic caller's hand-rolled audio-publishing path entirely and
is the more likely path to actually work.

## Live voice pipeline: real root cause found, and a real deployment limit (2026-09-14)

Testing the deployed `call.html` from a real browser, nothing happened. The
actual root cause was much simpler than the transcript gap above: **no agent worker had ever been
deployed persistently.** Every prior live test ran `agent/voice/entrypoint.py` manually in a local
background shell and killed it afterward — the deployed web service only ever ran `web_api/main.py`
(FastAPI). This was fixed and then hit a second, real constraint:

1. Ran the worker as a subprocess of the `web_api` Render service, gated by an env var. It
   registered with LiveKit successfully — real progress — but immediately self-reported "full
   capacity" (load 0.98–0.99 against the default 0.7 threshold) purely from import/warm-up cost on
   Render free tier's fractional CPU share, so it never accepted a job. Fixed with
   `WorkerOptions(load_threshold=1.5)`.
2. The combined service then crash-looped (restarting every 60–90s). Split `sentence-transformers`/
   `torch` out into a new `requirements-deploy.txt` after confirming `agent/gate/semantic.py` (the
   only consumer of those packages) is never imported by the deployed agent or web app — only by
   tests. Crash-loop persisted.
3. Split the worker into its own dedicated free-tier Render service (`worker_service/main.py`,
   since deleted), so it wasn't sharing a container with FastAPI. Still crash-looped, now alone.
4. Tried disabling the worker's internal HTTP server (port 8081, unrelated to the app's web server)
   after seeing "Detected a new open port HTTP:8081" in Render's deploy log right as restarts
   started, on the theory that Render's port auto-detection was confused by two open ports. Checked
   `livekit/agents/worker.py` directly: `port=0` just means "OS picks a random port," not "disabled"
   — there is no way to disable that server in this library version. The crash-loop continued
   unchanged after this fix too, ruling the theory out.

**Four real attempts, all addressing plausible causes, none fixing it.** The honest conclusion:
Render's free tier (~512MB) cannot sustain deepgram + elevenlabs + groq + silero/onnxruntime loaded
together for more than about a minute, independent of memory trimming or container isolation. This
is a real resource ceiling, not a bug in this repo.

**Decision:** the agent worker is not
deployed on Render. It runs from a local machine (`python -m agent.voice.entrypoint start`) for
demos and the live finale. Paying for a bigger Render plan (~$7/mo Starter, 2GB RAM) was the
alternative and was declined in favor of staying on the free tier. The deployed web service
(`https://hesitate-v2.onrender.com`) still serves `call.html`, issues LiveKit tokens, and
demonstrates the verification gate against live Moss (`/gate/live-demo`) on its own — only the
voice worker itself needs to be started locally before a live call can be answered. This is an accepted
limitation, stated in the README and the PRD.

## Final build (2026-09-27)

- **Moss is in the live call.** Each turn queries the `hesitate-clinic` index (one document per policy sentence, top 3, about 7 ms) and the gate checks against the records those hits point to. The trace on the call page shows the hits, the draft, what was spoken and timings.
- **Live A/B** (`bench/run_live_ab.py`, `bench/results/live_ab.json`): 23 questions, real Moss and Groq, expected answers declared before the run. Without the gate 6 wrong answers reached the caller; with it 0; 0 correct answers blocked. Moss p50 6.6 ms, gate p50 0.25 ms, gate max 8.4 ms.
- **Closed the "why not just search the clean dataset" gap.** Raised in review: if a clean policy table exists, why let the agent read messy documents at all? Answer: the table is deliberately tiny (6 facts) and can't cover most of what patients ask (water while fasting, medication, parking, results). Added `corpus/patient_guide.py` — real clinic guidance with no `PolicyRecord` behind it — indexed alongside the policy docs (`scripts/build_moss_index.py`, 13 docs total). Added 4 questions to the live A/B that only that guide content can answer, to prove the gate lets real unstructured guidance through instead of declining it as an unverifiable policy claim. All 4 pass. In short: the table guards the few facts that hurt someone if wrong; the documents cover everything else; the gate is what tells the difference.
- **Mistake caught by that run:** after adding "a referral is required" phrasing to the extractor, the A/B flagged "No referral is needed" (correct) as wrong. Fixed with an explicit negative pattern; regression test added.
- **Gaps closed by probing phrasings a caller might plausibly use:** "half a day", "one day", "half an hour", "an hour early", "two hundred dollars", "a referral is required". Before the fix each produced zero claims and passed through. Tests: `tests/test_adversarial_phrasings.py`. The rewrites are limited to fasting and arrival phrases so unrelated sentences still pass.
- **Policy Desk** (`corpus/desk.py`, `/policy`, `/poison`, `/desk/reset`; enabled only with `HESITATE_DESK=1`): an approved change supersedes the current record and is added to Moss; an unapproved document is indexed but never becomes policy. Verified live: publish 10 hours, the model's stale 12 was corrected to 10; add a 16-hour document, the model said 16, the caller heard 10.
- **Bugs found testing repeated live calls:** every hangup threw `'bool' object can't be awaited` (a shutdown callback returned a bool instead of being awaitable), fixed in `agent/voice/entrypoint.py`. The agent took 20+ seconds to join because each call loaded the Moss index before joining; it now loads alongside session start and the voice detector is preloaded per worker process.
- **Dropped a flaky test:** a live Groq latency bound (<1 s, then <2 s) kept failing on network variance with nothing changed. The regression it guarded, reasoning effort reverting to default, is caught by the reasoning-token check instead.
