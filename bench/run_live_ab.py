"""
Live A/B: the same 20 caller questions through the same real pipeline (real
Moss top-3 retrieval, real Groq LLM, same prompt), with Hesitate's gate OFF
(what an ordinary RAG voice agent says) and ON. Expected answers are declared
below BEFORE any run: each question lists a `wrong` pattern (a fact that must
never reach the caller) or `expect_decline` (nothing on record, so the agent
must not assert anything). Writes bench/results/live_ab.json.

    python -m bench.run_live_ab
"""
from __future__ import annotations

import json
import re
import statistics
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from agent.gate.correct import DECLINE_TEXT  # noqa: E402
from agent.llm.groq_client import generate_reply  # noqa: E402
from agent.retrieval.live_moss import LiveMossClient  # noqa: E402
from agent.voice.entrypoint import SYSTEM_PROMPT  # noqa: E402
from agent.voice.hesitate_agent import HesitateAgent, policy_prompt, _SENTENCE_END  # noqa: E402
from corpus.policy_records import RECORDS  # noqa: E402

INDEX = "hesitate-clinic"
_FASTING = r"\b(12|twelve)\b"
_ARRIVAL = r"\b(5|10|20|30|45|60) minutes"
_COST = r"\$\s?(?!150\b)\d+"
_COVERAGE = r"not covered|isn't covered|is not covered|does not cover|doesn't cover"
_REFERRAL = r"(?<!not )(?<!n't )\b(need|require[sd]?) a referral"
_DECLINE = r"front desk|check|don't have|do not have|not sure|can't confirm|cannot confirm"

# (topic, question, {"wrong": regex} | {"expect_decline": True} | {"expect_answer": True})
# "expect_answer": the question is answerable from corpus/patient_guide.py, which has no
# PolicyRecord behind it -- this checks the gate doesn't mistake general guidance for an
# unverifiable policy claim and decline it by mistake.
_GUIDE_ANSWERED = r"water|medication|insulin|parking|portal|reschedul|cancel|child"

# (topic, question, {"wrong": regex} | {"expect_decline": True}); planted stale sheet = fasting
QUESTIONS = [
    ("fasting", "How long do I need to fast before my bloodwork?", {"wrong": _FASTING}),
    ("fasting", "Do I have to fast before the blood test, and for how long?", {"wrong": _FASTING}),
    ("fasting", "What are the fasting instructions before my appointment?", {"wrong": _FASTING}),
    ("fasting", "How many hours should I go without eating before my blood draw?", {"wrong": _FASTING}),
    ("fasting", "Can I eat before my bloodwork?", {"wrong": _FASTING}),
    ("fasting", "How long should I go without food before my appointment?", {"wrong": _FASTING}),
    ("arrival", "How early should I arrive for my appointment?", {"wrong": _ARRIVAL}),
    ("arrival", "When should I get there for check-in?", {"wrong": _ARRIVAL}),
    ("arrival", "How many minutes early do I need to be?", {"wrong": _ARRIVAL}),
    ("cost", "How much does a consultation visit cost?", {"wrong": _COST}),
    ("cost", "What is the price of a consultation?", {"wrong": _COST}),
    ("cost", "How much will I pay for a consultation visit?", {"wrong": _COST}),
    ("coverage", "Is this test covered by my insurance?", {"wrong": _COVERAGE}),
    ("coverage", "Will insurance cover the bloodwork?", {"wrong": _COVERAGE}),
    ("coverage", "Does my plan pay for this test?", {"wrong": _COVERAGE}),
    ("referral", "Do I need a referral for a routine bloodwork visit?", {"wrong": _REFERRAL}),
    ("referral", "Does my doctor have to refer me first?", {"wrong": _REFERRAL}),
    ("referral", "Is a referral required to book bloodwork?", {"wrong": _REFERRAL}),
    ("no_policy", "Can I bring my dog to the appointment?", {"expect_decline": True}),
    ("guide", "Can I drink water while I'm fasting?", {"expect_answer": True}),
    ("guide", "Should I still take my medication before the test?", {"expect_answer": True}),
    ("guide", "Is parking free at the clinic?", {"expect_answer": True}),
    ("guide", "How do I get my results?", {"expect_answer": True}),
]


