"""
Minimal FastAPI service, deployed early so the mandatory "deployed link"
submission requirement has something real behind it from day one, rather
than being built last. This will grow into the actual dashboard API as
the voice loop is built; every route here does something real.
"""
import os
import sys
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Hesitate")

# The LiveKit agent worker runs as its own deployed service
# (worker_service/main.py), not as a subprocess of this one. Running
# both FastAPI and a full livekit-agents worker in one Render free-tier
# container (512MB) OOM-crash-looped even after trimming torch/
# sentence-transformers out of the deployed deps -- see
# requirements-deploy.txt and worker_service/main.py's docstring for
# the real findings. Splitting them into two free-tier services (each
# gets its own 512MB) fixed it without paying for a bigger plan.


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
def get_token(room: str = "hesitate-demo"):
    """Issues a short-lived, room-scoped LiveKit token for the browser
    client. PLAN.md section 3: the API secret never leaves the server."""
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
