# Hesitate: Finale Guide

Your one document for today. Part 1 teaches you the project in plain words. Part 2 is the exact
6 minutes, word for word. Part 3 covers the questions judges will ask. Part 4 is the setup
checklist and what to do if something breaks.

Read Part 1 once, carefully. Read Part 2 out loud three times, standing up.

---

# Part 1: Understand the project

## The problem, in one breath

A clinic puts an AI voice assistant on its phone line. A patient calls and asks, "How long do I
fast before my blood test?" The right answer is **8 hours**. An old prep sheet still sitting in
the clinic's files says **12 hours**. The AI finds both sheets, picks the old one, and tells the
patient "12 hours" in a calm, confident voice. Nobody notices until the patient shows up hungry
for no reason, or worse.

This is real. In 2024, a Canadian tribunal ruled that **Air Canada** had to pay because its
website chatbot told a customer something that wasn't true about a refund policy. The airline
argued the chatbot was a separate thing and not its responsibility. The tribunal said no: if your
bot says it, you own it.

## What Hesitate does

Hesitate checks every sentence the AI is about to say **before it's spoken out loud**.

- If the sentence is right, it's spoken as-is.
- If it's wrong, it's thrown away and replaced with the correct answer.
- If there's nothing on record to check it against, the agent says "I'll check with the front
  desk" instead of guessing.

**The analogy:** a new receptionist who read every file in the building, including old ones,
with a supervisor standing behind them. Before each sentence leaves their mouth, the supervisor
checks it against the official rulebook and stops them if it's wrong. Hesitate is that
supervisor, and it takes about a quarter of a millisecond.

## The pieces, in plain words

| Piece | What it is | Its job here |
|---|---|---|
| **LiveKit** | Phone-call plumbing for the web | Connects your voice in the browser to the agent |
| **Deepgram** | Speech to text | Turns what you say into words |
| **Moss** | A very fast search engine | Finds the 3 most relevant clinic documents in ~7 ms |
| **Groq (gpt-oss-20b)** | The AI model | Reads those documents and writes an answer |
| **The gate** (Hesitate) | The fact checker | Checks each sentence before it becomes audio |
| **ElevenLabs** | Text to speech | Speaks the checked answer out loud |

## Moss, and why it matters here

Moss is a search tool. You give it documents; you ask it a question; it hands back the most
relevant passages. It's fast, around 7 milliseconds, so it can sit inside a live phone call
without making the caller wait.

Moss does **two jobs** in Hesitate:

1. **Every time the caller asks something**, Moss finds the relevant clinic documents for the AI
   to answer from.
2. **The Policy Desk writes into Moss live.** When staff change a policy, the new document goes
   straight into Moss, and the very next call uses it.

The important thing to understand: **Moss finds what's relevant, not what's true.** The old
12-hour sheet is very relevant to a fasting question, so Moss ranks it first. That's not a Moss
bug. That's how all search works. Hesitate is the part that decides what's actually allowed to
be said.

## Two kinds of information (this is the key idea)

The clinic has two kinds of information, and Hesitate treats them differently.

1. **The documents.** Prep sheets, FAQs, the patient guide. Messy, lots of them, some outdated.
   They cover everything: "Can I drink water?", "Is parking free?", "How do I get my results?"
2. **The policy table.** A small list of the handful of facts that hurt someone if they're
   wrong: fasting time, arrival time, cost, referral, insurance coverage. Each row has a date,
   and when a rule changes, the new row says "this replaces that one."

The AI answers freely from the documents. The gate only steps in when a sentence touches one of
the facts in the table. That's why "Can I drink water?" gets answered normally, and "fast for 12
hours" gets corrected.

**Why not just answer from the table?** Because the table only holds a few facts. Patients ask
about everything. You need the documents to be useful and the table to be safe.

## How the check actually works

Take the sentence: *"You need to fast for 12 hours."*

1. **Pull out the fact.** The gate reads the sentence and finds: fasting time = 12 hours.
2. **Find the current rule.** It looks up fasting time in the table. There are two rows: an old
   one (12 hours) and a new one (8 hours) that says "this replaces the old one." So the current
   rule is 8 hours.
3. **Compare.** 12 is not 8, so the sentence is wrong.
4. **Replace.** The caller hears: *"Actually, 8 hours, per your prep instructions."* The
   correction is built from the table's value, never from the AI.

No second AI is involved in the check. It's plain rules and a lookup, so it's fast and gives the
same answer every time.

The four possible results:
- **Supported:** matches the rule → spoken.
- **Contradicted:** doesn't match → corrected.
- **Unverifiable:** no rule exists for it → "I'll check with the front desk."
- **Conflict:** two current rules disagree → also declines, rather than guessing which one.

