# Hesitate

A clinic voice agent that checks its own facts before it says them out loud.

The problem: a voice agent can be handed the right documents and still say the wrong thing.
Standard retrieval grounds what the model reads, not what it says — so if an old prep sheet is
still sitting in the search index next to the current one, the model can happily repeat the stale
number with total confidence. Hesitate catches that before it reaches the caller's ears, not after.
Built for the YC Fall 2026 × Moss: The Zero Latency Builder Sprint.

`PLAN.md` has the full spec this repo implements. `COMPETITION.md` is the running log of what's
actually built and proven versus what's still aspirational — including the mistakes found along
the way and how they got fixed.

**Demo video:** https://www.youtube.com/watch?v=l0ZynfcKPm0
**Live:** https://hesitate-v2.onrender.com/call.html

## What it actually does

Every sentence the agent is about to speak gets checked against the clinic's current policy before
it hits text-to-speech. If the sentence matches policy, it's spoken as-is. If it contradicts
policy — say, the model says "fast for 12 hours" but the clinic's real answer is 8 — the wrong
sentence is thrown out and replaced with a correction pulled straight from the real record, not
from asking the model to try again. If there's nothing on record to check the claim against, the
agent says it doesn't know rather than guessing.

Moss is what makes this possible in practice: the lookup happens in-process in single-digit
milliseconds, so the check can sit inside a live phone call without the conversation stalling out
waiting for it.

## What's real right now

- Live and working: `/gate/demo` runs the actual verification logic, `/token` issues real LiveKit
  room tokens, `/call.html` is a real browser client you can talk to.
- The whole pipeline has run live, end to end, with a real person talking into a real microphone:
  speech in, a checked (and sometimes corrected) reply out.
- Everything behind it is a real account, not a mock: Moss, LiveKit, Deepgram, Groq, ElevenLabs.
- The agent's voice worker currently runs from a local machine rather than the free-tier deployment
  — the reasoning is written up honestly in `COMPETITION.md` instead of hidden.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the tests and benchmarks

```bash
source .venv/bin/activate
python -m pytest tests/ -q                     # full suite: typed + semantic routes, live-service tests skip without API keys
python -m bench.run_benchmark                  # typed route: confusion matrix + latency
python -m bench.run_semantic_benchmark         # semantic route: confusion matrix + latency
```

All three run offline except for a one-time model download the first time you run the semantic
benchmark or tests (`cross-encoder/nli-deberta-v3-xsmall`, about 70MB from Hugging Face).

## How the repo is laid out

```
agent/gate/     the verification logic itself: pulling out claims, resolving them against policy, correcting or declining
agent/voice/    the LiveKit agent — wires speech-to-text, the LLM, the gate, and text-to-speech together
agent/retrieval/ the Moss client and the adapter that turns retrieval hits into resolvable records
corpus/         synthetic clinic policy documents, including a deliberately stale one to prove the catch works
bench/          benchmark scripts with pre-declared expected answers — every number in the docs traces back here
tests/          the pytest suite
web_api/        the deployed FastAPI service and the browser call page
docs/           architecture diagram, PRD, the demo video script
COMPETITION.md  the honest running log — what's proven, what's not, what broke and how it got fixed
PLAN.md         the full spec this repo builds toward
```

## One hard rule

Every document in the policy corpus is made up. No real clinic, patient, or insurer data is used
anywhere in this repository — see `corpus/provenance.md` for exactly what's synthetic and why.
