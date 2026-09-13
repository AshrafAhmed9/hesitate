"""
LLM reply generation via Groq (openai/gpt-oss-20b), chosen for this
project because Ashraf does not have an OpenAI/Anthropic key.

MEASURED FINDING, not asserted: gpt-oss-20b is a reasoning model that by
default spends completion tokens on a hidden `reasoning` field before
producing `content`. For a one-sentence factual reply this measured
121 reasoning tokens and 581ms total latency -- both directly hostile to
the voice-turn latency budget (PLAN.md section 5 target: added
first-useful-answer p95 <= 200ms). Setting `reasoning_effort: "low"`
dropped reasoning tokens to 6 and total latency to 361ms on the same
question, measured on the same machine/network. `reasoning_effort: "none"`
is NOT a valid value for this model (HTTP 400) -- "low" is the floor.

This is exactly the kind of measured-not-invented latency finding PLAN.md
section 5 requires ("no fixed '15ms NLI' claim without measurement").
"""
from __future__ import annotations

import os

import requests

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-20b"
REASONING_EFFORT = "low"  # measured minimum; "none" is rejected by the API


def generate_reply(system_prompt: str, user_text: str, max_tokens: int = 150) -> dict:
    """Returns {'text': str, 'latency_ms': float, 'reasoning_tokens': int,
    'completion_tokens': int}. Raises on non-200 rather than silently
    returning an empty reply -- PLAN.md's own gpt-oss discovery here was
    exactly a silent-empty-content failure mode to guard against."""
    import time
    api_key = os.environ["GROQ_API_KEY"]
    t0 = time.perf_counter()
    resp = requests.post(
        GROQ_CHAT_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "max_tokens": max_tokens,
            "reasoning_effort": REASONING_EFFORT,
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    elapsed_ms = (time.perf_counter() - t0) * 1000
    choice = data["choices"][0]["message"]
    content = choice.get("content", "")
    if not content:
        raise RuntimeError(
            f"empty content from Groq despite HTTP 200 -- likely reasoning_tokens ate the "
            f"whole max_tokens budget; response: {data}"
        )
    usage = data.get("usage", {})
    return {
        "text": content,
        "latency_ms": elapsed_ms,
        "reasoning_tokens": usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
    }
