"""
A synthetic LiveKit room participant that speaks a real, locally-
synthesized phrase (macOS `say`, zero cost, no API) into a room -- used
to test the full live pipeline (Deepgram STT -> Groq LLM -> the
verification gate -> GuardedTTS) end to end WITHOUT a human joining via
browser and microphone.

Usage:
    python -m scripts.synthetic_caller "How long do I need to fast?"

Requires: a LiveKit agent worker (agent/voice/entrypoint.py) already
running and dispatched to the same room, ffmpeg on PATH, and macOS `say`
(this script is macOS-only; documented, not hidden -- a Linux/CI
equivalent would need a different local TTS, e.g. espeak).
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import tempfile

from dotenv import load_dotenv
from livekit import rtc

load_dotenv()

SAMPLE_RATE = 16000
NUM_CHANNELS = 1
ROOM_NAME = "hesitate-demo"


def synthesize_locally(text: str) -> bytes:
    """macOS `say` -> ffmpeg -> raw 16-bit PCM mono @ 16kHz. Zero cost,
    no network call, no API key -- this is what makes it safe to run
    repeatedly during development without touching any reserved quota."""
    with tempfile.NamedTemporaryFile(suffix=".aiff") as aiff, \
         tempfile.NamedTemporaryFile(suffix=".raw") as raw:
        subprocess.run(["say", "-o", aiff.name, text], check=True)
        subprocess.run(
            ["ffmpeg", "-y", "-i", aiff.name, "-ar", str(SAMPLE_RATE), "-ac", str(NUM_CHANNELS), "-f", "s16le", raw.name],
            check=True, capture_output=True,
        )
        return open(raw.name, "rb").read()


async def speak_into_room(text: str, room_name: str = ROOM_NAME) -> None:
    import uuid
    from agent.voice.token import issue_room_token

    # Unique identity per run: a hardcoded identity risks colliding with a
    # not-yet-fully-cleaned-up connection from a previous test run, which
    # is a plausible contributor to the observed transcript gap.
    identity = f"synthetic-caller-{uuid.uuid4().hex[:8]}"
    token = issue_room_token(room_name, identity=identity)
    room = rtc.Room()
    await room.connect(os.environ["LIVEKIT_URL"], token)
    print(f"Connected to room {room_name!r} as {identity!r}.")

    source = rtc.AudioSource(SAMPLE_RATE, NUM_CHANNELS)
    track = rtc.LocalAudioTrack.create_audio_track("synthetic-caller-mic", source)
    await room.local_participant.publish_track(track)
    print("Published synthetic microphone track.")

    pcm = synthesize_locally(text)
    print(f"Synthesized {len(pcm)} bytes locally (zero cost, no API call): {text!r}")

    frame_ms = 20
    bytes_per_frame = int(SAMPLE_RATE * frame_ms / 1000) * 2  # 16-bit samples
    for i in range(0, len(pcm), bytes_per_frame):
        chunk = pcm[i:i + bytes_per_frame]
        if len(chunk) < bytes_per_frame:
            chunk = chunk + b"\x00" * (bytes_per_frame - len(chunk))
        frame = rtc.AudioFrame(
            data=chunk,
            sample_rate=SAMPLE_RATE,
            num_channels=NUM_CHANNELS,
            samples_per_channel=bytes_per_frame // 2,
        )
        await source.capture_frame(frame)
        await asyncio.sleep(frame_ms / 1000)

    print("Finished speaking. Waiting 5s for agent response, then disconnecting.")
    await asyncio.sleep(5)
    await room.disconnect()


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "How long do I need to fast before my bloodwork?"
    asyncio.run(speak_into_room(text))
