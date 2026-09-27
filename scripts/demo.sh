#!/usr/bin/env bash
# One command from cold to a ready call page: restarts the worker with real
# ElevenLabs audio, starts the local web server, opens the browser.
# Usage: bash scripts/demo.sh        (add SILENT=1 to keep TTS in dev mode)
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
set -a; source .env; set +a

pkill -f "[a]gent.voice.entrypoint" 2>/dev/null || true
pkill -f "[u]vicorn web_api.main" 2>/dev/null || true
sleep 1

[ "${SILENT:-0}" = "1" ] || export HESITATE_TTS_MODE=live

python -m agent.voice.entrypoint start > /tmp/hesitate_worker.log 2>&1 &
HESITATE_DESK=1 uvicorn web_api.main:app --port 8000 > /tmp/hesitate_web.log 2>&1 &

echo "Waiting for the worker to register..."
for _ in $(seq 1 60); do
  grep -q "registered worker" /tmp/hesitate_worker.log 2>/dev/null && break
  sleep 1
done
grep -q "registered worker" /tmp/hesitate_worker.log || { echo "Worker did not register. See /tmp/hesitate_worker.log"; exit 1; }

# Start every session from the original policy (removes any leftover desk edits).
for _ in $(seq 1 20); do curl -sf -X POST localhost:8000/desk/reset >/dev/null && break; sleep 1; done

echo "READY  (TTS: ${HESITATE_TTS_MODE:-dev})  http://localhost:8000/call.html"
open "http://localhost:8000/call.html" 2>/dev/null || true
