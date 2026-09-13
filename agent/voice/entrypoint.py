"""
The actual LiveKit Agents worker entrypoint. Wires HesitateAgent
(agent/voice/hesitate_agent.py) to real Deepgram STT, real Groq LLM
(model + reasoning_effort matching the measured finding in
agent/llm/groq_client.py), and TTS gated by agent/voice/tts.py's dev/live
mode split (real ElevenLabs only when explicitly requested, since Ashraf
reserved that quota for the final demo).

STATUS: constructs without error (verified below); has NOT been run
against a live LiveKit room with a real participant yet -- that requires
a browser client to join and speak, which does not exist yet. This is an
honestly-labeled gap, not a claim of end-to-end voice completion.

Run with: python -m agent.voice.entrypoint dev   (LiveKit's own dev-mode CLI)
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from livekit.agents import AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, elevenlabs, groq as groq_plugin

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
        llm=groq_plugin.LLM(
            model="openai/gpt-oss-20b",
            api_key=os.environ["GROQ_API_KEY"],
            reasoning_effort="low",
        ),
        tts=elevenlabs.TTS(api_key=os.environ["ELEVENLABS_API_KEY"]),
    )


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    session = build_session()
    agent = HesitateAgent(instructions=SYSTEM_PROMPT, policy_records=RECORDS)
    await session.start(agent=agent, room=ctx.room)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