## The proof

A test of 23 real questions, run through the real system (real Moss, real AI), with the correct
answers written down **before** the run so nobody can say the results were adjusted afterward:

| | Wrong answers that reached the caller | Correct answers wrongly blocked |
|---|---|---|
| Normal AI agent | **6 of 23** | n/a |
| With Hesitate | **0 of 23** | **0 of 23** |

- All 6 wrong answers came from the old 12-hour sheet.
- 4 of the questions (water, medication, parking, results) have no rule in the table at all.
  They passed through fine, which proves the gate doesn't block everything.
- Moss search: about **7 ms**. The check itself: about **0.25 ms**.

"0 wrongly blocked" matters. A checker that blocks everything would also score 0 wrong. Showing
both numbers is what makes the result believable.

## What it doesn't do (know this, say it if asked)

- It only checks facts it knows how to read: numbers, costs, times, yes/no rules. A sentence like
  "You'll get a text message" has no number in it, so it isn't checked.
- If the policy table itself is wrong, Hesitate will enforce the wrong answer. It enforces the
  table; it doesn't discover truth.
- The voice worker runs on your laptop, not the cloud, because Render's free tier ran out of
  memory. The web page and the API are deployed.
- No real clinic has used it yet. No customer interviews.

Saying these calmly makes you more believable, not less.

---

# Part 2: The 6 minutes

**Before you start:** page open, protection **OFF**, call already connected, trace panel empty.
Policy Desk reset to 8 hours. Stand where the judges can see the screen and your face.

## 0:00 to 0:30: The hook

> "In 2024, Air Canada was held legally responsible for what its chatbot told a customer about
> its own refund policy. Voice agents are now answering patients the same way.
>
> This is a clinic's voice assistant. A patient wants to know how long to fast before a blood
> test. The clinic's real answer is 8 hours. But an old sheet in their system still says 12.
> Watch what happens."

*Look at the judges, not the screen, for this part. Memorize it word for word.*

## 0:30 to 1:20: Protection OFF (the problem, live)

