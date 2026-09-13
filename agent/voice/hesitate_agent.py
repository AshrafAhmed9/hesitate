"""
The actual sole-TTS-entry-point boundary (PLAN.md section 3/4).

Overrides LiveKit Agent.tts_node -- the one point every generated
sentence must pass through before becoming audio, including corrections
(PLAN.md: "Every application speech path must use the boundary"). Buffers
incoming text into sentences, runs each through the real verification
gate, and passes only the approved/corrected/decline text onward to the
real TTS synthesis (the default tts_node implementation via super()).

This is unit-tested at the text level (buffer -> gate -> replacement text)
without a live LiveKit room -- see tests/test_hesitate_agent.py. It has
NOT been run against a real live audio call yet; that requires an actual
room/participant, which is the next integration step once a browser
client exists.
"""
from __future__ import annotations

import re
from typing import AsyncIterable

from livekit.agents import Agent
from livekit.agents.voice.agent import ModelSettings

from agent.gate.correct import DECLINE_TEXT, build_sentence_correction
from agent.gate.schema import Decision, PolicyRecord
from agent.gate.verify import verify_sentence

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


class HesitateAgent(Agent):
    """PLAN.md section 4's release rule, applied to every sentence the
    LLM produces, before any of it reaches audio."""

    def __init__(self, *args, policy_records: list[PolicyRecord], **kwargs):
        super().__init__(*args, **kwargs)
        self._policy_records = policy_records

    async def tts_node(self, text: AsyncIterable[str], model_settings: ModelSettings):
        verified_stream = self._verify_and_replace(text)
        async for chunk in super().tts_node(verified_stream, model_settings):
            yield chunk

    async def _verify_and_replace(self, text: AsyncIterable[str]) -> AsyncIterable[str]:
        """Buffers the incoming token stream into sentences (bounded by
        sentence-ending punctuation; PLAN.md section 4 'Stream lifecycle'),
        verifies each one, and yields the approved/corrected/decline text
        instead of the original wherever it was CONTRADICTED, CONFLICT, or
        UNVERIFIABLE."""
        buffer = ""
        async for token in text:
            buffer += token
            parts = _SENTENCE_END.split(buffer)
            # everything but the last part is a complete sentence
            for sentence in parts[:-1]:
                if sentence.strip():
                    yield self._verify_one(sentence.strip())
            buffer = parts[-1]
        if buffer.strip():
            yield self._verify_one(buffer.strip())  # final flush, per section 4

    def _verify_one(self, sentence: str) -> str:
        result = verify_sentence(sentence, self._policy_records)
        decision = result.sentence_decision
        if decision == Decision.SUPPORTED:
            return sentence
        if decision == Decision.CONTRADICTED:
            correction = build_sentence_correction(result.atomic_verdicts)
            return correction
        return DECLINE_TEXT  # CONFLICT or UNVERIFIABLE
