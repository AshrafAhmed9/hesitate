# Hesitate

A clinic voice agent that checks each sentence against the clinic's current policy before it says it.

In 2024 a Canadian tribunal held Air Canada responsible for what its website chatbot told a
customer about refunds ([Moffatt v. Air Canada](https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html)).
Voice agents now answer patients the same way, and search alone doesn't prevent it: if an old prep
sheet is still in the index next to the current one, the model can repeat the old number with full
confidence. Hesitate stops that sentence before it reaches the caller's ears.

Built for the YC Fall 2026 × Moss: The Zero Latency Builder Sprint.

**Demo video:** https://www.youtube.com/watch?v=l0ZynfcKPm0
**Live page:** https://hesitate-v2.onrender.com/call.html (needs the voice worker running; see below)

## The number

23 real questions, real Moss search, real Groq model, expected answers written down before the
run (`bench/run_live_ab.py`, results in `bench/results/live_ab.json`):

| | Wrong facts that reached the caller | Correct answers wrongly blocked |
|---|---|---|
| Ordinary retrieval agent | 6 of 23 | n/a |
| Same agent with Hesitate | 0 of 23 | 0 of 23 |

Moss lookup takes about 7 ms at the median. The check itself takes under a millisecond at the
median (about 8-12 ms worst case). The six wrong answers all come from the same place: the old
12-hour fasting sheet, which Moss ranks first for fasting questions.

Four of the 23 questions (water while fasting, medication, parking, getting results) have no
policy record behind them at all — they're only in the general clinic documents. The point of
including them: Hesitate only enforces the small set of facts that can actually hurt someone if
wrong. It doesn't try to turn every sentence a clinic might say into a structured record, and it
doesn't block the agent from answering things the policy table was never meant to cover.

This is 23 questions on a small clinic corpus, not a claim about every deployment. The gaps we
know about are in `docs/FAILURE_TAXONOMY.md`.

## How a call works

1. The caller asks a question (voice, or typed into the call page).
2. Moss returns the three most relevant policy passages, in about 7 ms. The model answers from them.
3. Each sentence the model writes is checked against the policy record for that fact, before it
   goes to text-to-speech. Matches are spoken. Contradictions are replaced with a correction built
   from the current record. Anything with nothing on record becomes "I'll check with the front desk."
4. The call page shows all of it: what Moss found, the model's draft (struck out if it was wrong),
   what was actually spoken, and the time each step took.

The call page has a switch to turn protection off. With it off, the same agent with the same
search results says "12 hours" out loud. That's the baseline the number above is measured against.

The **policy desk** on the call page (demo machine only) shows the check isn't hardcoded. Publish a
new fasting time and the next answer follows it, because the new record explicitly replaces the
old one. Drop in an unapproved document saying "16 hours": Moss finds it and the model repeats it,
but no approved record backs it, so the caller still hears the real policy.

## What's real

- Moss, LiveKit, Deepgram, Groq and ElevenLabs are all real accounts, not mocks.
- The whole loop has been run live with a real microphone.
- The voice worker runs from a local machine, not on Render. It crash-looped on the free tier on
  every attempt; the write-up is in `COMPETITION.md`.
- Not covered: claims with no number in them ("you'll get a text"), and vocabulary from outside the
  clinic domain. Both are listed with their causes in `docs/FAILURE_TAXONOMY.md`.

## Run the demo

```bash
bash scripts/demo.sh            # real ElevenLabs voice; SILENT=1 for silent dev mode
```

That restarts the worker, starts the web server on port 8000, resets the policy desk and opens
`http://localhost:8000/call.html`.

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
docs/           architecture, PRD, failure taxonomy
COMPETITION.md  build log: what broke during the build and how each problem was found and fixed
```

## One hard rule

Every document in the policy corpus is made up. No real clinic, patient, or insurer data is used
anywhere in this repository — see `corpus/provenance.md` for exactly what's synthetic and why.
