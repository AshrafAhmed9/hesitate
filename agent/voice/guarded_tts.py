"""
Wraps a real LiveKit TTS plugin (e.g. elevenlabs.TTS) with the same
quota discipline as agent/voice/tts.py, but at the AgentSession level so
it's actually enforced during a live call, not just in isolated dev-mode
testing.

DECISION (Ashraf, COMPETITION.md): the ElevenLabs free tier (10,000
chars/month) is reserved for the final demo recording and the live
finale ONLY. Without this wrapper, running agent/voice/entrypoint.py
against ANY real LiveKit room -- including exploratory dev testing --
would call the real ElevenLabs API on every agent turn and spend that
quota. This makes "dev mode = silent, zero cost" the default for the
whole session, not just for calls made directly through speak().

In DEV mode, synthesize()/stream() emit a single short silent audio frame
instead of calling the real provider -- the AgentSession pipeline keeps
working end-to-end (STT, LLM, the verification gate, turn-taking) so the
whole loop can be tested live, with only the actual spoken audio replaced
by silence. Real ElevenLabs is called only when mode="live" is passed
explicitly, matching agent/voice/tts.py's TTSMode enum.
"""
from __future__ import annotations

import os

from livekit import rtc
from livekit.agents import tts as tts_base
from livekit.agents.types import APIConnectOptions, DEFAULT_API_CONNECT_OPTIONS

from agent.voice.tts import TTSMode


class _SilentChunkedStream(tts_base.ChunkedStream):
    """Emits one short silent frame instead of calling a real provider.
    Uses the real AudioEmitter API (initialize/push/flush/end_input),
    verified against this exact installed livekit-agents version rather
    than assumed."""

    async def _run(self, output_emitter) -> None:
        num_channels = self._tts.num_channels
        sample_rate = self._tts.sample_rate
        duration_s = 0.3
        num_samples = int(sample_rate * duration_s)
        silence = b"\x00\x00" * num_samples * num_channels  # 16-bit PCM silence

        output_emitter.initialize(
            request_id=str(id(self)),
            sample_rate=sample_rate,
            num_channels=num_channels,
            mime_type="audio/pcm",
        )
        print(f"[GuardedTTS dev-stub, 0 chars spent] would speak: {self._input_text!r}")
        output_emitter.push(silence)
        output_emitter.flush()
        output_emitter.end_input()


class GuardedTTS(tts_base.TTS):
    """Drop-in replacement for a real TTS plugin. Reads HESITATE_TTS_MODE
    from the environment (default 'dev') so a live LiveKit room test never
    accidentally spends the reserved ElevenLabs quota unless explicitly
    told to."""

    def __init__(self, real_tts: tts_base.TTS, mode: TTSMode | None = None):
        super().__init__(
            capabilities=real_tts.capabilities,
            sample_rate=real_tts.sample_rate,
            num_channels=real_tts.num_channels,
        )
        self._real_tts = real_tts
        self._mode = mode or TTSMode(os.environ.get("HESITATE_TTS_MODE", TTSMode.DEV.value))

    def synthesize(self, text: str, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS):
        if self._mode == TTSMode.LIVE:
            return self._real_tts.synthesize(text, conn_options=conn_options)
        return _SilentChunkedStream(tts=self, input_text=text, conn_options=conn_options)

    def stream(self, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS):
        if self._mode == TTSMode.LIVE:
            return self._real_tts.stream(conn_options=conn_options)
        raise NotImplementedError(
            "GuardedTTS.stream() dev-mode path not implemented -- HesitateAgent's tts_node "
            "override currently drives synthesis via synthesize()-per-sentence, not the "
            "streaming .stream() API, so this has not been exercised. If AgentSession calls "
            ".stream() directly, this will raise loudly rather than silently spending quota."
        )
