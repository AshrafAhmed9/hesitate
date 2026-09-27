# Finale Q&A

Likely questions, short answers, and where the code backs each one up.

**Why not just ask a second model to check the first?**
It adds a slow, non-deterministic call inside a live phone conversation, and a model can be wrong
the same way the first one was. The check here is typed: extract the claim, find the policy record
for that fact, compare values. It takes under a millisecond and gives the same answer every time.
Code: `agent/gate/extract.py`, `agent/gate/resolve.py`.

**How does it know which record is current?**
Records replace each other explicitly (`supersedes`) and have effective dates. It never picks by
similarity or by which document is newest. Two current records that disagree produce a CONFLICT
and a decline, not a guess. Code: `resolve.py` (`_drop_superseded`, the CONFLICT branch). The
policy desk shows this live.

**Isn't retrieval already the grounding?**
Retrieval decides what the model reads. It doesn't control what the model says. In the live test,
the stale 12-hour sheet ranked first, the model repeated it, and 6 of 20 answers were wrong.
Same model, same search results, gate off.

**What does it miss?**
Claims with no number or typed slot ("you'll get a text message"), and other domains' vocabulary
(the insurance corpus exposed this). They're in `docs/FAILURE_TAXONOMY.md` with causes. The design
choice: when the check can't parse a factual span, it declines rather than passes it
(`agent/gate/completeness.py`).

**What does the gate wrongly block?**
0 of 20 correct answers in the live run. The number is in `bench/results/live_ab.json`, next to the
wrong-answer count, because a gate that blocks everything would also score 0 wrong.

**Is the demo rigged?**
The stale sheet is planted, because real clinics have old sheets. Both modes use the identical
pipeline (same Moss top 3, same prompt, temperature 0); only the gate differs
(`agent/voice/hesitate_agent.py`, `gate_enabled`). The policy desk lets a judge change the inputs.
The A/B script's expected answers are declared before the run.

**What does Moss do here, beyond search?**
Two jobs. It retrieves the policy passages on every turn (about 7 ms, in process, so it fits inside
a voice call). And it's the live index the policy desk writes to (`add_docs`), so a policy change
shows up in the next call. Its role in the gate: the records Moss returns are the candidates the
check compares against.

**Why is this a company?**
Operators are liable for what their agents say (Moffatt v. Air Canada, BC Civil Resolution
Tribunal, Feb 2024). Any regulated voice deployment needs a layer that can refuse. There are no
customer interviews yet; the ruling is the market signal, not evidence of demand.

**What about NeMo Guardrails or similar output rails?**
Output rails exist. The difference here is checking against versioned, authoritative policy
records with explicit supersession, in milliseconds, without a second model. Not claiming nobody
else gates output.

**How would someone use it?**
The whole check sits at LiveKit's single `tts_node` boundary, so an existing LiveKit agent gets it
by subclassing `HesitateAgent`. The records and extractor are the domain-specific work.

**Why does the worker run locally?**
It crash-looped on Render's free tier every time (~512 MB). Documented in `COMPETITION.md`.
Everything else is deployed.

**Which part did you write / how does the check work?**
Say it in your own words: sentence in, pull out the number, look up the current record for that
fact, compare, speak or replace. Then point at `resolve.py`.
