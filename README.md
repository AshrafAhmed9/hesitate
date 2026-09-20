# Hesitate

A clinic voice agent's factual claims are verified against curated policy records **before** they
are spoken — not after, and not by a similarity score. Built for the YC Fall 2026 × Moss: The Zero
Latency Builder Sprint. See `PLAN.md` for the full specification and `COMPETITION.md` for the
evidence ledger tracking what's actually built vs. claimed.

**Demo video:** https://www.youtube.com/watch?v=l0ZynfcKPm0

## What's real right now

**Live:** https://hesitate-v2.onrender.com — `/gate/demo` runs the real verification gate,
`/token` issues real LiveKit room tokens, `/call.html` is a browser client using the LiveKit JS SDK.

**Built and tested:** the verification gate (typed extraction to structured policy resolution to
deterministic correction, plus a standalone Tier 2 semantic route), the real Moss/LiveKit/Deepgram/
Groq integrations (all live-verified, not mocked), and HesitateAgent overriding LiveKit's
tts_node -- the actual interception point every generated sentence passes through.

**A real human has joined a call via browser and microphone** and the full loop has run live:
speech in, a verified (or corrected) reply out. The agent worker runs locally rather than on the
free-tier deployment -- see COMPETITION.md for why, and docs/ARCHITECTURE.md for the exact status
of every component, including bugs found and fixed along the way.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the tests and benchmarks

```bash
source .venv/bin/activate
python -m pytest tests/ -q                     # 20 tests, typed + semantic routes
python -m bench.run_benchmark                  # typed route: confusion matrix + latency
python -m bench.run_semantic_benchmark         # semantic route: confusion matrix + latency
```

All three should pass/complete with no network access required except the one-time model download
on first run of the semantic benchmark or tests (`cross-encoder/nli-deberta-v3-xsmall`, ~70MB from
Hugging Face).

## Repository layout

```
agent/gate/     the verification gate itself — schema, extraction, resolution, correction, semantic
corpus/         curated, synthetic PolicyRecord fixtures with a real supersession chain
bench/          pre-declared test cases and benchmark scripts — every published number traces here
tests/          pytest suite
docs/           architecture diagram, PRD
COMPETITION.md  evidence ledger — what's claimed vs. proven, updated as work lands
PLAN.md         the full specification this repo implements
```

## Hard constraint

All corpus documents are self-authored/synthetic. No real clinic, patient, or payer data is used
anywhere in this repository — see `corpus/provenance.md`.
