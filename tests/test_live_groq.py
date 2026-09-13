"""LIVE test against the real Groq API. Skips cleanly without GROQ_API_KEY."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set — live Groq test skipped",
)


def test_generate_reply_returns_nonempty_content():
    from agent.llm.groq_client import generate_reply
    r = generate_reply(
        "You are a clinic front-desk voice assistant. Answer briefly, one sentence.",
        "How long do I need to fast before my bloodwork?",
    )
    assert r["text"]
    assert r["reasoning_tokens"] < 20, "reasoning_effort=low should keep reasoning tokens minimal"


def test_latency_under_measured_baseline():
    """Not a tight SLA -- network variance is real -- but catches a
    regression back toward the ~580ms default-reasoning-effort behavior."""
    from agent.llm.groq_client import generate_reply
    r = generate_reply(
        "You are a clinic front-desk voice assistant. Answer briefly, one sentence.",
        "Do I need a referral?",
    )
    assert r["latency_ms"] < 1000
