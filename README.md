# Hesitate

A clinic voice agent's factual claims are verified against curated policy records **before** they
are spoken — not after, and not by a similarity score. Built for the YC Fall 2026 × Moss: The Zero
Latency Builder Sprint. See `PLAN.md` for the full specification and `COMPETITION.md` for the
evidence ledger tracking what's actually built vs. claimed.

## What's real right now

The verification gate: typed extraction → structured policy resolution → deterministic correction,
plus a standalone Tier 2 semantic route for nonnumeric claims. No voice pipeline, no live Moss
connection, no deployment yet — see `docs/ARCHITECTURE.md` for the exact status of every component.

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
