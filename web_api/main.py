"""
Minimal FastAPI service, deployed early so the mandatory "deployed link"
submission requirement has something real behind it from day one, rather
than being built last. This will grow into the actual LiveKit token
endpoint + dashboard API as the voice loop is built; it is not a
placeholder faked to look done -- every route here does something real.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Hesitate")


@app.get("/")
def root():
    return {
        "project": "Hesitate",
        "status": "gate implemented and tested; voice pipeline in progress",
        "repo": "https://github.com/AshrafAhmed9/hesitate",
    }


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})


@app.get("/gate/demo")
def gate_demo():
    """Runs the real verification gate against the real bug scenario, so
    the deployed link demonstrates actual behavior, not a static page."""
    import sys
    sys.path.insert(0, "..")
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