**Do:** Say into the mic, clearly: *"How long do I need to fast before my blood test?"*
(If the mic misbehaves, type it into the text box. Don't apologize, just type.)

**It will say:** "12 hours."

> "Wrong. Here's why." *(point at the trace panel)* "Moss searched the clinic's documents in
> about 7 milliseconds and ranked the old 12-hour sheet first, because it's the most relevant
> match. The AI repeated it. This is a normal retrieval agent. Search is fast and accurate at
> finding relevant documents, but relevant isn't the same as current."

## 1:20 to 2:20: Protection ON (the fix, live)

**Do:** Hang up. Flip protection **ON**. Start call. Ask the exact same question.

**It will say:** "Actually, 8 hours, per your prep instructions."

> *(point at the struck-out draft)* "Same search results, same AI. It still wrote '12 hours.'
> But before that sentence became audio, Hesitate pulled out the fact, fasting time equals 12,
> looked up the current rule, 8, and replaced it. The caller never heard the wrong answer.
> *(point at the timing)* The check took a fraction of a millisecond."

**Then ask:** *"Can I drink water while I'm fasting?"*

**It will say:** yes, plain water is fine.

> "That one isn't in the policy table at all. It comes from the clinic's general patient guide,
> and it passes straight through. Hesitate only guards the handful of facts that hurt someone if
> they're wrong. It doesn't block everything else."

## 2:20 to 3:30: The Policy Desk (the judge drives it)

**Do:** Scroll to the Policy Desk. Turn to a judge.

> "Don't take my word that it's not hardcoded. Pick a new fasting time."

**Do:** Type their number (say 10). Click **Publish approved policy**. Wait for "Done." Ask the
fasting question again.

**It will say:** "10 hours."

> "The new rule went into Moss live and replaced the old one, and the next answer followed it."

**Do:** Click **Drop unapproved document** (it says "Patients must fast 16 hours"). Ask again.

**It will say:** still 10. The trace shows the 16-hour document marked **not an approved
policy**.

> "Now Moss has a document saying 16 hours, and the AI might even read it. But nobody approved
> it, so the caller still hears 10. Search can be wrong. The agent still won't say it."

## 3:30 to 4:00: The number

**Do:** Scroll to the Proof panel.

> "We didn't just test this once. Twenty-three real questions, answers written down before the
> run. Without Hesitate, **six wrong answers reached the caller. With it, zero.** And zero
> correct answers were wrongly blocked, including four questions that had no policy rule at
> all."

*Say "six" and "zero" slowly. Pause after "zero."*

## 4:00 to 4:15: The close

> "Retrieval decides what the agent reads. Hesitate decides what it's allowed to say."

*Stop talking. Let them ask.*

## 4:15 to 6:00: Questions (see Part 3)

If you're running long, cut the water question in the ON step first, then shorten the Policy
Desk to just the publish step. **Never cut the OFF/ON comparison or the number.**

---

# Part 3: Judge questions, with answers

Keep answers short. Say the answer, then stop.

**"Why not just search only the correct documents?"**
> "The correct table only covers maybe 30 facts. Patients ask about hundreds of things: water,
> parking, results. The documents answer those. The table guards the small set of facts that
> hurt someone if they're wrong."

**"What if the policy table itself is wrong?"**
> "Then it's confidently wrong, like any system. The difference is there's one small table with
> one owner to fix, not a pile of scattered documents. It enforces the table, it doesn't
> discover truth."

**"Why not use a second AI to check the first?"**
> "It would be slower, it can be wrong the same way, and it gives different answers each time.
> Ours is a direct lookup and comparison: under a millisecond, same answer every time."

**"What does Moss actually do here?"**
> "Two things. It finds the right documents on every turn, in about 7 milliseconds, fast enough
> for a live call. And the Policy Desk writes into it live, so a policy change shows up in the
> very next call."

**"Is the demo rigged?"**
> "The old sheet is planted on purpose, because real clinics have old sheets. But protection
> on and off use the exact same search and the exact same AI. The only difference is the check.
> And you just changed the policy yourself on the Policy Desk."

**"What does it miss?"**
> "Claims with no number or clear rule in them, like 'you'll get a text message.' And
> vocabulary from other fields: we ran it on insurance documents and it missed terms like
> 'police report.' Both are written up in the repo with the reasons."

**"Is this a business?"**
> "Air Canada showed companies are liable for what their agents say. Any clinic or regulated
> business putting a voice agent in front of customers needs something that can refuse to say
> the wrong thing. We haven't talked to customers yet. That's the next step."

**"How would another company use it?"**
> "The check sits at one point in LiveKit, right before speech. An existing LiveKit agent gets
> it by switching one base class. The work for a new customer is writing their policy table."

**"Why does it run on your laptop?"**
> "The voice worker needs more memory than Render's free tier gives. The web page and API are
> deployed. It's documented in the repo."

**If you don't know an answer:**
> "I don't know that yet. Here's how I'd find out: ..." *(and give one real step)*

Never make something up. A calm "I don't know" beats a confident wrong answer, which is the
whole point of your project.

---

# Part 4: Setup and backup plans

## 30 minutes before you go on

1. **On a phone hotspot?** Turn IPv6 off, or calls take minutes to connect:
   `networksetup -setv6off Wi-Fi`
   (Venue Wi-Fi that works normally: skip this.)
2. **Start everything** (once, and only once):
   `cd ~/Desktop/PROJECTS/"YC Fall 2026 x Moss" && bash scripts/demo.sh`
   Wait for `READY (TTS: live)`.
3. **Open** `http://localhost:8000/call.html` in **Chrome, incognito** (ad blockers can break
   the connection).
4. **Allow the microphone.**
5. **Click "Reset to original policy"** on the Policy Desk.
6. **Do one full test call**, OFF then ON. Hang up after.
7. Set protection to **OFF**, start the call, leave the trace empty. You're ready.
8. **Don't make lots of extra test calls** in the last 30 minutes. The Groq daily limit is 1,000
   requests; you're fine, just don't burn it.

## If something breaks on stage

Say one sentence about it and keep going. Never debug in front of the judges.

| What breaks | What you do | What you say |
|---|---|---|
| Mic doesn't pick you up | Type in the text box | "Let me type it, the room's a bit loud." |
| Agent doesn't join | Hang up, start call again once | "One second, reconnecting." |
| OFF gives the right answer (8) | Point at the Proof panel | "It got lucky this time. Across 23 questions it was wrong 6 times. That's the point: you can't count on it." |
| Still dead after one retry | Open a terminal, run the tests: `pytest tests/test_adversarial_phrasings.py -v` | "Here's the check running on its own." |
| Internet gone | Play the video from your laptop | "Here's the recorded run." |

**Do not restart `demo.sh` in the middle of a call.** Running it twice at once was what broke
things during testing.

## Last reminders

- Talk **while** you demo. Don't explain first and demo later.
- Say the number once, slowly: **six, zero, zero.**
- Look at the judges during the hook and the close.
- Don't apologize for anything.
- End on the closing line, then stop talking.
