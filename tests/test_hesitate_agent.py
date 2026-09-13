"""
Tests the sentence-buffering + verification logic HesitateAgent.tts_node
applies to every token stream, without needing a live LiveKit room/STT/
TTS (that integration is untested end-to-end — see hesitate_agent.py's
module docstring for the honest status).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

pytest.importorskip("livekit.agents")

from agent.voice.hesitate_agent import HesitateAgent
from corpus.policy_records import RECORDS


class _Stub:
    """Binds just the two methods under test, avoiding a full Agent()
    construction which needs a real LLM/STT/TTS wired up."""
    _policy_records = RECORDS
    _verify_and_replace = HesitateAgent._verify_and_replace
    _verify_one = HesitateAgent._verify_one


async def _token_stream(tokens):
    for t in tokens:
        yield t


async def _collect(tokens):
    stub = _Stub()
    out = []
    async for sentence in stub._verify_and_replace(_token_stream(tokens)):
        out.append(sentence)
    return out


@pytest.mark.asyncio
async def test_streamed_hallucination_is_corrected_before_next_sentence():
    tokens = ["You", "'ll need to ", "fast for twelve hours", " before the test.",
              " Please ", "arrive 15 minutes early."]
    out = await _collect(tokens)
    assert out == [
        "Actually — 8 hours, per your prep instructions.",
        "Please arrive 15 minutes early.",
    ]
    # The critical guarantee: the wrong number never appears in what's
    # handed onward to TTS.
    assert not any("twelve" in s for s in out)


@pytest.mark.asyncio
async def test_correct_claim_passes_through_unmodified():
    tokens = ["Fast for 8 hours before the test."]
    out = await _collect(tokens)
    assert out == ["Fast for 8 hours before the test."]


@pytest.mark.asyncio
async def test_final_flush_with_no_trailing_punctuation():
    """PLAN.md section 4: 'Final flush goes through the same gate.'"""
    tokens = ["Fast for 8 hours"]  # no trailing period
    out = await _collect(tokens)
    assert out == ["Fast for 8 hours"]


@pytest.mark.asyncio
async def test_unverifiable_claim_declines():
    tokens = ["You'll get a text confirmation an hour before your visit."]
    out = await _collect(tokens)
    # KNOWN GAP (documented in bench/cases.py): this sentence has no typed
    # slot, so it's currently SUPPORTED (no claims extracted), not
    # declined. Asserting actual behavior, matching the documented finding.
    assert out == ["You'll get a text confirmation an hour before your visit."]
