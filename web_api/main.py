"""
Minimal FastAPI service, deployed early so the mandatory "deployed link"
submission requirement has something real behind it from day one, rather
than being built last. This will grow into the actual dashboard API as
the voice loop is built; every route here does something real.
"""
import asyncio
import os
import sys
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Hesitate")

# The LiveKit agent worker (agent/voice/entrypoint.py) is NOT deployed
# here or anywhere on Render. It was tried three ways on Render's free
# tier -- as a subprocess of this service, after trimming torch/
# sentence-transformers out of the deploy deps, and in its own
# dedicated free-tier service -- and crash-looped every time (~45-90s
# restart cycle); the plugin stack (deepgram+elevenlabs+groq+silero)
# simply doesn't fit free-tier RAM for more than about a minute. See
# agent/voice/entrypoint.py's docstring for the full finding. Per
# Ashraf's decision, the worker runs from a local machine for demos and
# the live finale instead of a paid Render plan; this deployed service
# still serves call.html, issues tokens, and demonstrates the
# verification gate against live Moss (/gate/live-demo) on its own.


@app.get("/")
def root():
    return {
        "project": "Hesitate",
        "status": "gate implemented and tested; voice pipeline in progress",
        "repo": "https://github.com/AshrafAhmed9/hesitate",
        "call": "/call.html",
    }


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})


@app.get("/gate/demo")
def gate_demo():
    """Runs the real verification gate against the real bug scenario, so
    the deployed link demonstrates actual behavior, not a static page."""
    from agent.gate.verify import verify_sentence
    from corpus.policy_records import RECORDS

    sentence = "You'll need to fast for twelve hours before the test."
    result = verify_sentence(sentence, RECORDS)
    return {
        "input_sentence": sentence,
        "decision": result.sentence_decision.value,
        "disposition": result.disposition,
        "spoken_output": result.replacement_text,
        "gate_latency_ms": result.stage_timings_ms["total_ms"],
    }


@app.get("/token")
def get_token(room: Optional[str] = None):
    """Issues a short-lived, room-scoped LiveKit token for the browser
    client. the design spec section 3: the API secret never leaves the server.

    REAL BUG (2026-09-20): a fixed default room name ('hesitate-demo')
    meant every test session -- synthetic caller, browser calls, manual
    `connect --room` runs, all day -- reused the same room. After enough
    forceful worker restarts, LiveKit's automatic-dispatch record for
    that specific room got stuck referencing a dead worker process, so a
    freshly restarted worker registered fine but never received a job
    for that room -- the browser call connected but nothing happened,
    with no error surfaced anywhere. A fresh, unique room name per call
    sidesteps the whole class of problem: no stale dispatch to inherit."""
    room = room or f"hesitate-call-{uuid.uuid4().hex[:8]}"
    try:
        from agent.voice.token import issue_room_token
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"token service unavailable: {e}")
    identity = f"caller-{uuid.uuid4().hex[:8]}"
    token = issue_room_token(room, identity)
    return {
        "token": token,
        "url": os.environ.get("LIVEKIT_URL", ""),
        "room": room,
        "identity": identity,
    }


# Policy Desk: live policy edits for the demo. Off unless HESITATE_DESK=1, so the
# public Render deployment cannot be used to rewrite anything.
_desk_lock = asyncio.Lock()


def _require_desk():
    if os.environ.get("HESITATE_DESK") != "1":
        raise HTTPException(status_code=404, detail="policy desk is only enabled on the demo machine")


def _moss():
    from moss import MossClient
    return MossClient(os.environ["MOSS_PROJECT_ID"], os.environ["MOSS_PROJECT_KEY"])


class PolicyChange(BaseModel):
    attribute: str
    value: float


class PoisonDoc(BaseModel):
    text: str = Field(min_length=3, max_length=300)


@app.get("/desk")
def desk_state():
    _require_desk()
    from corpus.desk import load_entries, POLICY_FIELDS
    return {"entries": load_entries(), "attributes": sorted(POLICY_FIELDS)}


