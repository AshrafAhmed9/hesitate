# 6-minute run sheet

Start: `bash scripts/demo.sh`, wait for READY. Page open at localhost:8000/call.html, Start call,
protection OFF. Phone hotspot on standby.

| Time | Screen | Say / do |
|---|---|---|
| 0:00–0:25 | Call page, empty trace | "An airline was held liable in 2024 for what its chatbot said about its own policy. Voice agents now answer patients. A patient asks how long to fast before a blood test. The real answer is 8 hours. An old sheet in the system still says 12. Watch." |
| 0:25–1:25 | Protection OFF | Ask: "How long do I need to fast before my blood test?" It says 12 hours. Point at the trace: "Moss ranked the old sheet first and the model repeated it. That's an ordinary retrieval agent." |
| 1:25–2:25 | Protection ON | Same question. It says 8. Point at the struck-out draft and the check time: "It caught it in about a millisecond." |
| 2:25–3:25 | Policy desk | Hand the keyboard to a judge. They publish a new fasting time, then ask. It follows. Then they drop an unapproved "16 hours" doc and ask again: the trace flags it "not an approved policy" and the answer doesn't change. "Search can be wrong. The agent still won't say it." |
| 3:25–4:00 | Proof panel | "Twenty real questions: 6 wrong answers reached the caller without this, 0 with it, and 0 correct answers blocked." Say the number slowly. |
| 4:00–6:00 | Q&A | Answers from `docs/FINALE_QA.md`. |

Close: "Retrieval decides what the agent reads. Hesitate decides what it's allowed to say."

**Fallbacks (decide now, don't debug on stage):**
- Mic or room noise fails: type the question in the text box.
- Agent fails: `pytest tests/test_hesitate_agent.py tests/test_adversarial_phrasings.py -v` in a terminal.
- Network down: the video, downloaded locally.
- If OFF answers correctly on stage, say so, point at the Proof panel (6 of 20) and move on. Never fake it.
- Say one sentence about any failure and continue.