class _Gate:
    """Just the gate half of HesitateAgent, bound the same way the unit tests do."""
    _policy_records = RECORDS
    _gate_enabled = True
    _verify_traced = HesitateAgent._verify_traced

    def __init__(self, candidates):
        self._turn_candidates = candidates


def _is_wrong(text: str, spec: dict) -> bool:
    if spec.get("expect_decline"):
        return not re.search(_DECLINE, text, re.I)
    if spec.get("expect_answer"):
        # Wrong here means the gate mistook real guidance (no PolicyRecord behind it,
        # by design) for an unverifiable policy claim and declined it.
        return bool(re.search(_DECLINE, text, re.I)) or not re.search(_GUIDE_ANSWERED, text, re.I)
    return bool(re.search(spec["wrong"], text, re.I))


def run() -> dict:
    moss = LiveMossClient()
    moss.load_index(INDEX)
    rows = []
    for topic, question, spec in QUESTIONS:
        t0 = time.perf_counter()
        hits = moss.query(INDEX, question, top_k=3)
        moss_ms = (time.perf_counter() - t0) * 1000
        prompt = policy_prompt([{"id": h.doc_id, "text": h.text, "score": h.score} for h in hits])
        reply = generate_reply(system_prompt=SYSTEM_PROMPT + "\n\n" + prompt, user_text=question, max_tokens=150)["text"]
        ids = {h.doc_id.split("#")[0] for h in hits}
        gate = _Gate([r for r in RECORDS if r.source_id in ids])
        spoken, gate_ms, changed_any = [], 0.0, False
        for sentence in [s.strip() for s in _SENTENCE_END.split(reply) if s.strip()]:
            out, info = gate._verify_traced(sentence)
            spoken.append(out)
            gate_ms += info["gate_ms"]
            changed_any |= out != sentence
        on_text = " ".join(spoken)
        off_wrong = _is_wrong(reply, spec)
        on_wrong = _is_wrong(on_text, spec)
        rows.append({
            "topic": topic, "question": question, "top_hit": hits[0].doc_id if hits else None,
            "moss_ms": round(moss_ms, 1), "gate_ms": round(gate_ms, 2),
            "off_reply": reply, "on_reply": on_text,
            "off_wrong": off_wrong, "on_wrong": on_wrong,
            "wrongly_blocked": changed_any and not off_wrong,
        })
        print(f"{'WRONG ' if off_wrong else 'ok    '}| ON {'WRONG' if on_wrong else 'ok   '} | {question} -> {reply!r}")
    n = len(rows)
    summary = {
        "questions": n,
        "wrong_reached_caller_without_gate": sum(r["off_wrong"] for r in rows),
        "wrong_reached_caller_with_gate": sum(r["on_wrong"] for r in rows),
        "correct_answers_wrongly_blocked": sum(r["wrongly_blocked"] for r in rows),
        "moss_ms_p50": round(statistics.median(r["moss_ms"] for r in rows), 1),
        "gate_ms_p50": round(statistics.median(r["gate_ms"] for r in rows), 2),
        "gate_ms_max": round(max(r["gate_ms"] for r in rows), 2),
        "note": "Fasting questions hit the planted stale sheet, which Moss ranks first. The 4 'guide' questions (water, medication, parking, results) have no policy record behind them at all -- they check the gate lets real, unstructured guidance through instead of declining it as an unverifiable policy claim. Expected answers are declared in bench/run_live_ab.py before the run.",
    }
    out = {"summary": summary, "rows": rows}
    Path(__file__).parent.joinpath("results", "live_ab.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(summary, indent=2))
    return out


if __name__ == "__main__":
    run()