@app.post("/policy")
async def publish_policy(change: PolicyChange):
    """An approved change: supersedes the current record and is indexed in Moss."""
    _require_desk()
    from corpus.desk import load_entries, save_entries, validate_policy, apply_entries
    from corpus.policy_records import RECORDS
    from datetime import datetime
    from moss import DocumentInfo
    try:
        value = validate_policy(change.attribute, change.value)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    async with _desk_lock:
        entries = load_entries()
        entry = {"kind": "policy", "attribute": change.attribute, "value": value,
                 "at": datetime.now().isoformat()}
        _, docs = apply_entries(RECORDS, entries + [entry])
        new_doc = docs[-1]
        await _moss().add_docs("hesitate-clinic", [DocumentInfo(id=new_doc["id"], text=new_doc["text"])])
        save_entries(entries + [entry])  # written last: the worker reloads Moss when this changes
    return {"published": new_doc["text"], "moss_doc": new_doc["id"]}


@app.post("/poison")
async def drop_unapproved(doc: PoisonDoc):
    """An unapproved document: Moss will retrieve it, but no policy record backs it."""
    _require_desk()
    from corpus.desk import load_entries, save_entries
    from moss import DocumentInfo
    async with _desk_lock:
        entries = load_entries()
        entry = {"kind": "poison", "text": doc.text.strip()}
        doc_id = f"judge_upload_{len(entries) + 1}.txt#note"
        await _moss().add_docs("hesitate-clinic", [DocumentInfo(id=doc_id, text=entry["text"])])
        save_entries(entries + [entry])
    return {"indexed": entry["text"], "moss_doc": doc_id}


@app.post("/desk/reset")
async def reset_desk():
    _require_desk()
    from corpus.desk import load_entries, save_entries, apply_entries
    from corpus.policy_records import RECORDS
    async with _desk_lock:
        _, docs = apply_entries(RECORDS, load_entries())
        if docs:
            await _moss().delete_docs("hesitate-clinic", [d["id"] for d in docs])
        save_entries([])
    return {"reset": True, "removed": len(docs)}


@app.get("/proof")
def proof():
    """Serves the committed result of `python -m bench.run_live_ab` so the call page can show it."""
    import json
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bench", "results", "live_ab.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="run python -m bench.run_live_ab first")
    with open(path) as f:
        return json.load(f)


@app.get("/gate/live-demo")
def gate_live_demo():
    """Same scenario as /gate/demo, but using the REAL live Moss service
    for retrieval instead of the fixture RECORDS list directly -- this is
    what satisfies 'required sponsor integration actually runs in the
    deployed workflow' rather than only in local tests. Requires
    MOSS_PROJECT_ID/MOSS_PROJECT_KEY set on the deployed service."""
    try:
        from agent.retrieval.live_moss import LiveMossClient
        from agent.retrieval.adapter import retrieve_candidate_records
        from agent.gate.extract import extract_claims
        from agent.gate.resolve import resolve_claim
        from agent.gate.correct import build_sentence_correction
        from agent.gate.schema import AtomicVerdict
        from corpus.policy_records import RECORDS
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"live Moss demo unavailable: {e}")

    sentence = "You'll need to fast for twelve hours before the test."
    try:
        client = LiveMossClient()
        client.load_index("hesitate-test")
        candidates = retrieve_candidate_records(client, "hesitate-test", "how long do I need to fast?", RECORDS, top_k=5)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"live Moss query failed: {e}")

    claims = extract_claims(sentence)
    if not claims:
        return {"input_sentence": sentence, "error": "no claim extracted"}
    decision, evidence_ids, reason, record = resolve_claim(claims[0], candidates)
    verdict = AtomicVerdict(claims[0], decision, evidence_ids, reason, resolved_record=record)
    replacement = build_sentence_correction((verdict,)) if decision.value == "contradicted" else sentence

    return {
        "input_sentence": sentence,
        "moss_index": "hesitate-test",
        "moss_candidates_retrieved": sorted(set(c.source_id for c in candidates)),  # dedup: one source doc can back multiple curated records
        "decision": decision.value,
        "spoken_output": replacement,
        "note": "This query hit the real Moss service, not a local fixture.",
    }


_static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

    @app.get("/call.html")
    def call_page():
        return FileResponse(os.path.join(_static_dir, "call.html"))
