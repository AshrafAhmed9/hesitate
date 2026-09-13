# Video script draft — Hesitate

Mandatory submission deliverable (PLAN.md section 23: "demo video should showcase the working
product and explain the use of Moss"). This draft is built strictly from what `COMPETITION.md`'s
ledger currently proves — no staff-resolution loop, no policy-publishing workflow, no cross-domain
segment, because none of those are built yet. Update this script as more gets built; do not pad it
with unbuilt capability to hit a runtime target.

**Status:** draft only. Recording requires Ashraf's voice/presence for narration, and a real live
call (browser + microphone) for the voice-agent segment, which has not happened yet — see the open
gap in `COMPETITION.md`. Everything else below can be screen-recorded from already-working,
already-tested artifacts without waiting on that.

---

## Segment 1 — The catch (0:00–0:30)

**What to show:** the real live end-to-end finding, not a staged mockup.

Run `python3 -m pytest tests/test_end_to_end_live.py -v -s` on screen, or better, re-run the
underlying scenario live and narrate over it:

> "This clinic's policy says patients fast for 8 hours. An old prep sheet, still sitting in the
> index, says 12. Watch what a normal AI agent does with that."

Show the real Moss retrieval scores side by side (0.99 for the stale doc vs 0.975 for the current
one — the actual numbers from the live test, not invented ones) — this is the moment that earns the
whole premise: **the wrong document doesn't just exist in the corpus, Moss's own ranking prefers
it.**

> "A real Groq model, handed that passage, says exactly what you'd expect: fast for twelve hours.
> Hesitate catches it — in under ten milliseconds — and corrects it before anyone hears the wrong
> number."

Show the terminal output: `CONTRADICTED` → `Actually — 8 hours, per your prep instructions.`

## Segment 2 — How it works, briefly (0:30–1:00)

Show `docs/ARCHITECTURE.md`'s diagram for 5-10 seconds. One sentence of narration:

> "Every claim the agent generates is checked against a structured policy record before it reaches
> speech — not a similarity score, an exact comparison. If a stale record and a current one
> disagree, and neither explicitly supersedes the other, Hesitate doesn't guess — it declines."

Show the CONFLICT case from `bench/cases.py` briefly if time allows.

## Segment 3 — It's real, not a demo trick (1:00–1:30)

> "Every one of the accounts behind this is live — not simulated."

Quick screen flashes (2-3 seconds each): the Moss project dashboard, the LiveKit project, the
deployed URL `https://hesitate-v2.onrender.com/gate/demo` returning a real response with `curl` or
a browser, and the GitHub repo with its commit history showing real bugs found and fixed (the
missing-env-vars deploy bug, the completeness-check gap) — **this is stronger than hiding mistakes.**

## Segment 4 — [GAP — needs a real call] Voice, live (1:30–2:15)

**Cannot be filmed yet.** This is the one segment that needs Ashraf: open `call.html` on the
deployed URL, speak the fasting question into a real microphone, and let the audience hear the
agent's real voice response. If the underlying transcript gap (documented in `COMPETITION.md`,
2026-09-13) isn't resolved before recording, this segment cannot be shot as scripted — reprioritize
debugging that path, or restructure the video around Segments 1–3 and 5 only and disclose plainly
that the voice interface is still in progress.

## Segment 5 — The honest limits (2:15–2:45)

PLAN.md's own instruction: show what the system won't do, and say plainly what isn't finished.

> "This isn't finished. It catches numeric and categorical claims — fasting duration, cost,
> coverage, required documents. It doesn't yet catch every kind of vague claim a model might make,
> and we found and fixed one of those gaps ourselves, live, days before this video. We're not
> hiding that — the whole point of Hesitate is that hidden gaps are the problem."

## Segment 6 — Close (2:45–3:00)

> "Retrieval that's fast enough to check a claim before it's spoken, not just before it's
> generated — that's what Moss made possible here. Repo, deployed link, and full evidence log are
> below."

---

## What this script deliberately does NOT include

Per PLAN.md sections 9, 12, 17: the policy-publishing workflow, staff resolution/case inbox,
cross-domain pack, and multi-backend ablation are all real planned capabilities but none are built
enough to demo honestly yet. Adding them to the script now would mean either recording something
staged or padding runtime with slides instead of working product — both against the plan's own
rules. Revise this script once (and only once) those are actually working.
