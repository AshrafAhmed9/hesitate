"""
Joins a real LiveKit room as a caller, types one question into the agent
(the same lk.chat path the call page's text box uses) and prints the trace
events the browser renders. Usage:

    python -m scripts.text_caller "How long do I need to fast?"            # protection ON
    python -m scripts.text_caller "How long do I need to fast?" --off      # baseline, gate off
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid

from dotenv import load_dotenv
from livekit import rtc

from agent.voice.token import issue_room_token

load_dotenv()


async def ask(question: str, protection: bool = True, wait_s: float = 25.0) -> list[dict]:
    room_name = ("hesitate-call-" if protection else "baseline-") + uuid.uuid4().hex[:8]
    token = issue_room_token(room_name, f"text-caller-{uuid.uuid4().hex[:6]}")
    room = rtc.Room()
    events: list[dict] = []
    got_sentence = asyncio.Event()
    ready = asyncio.Event()

    @room.on("data_received")
    def _on_data(pkt: rtc.DataPacket):
        if pkt.topic == "hesitate-trace":
            ev = json.loads(pkt.data.decode())
            events.append(ev)
            if ev["t"] == "ready":
                ready.set()
            if ev["t"] == "sentence":
                got_sentence.set()

    await room.connect(os.environ["LIVEKIT_URL"], token)
    await asyncio.wait_for(ready.wait(), 40)  # agent announces itself once its session is listening
    await room.local_participant.send_text(question, topic="lk.chat")
    try:
        await asyncio.wait_for(got_sentence.wait(), wait_s)
        await asyncio.sleep(1.5)
    except asyncio.TimeoutError:
        pass
    await room.disconnect()
    return events


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "How long do I need to fast before my bloodwork?"
    for ev in asyncio.run(ask(q, protection="--off" not in sys.argv)):
        print(json.dumps(ev, indent=2))
