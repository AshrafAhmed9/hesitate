"""
The actual LiveKit Agents worker entrypoint. Wires HesitateAgent
(agent/voice/hesitate_agent.py) to real Deepgram STT, real Groq LLM
(model + reasoning_effort matching the measured finding in
agent/llm/groq_client.py), and TTS gated by agent/voice/tts.py's dev/live
mode split (real ElevenLabs only when explicitly requested, since Ashraf
reserved that quota for the final demo).

STATUS (updated after a real live test, 2026-09-13): constructs without
error. Confirmed LIVE and working: connects to a real LiveKit room via
`connect --room <name>`, silero.VAD loads, a real Deepgram STT WebSocket
connection is established against the real project. Tested with
scripts/synthetic_caller.py (a synthetic participant publishing real,
locally-synthesized speech via macOS `say` + ffmpeg -- zero cost, no
human needed).

UNRESOLVED GAP, found and NOT yet fixed: no transcript or turn-taking
event was ever observed after the Deepgram WebSocket connected, across
multiple runs and a 50-second window. The STT connection is real; the
audio frames from the synthetic caller are likely malformed or
misaligned at the byte/frame level (rtc.AudioFrame constructed directly
from raw PCM bytes in scripts/synthetic_caller.py, rather than via a
verified-correct construction path) -- a real browser's WebRTC mic
capture would not have this problem, since the browser's own audio
pipeline handles framing correctly. This needs either fixing the raw
frame construction or testing via an actual browser (call.html) instead.
Not silently claimed as working; not spent further time guessing at
binary frame internals per instruction to stop and report when stuck.
One thing ruled out: AudioFrame byte layout itself is correct (verified
nbytes=640 for 320 int16 samples, itemsize=2, format='h') -- the bug is
elsewhere, likely in capture_frame() timing/pacing or how the published
track is actually being consumed server-side, not in frame construction.

Run with: python -m agent.voice.entrypoint dev   (LiveKit's own dev-mode CLI)
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from livekit.agents import AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, elevenlabs, groq as groq_plugin, silero

from agent.voice.guarded_tts import GuardedTTS
from agent.voice.hesitate_agent import HesitateAgent
from corpus.policy_records import RECORDS

load_dotenv()

SYSTEM_PROMPT = (
    "You are a clinic front-desk voice assistant. Answer questions about fasting "
    "instructions, arrival time, insurance coverage, cost, and required documents. "
    "Be brief -- one or two sentences."
)


def build_session() -> AgentSession:
    """Real providers, matching the measured findings elsewhere in this repo:
    Groq's gpt-oss-20b with reasoning_effort='low' (agent/llm/groq_client.py),
    Deepgram nova-3 STT, ElevenLabs TTS. TTS quota discipline (dev vs live
    mode) lives in agent/voice/tts.py and is NOT yet wired into this
    AgentSession path -- the LiveKit plugin calls ElevenLabs directly. Using
    this entrypoint against a real room WILL spend the reserved ElevenLabs
    quota; that wiring gap is tracked in COMPETITION.md, not hidden."""
    return AgentSession(
        stt=deepgram.STT(model="nova-3", api_key=os.environ["DEEPGRAM_API_KEY"]),
        # REAL FINDING: without VAD, AgentSession never detected the end of
        # the caller's speech as a completed turn, so the LLM node never
        # fired -- confirmed by a live test with scripts/synthetic_caller.py
        # where the worker joined and closed the session on disconnect with
        # no transcript/turn activity in between. silero.VAD closes that gap.
        vad=silero.VAD.load(),
        llm=groq_plugin.LLM(
            model="openai/gpt-oss-20b",
            api_key=os.environ["GROQ_API_KEY"],
            reasoning_effort="low",
        ),
        # Wrapped in GuardedTTS: real ElevenLabs is only called when
        # HESITATE_TTS_MODE=live is set explicitly. Default is silent
        # dev mode, so running this entrypoint against a real room never
        # accidentally spends the quota reserved for the final demo.
        tts=GuardedTTS(elevenlabs.TTS(api_key=os.environ["ELEVENLABS_API_KEY"])),
    )


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    session = build_session()
    agent = HesitateAgent(instructions=SYSTEM_PROMPT, policy_records=RECORDS)
    await session.start(agent=agent, room=ctx.room)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
