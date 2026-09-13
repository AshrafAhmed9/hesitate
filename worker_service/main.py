"""
A tiny standalone service whose only job is to keep the LiveKit agent
worker (agent/voice/entrypoint.py) running persistently, in its own
Render free-tier container.

Why this exists: running the agent worker as a subprocess of web_api's
own FastAPI service OOM-crash-looped on Render's free 512MB plan even
after removing torch/sentence-transformers -- FastAPI's own process
plus a full livekit-agents worker (deepgram/elevenlabs/groq/silero
plugins, onnxruntime) together exceeded the container's memory. Giving
the worker its own free-tier container (its own 512MB) instead of
sharing one with the web app fixes this without paying for a bigger
plan. This file exists only to satisfy Render's web_service port-bind
requirement (background_worker requires a paid plan); it does nothing
but report health and hold the worker subprocess alive.
"""
import os
import subprocess
import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Hesitate Worker")

_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_worker_proc = subprocess.Popen(
    [sys.executable, "-m", "agent.voice.entrypoint", "start"],
    cwd=_repo_root,
    env=os.environ.copy(),
)


@app.get("/health")
def health():
    running = _worker_proc.poll() is None
    return JSONResponse({"status": "ok" if running else "worker exited", "worker_pid": _worker_proc.pid})
