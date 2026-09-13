"""
Locks in the live-call quota guard (COMPETITION.md decision: ElevenLabs
free tier reserved for final demo + finale only). Uses a dummy API key to
prove the real provider is genuinely never called in dev mode -- if it
were called, this would raise (invalid key), not silently succeed.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

pytest.importorskip("livekit.plugins.elevenlabs")


@pytest.mark.asyncio
async def test_dev_mode_never_calls_real_provider():
    from livekit.plugins import elevenlabs
    from agent.voice.guarded_tts import GuardedTTS
    from agent.voice.tts import TTSMode

    real = elevenlabs.TTS(api_key="dummy-invalid-key-proves-no-network-call")
    guarded = GuardedTTS(real, mode=TTSMode.DEV)
    stream = guarded.synthesize("Quota must not be spent.")
    frames = [event async for event in stream]
    await stream.aclose()
    assert len(frames) > 0
    assert all(f.frame.sample_rate == real.sample_rate for f in frames)


@pytest.mark.asyncio
async def test_mode_defaults_to_dev_from_environment(monkeypatch):
    monkeypatch.delenv("HESITATE_TTS_MODE", raising=False)
    from livekit.plugins import elevenlabs
    from agent.voice.guarded_tts import GuardedTTS
    from agent.voice.tts import TTSMode

    real = elevenlabs.TTS(api_key="dummy")
    guarded = GuardedTTS(real)
    assert guarded._mode == TTSMode.DEV
