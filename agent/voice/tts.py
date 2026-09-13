"""
TTS abstraction with an explicit quota guard.

DECISION (Ashraf, recorded in COMPETITION.md): the ElevenLabs free tier
(10,000 chars/month) is reserved for the final demo recording and the
live finale ONLY. Dev iteration and rehearsal must not spend it. This
module enforces that as code, not as a habit to remember: real ElevenLabs
calls only happen when `mode="live"` is passed explicitly. The default
mode is "dev", which logs what would have been spoken and returns a
zero-length silent stub -- so the rest of the pipeline (gate timing,
correction logic, dashboard) can be exercised for free, indefinitely.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum


class TTSMode(str, Enum):
    DEV = "dev"    # default: no network call, no quota spent, logs text only
    LIVE = "live"  # real ElevenLabs call -- spends the reserved quota


@dataclass
class TTSResult:
    mode: TTSMode
    text: str
    audio_bytes: bytes | None  # None in dev mode
    characters_spent: int      # 0 in dev mode


def speak(text: str, mode: TTSMode = TTSMode.DEV) -> TTSResult:
    if mode == TTSMode.DEV:
        print(f"[TTS dev-stub, 0 chars spent] would speak: {text!r}")
        return TTSResult(mode=mode, text=text, audio_bytes=None, characters_spent=0)

    # mode == LIVE: real call, spends the reserved ElevenLabs quota.
    import requests
    api_key = os.environ["ELEVENLABS_API_KEY"]
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # "Rachel", a default stock voice
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={"text": text, "model_id": "eleven_monolingual_v1"},
        timeout=30,
    )
    resp.raise_for_status()
    return TTSResult(mode=mode, text=text, audio_bytes=resp.content, characters_spent=len(text))
