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
    # reasoning_effort='low' measured at 6 reasoning tokens (groq_client.py docstring)
    # vs 121 at default effort -- 30 gives headroom for live-call variance while still
    # catching a real regression back toward default effort's much larger token count.
    assert r["reasoning_tokens"] < 30, "reasoning_effort=low should keep reasoning tokens minimal"


def test_latency_under_measured_baseline():
    """Not a tight SLA -- network variance is real -- but catches a real
    regression, like reasoning_effort silently reverting to 'medium' (measured
    at 581ms total / 121 reasoning tokens vs 'low''s 361ms / 6 tokens,
    groq_client.py's module docstring). Widened from 1000ms after live runs
    on 2026-09-27 repeatedly landed at 1000-1300ms on plain Groq network
    variance with reasoning_effort='low' unchanged -- not a code regression."""
    from agent.llm.groq_client import generate_reply
    r = generate_reply(
        "You are a clinic front-desk voice assistant. Answer briefly, one sentence.",
        "Do I need a referral?",
    )
    assert r["reasoning_tokens"] < 20, "reasoning_effort=low should keep reasoning tokens minimal"
    assert r["latency_ms"] < 2000
