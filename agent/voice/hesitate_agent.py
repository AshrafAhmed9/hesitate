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

import asyncio
import json
import re
import time
from typing import AsyncIterable, Optional

from livekit.agents import Agent, llm
from livekit.agents.voice.agent import ModelSettings

from agent.gate.correct import DECLINE_TEXT, build_sentence_correction
from agent.gate.schema import Decision, PolicyRecord
from agent.gate.verify import verify_sentence

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
TRACE_TOPIC = "hesitate-trace"


def policy_prompt(hits: list[dict]) -> str:
    """Retrieved passages exactly as Moss ranked them -- no reordering, so a
    stale sheet that outranks the current one reaches the model the way it
    would in any ordinary RAG agent."""
    lines = "\n".join(f"{i + 1}. {h['text']}" for i, h in enumerate(hits))
    return (
        "Clinic policy passages, ranked by relevance:\n" + lines +
        "\nAnswer the caller using only these passages, in one short sentence, "
        "with no markdown. If they do not answer the question, say you will "
        "check with the front desk."
    )


class HesitateAgent(Agent):
    """PLAN.md section 4's release rule, applied to every sentence the
    LLM produces, before any of it reaches audio.

    Live-call additions: each turn retrieves from Moss (moss_client, an async
    moss.MossClient with the index already loaded) and the gate checks against
    the policy records Moss returned; a per-sentence trace is published over
    the LiveKit data channel so the call page can show what was caught.
    gate_enabled=False is the ordinary-RAG baseline: same retrieval, same
    prompt, nothing checked."""

    def __init__(
        self,
        *args,
        policy_records: list[PolicyRecord],
        moss_client=None,
        index_name: str = "hesitate-test",
        room=None,
        gate_enabled: bool = True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._policy_records = policy_records
        self._moss = moss_client
        self._index_name = index_name
        self._room = room
        self._gate_enabled = gate_enabled
        self._turn_candidates: Optional[list[PolicyRecord]] = None
        self._turn_id = 0
        self._turn_started = 0.0
        self._first_sentence_sent = False

    async def prepare_turn(self, caller_text: str) -> str:
        """Retrieve from Moss for this turn, remember the candidate records
        for the gate, publish the turn-start trace, return the prompt text."""
        self._turn_id += 1
        self._turn_started = time.perf_counter()
        self._first_sentence_sent = False
        hits: list[dict] = []
        moss_ms = 0.0
        if self._moss is not None:
            from moss import QueryOptions

            t0 = time.perf_counter()
            result = await self._moss.query(self._index_name, caller_text, QueryOptions(top_k=3))
            moss_ms = (time.perf_counter() - t0) * 1000
            hits = [{"id": d.id, "text": d.text, "score": round(d.score, 3)} for d in result.docs]
            ids = {h["id"] for h in hits}
            self._turn_candidates = [r for r in self._policy_records if r.source_id in ids]
        else:
            self._turn_candidates = None
        await self._publish({
            "t": "turn", "id": self._turn_id, "caller": caller_text,
            "moss": hits, "moss_ms": round(moss_ms, 1), "gate": self._gate_enabled,
        })
        return policy_prompt(hits)

    async def on_user_turn_completed(self, turn_ctx: llm.ChatContext, new_message: llm.ChatMessage) -> None:
        prompt = await self.prepare_turn(new_message.text_content or "")
        turn_ctx.add_message(role="system", content=prompt)

    async def _publish(self, payload: dict) -> None:
        if self._room is None:
            return
        try:
            await self._room.local_participant.publish_data(
                json.dumps(payload).encode(), topic=TRACE_TOPIC, reliable=True
            )
        except Exception as e:  # the trace must never break the call
            print(f"[hesitate trace] publish failed: {e!r}")

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
                    yield await self._verify_and_trace(sentence.strip())
            buffer = parts[-1]
        if buffer.strip():
            yield await self._verify_and_trace(buffer.strip())  # final flush, per section 4

    async def _verify_and_trace(self, sentence: str) -> str:
        spoken, info = self._verify_traced(sentence)
        first_ms = None
        if not getattr(self, "_first_sentence_sent", True):
            self._first_sentence_sent = True
            first_ms = round((time.perf_counter() - self._turn_started) * 1000, 1)
        await self._publish({
            "t": "sentence", "id": getattr(self, "_turn_id", 0), "draft": sentence,
            "spoken": spoken, "llm_ms": first_ms, **info,
        })
        return spoken

    def _verify_one(self, sentence: str) -> str:
        return self._verify_traced(sentence)[0]

    def _verify_traced(self, sentence: str) -> tuple[str, dict]:
        if not getattr(self, "_gate_enabled", True):
            return sentence, {"decision": "not_checked", "reason": "protection off", "gate_ms": 0.0}
        records = getattr(self, "_turn_candidates", None)
        if records is None:
            records = self._policy_records
        result = verify_sentence(sentence, records)
        decision = result.sentence_decision
        gate_ms = round(result.stage_timings_ms["total_ms"], 2)
        reason = next((v.reason for v in result.atomic_verdicts if v.decision == decision), "")
        info = {"decision": decision.value, "reason": reason, "gate_ms": gate_ms}
        if decision == Decision.SUPPORTED:
            return sentence, info
        if decision == Decision.CONTRADICTED:
            return build_sentence_correction(result.atomic_verdicts), info
        return DECLINE_TEXT, info  # CONFLICT or UNVERIFIABLE
