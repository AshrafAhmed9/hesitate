"""
PLAN.md section 9: "Reusable integration | Versioned gate interface,
packaged example, a second compatible text-stream agent | Another worker
invokes the same core without copying clinic logic."

A minimal text-based chat agent (no LiveKit, no audio, no voice
dependencies at all) that calls Groq directly and runs every reply
through the SAME verification gate (agent.gate.verify.verify_sentence)
that HesitateAgent uses for voice. This is the proof that the gate is a
reusable core, not logic wired specifically into the voice pipeline --
importing it here required zero clinic-specific code beyond passing in
the policy records.

Usage:
    python -m examples.text_chat_agent
    (then type questions; type 'quit' to exit)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from agent.gate.verify import verify_sentence
from agent.llm.groq_client import generate_reply
from corpus.policy_records import RECORDS

SYSTEM_PROMPT = (
    "You are a clinic front-desk assistant. Answer questions about fasting "
    "instructions, arrival time, insurance coverage, cost, and required "
    "documents. Be brief -- one or two sentences."
)


def ask(user_text: str) -> str:
    """One turn: generate a reply, verify it through the same gate the
    voice agent uses, return the text that would actually be shown/spoken.

    KNOWN LIMITATION observed live: when the LLM answers with a range
    ("8-12 hours") rather than a single value, extract.py's regex grabs
    only the first number, which can coincidentally match the current
    record (8) even though the full range is imprecise. This is a real
    gap in the typed extractor's range handling, not specific to this
    example -- the same regex is used by the voice agent."""
    reply = generate_reply(SYSTEM_PROMPT, user_text)
    result = verify_sentence(reply["text"], RECORDS)
    if result.disposition == "released":
        return result.replacement_text
    tag = "[CORRECTED]" if result.disposition == "corrected" else "[DECLINED]"
    return f"{tag} {result.replacement_text}"


def main():
    print("Hesitate text chat (reusing the same verification gate as the voice agent).")
    print("Type a question, or 'quit' to exit.\n")
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_text.lower() in ("quit", "exit"):
            break
        if not user_text:
            continue
        print(f"Agent: {ask(user_text)}\n")


if __name__ == "__main__":
    main()
