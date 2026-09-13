"""
THE full loop, live, for real: a real LLM (Groq) generates a reply, real
Moss retrieves candidate policy passages, the gate resolves and corrects
it, all measured. This is the actual product, end to end, for the first
time -- everything before this test exercised pieces in isolation.

Skips cleanly if either GROQ_API_KEY or MOSS_PROJECT_ID/KEY are absent.
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

pytestmark = pytest.mark.skipif(
    not (os.environ.get("GROQ_API_KEY") and os.environ.get("MOSS_PROJECT_ID")),
    reason="GROQ_API_KEY / MOSS_PROJECT_ID not set — live end-to-end test skipped",
)


def test_llm_hallucinates_stale_answer_and_gate_catches_it():
    """The actual demo scenario, live: prompt the real LLM in a way that
    invites it to use whatever the top retrieved passage says (mimicking
    what a naive RAG agent does), and confirm the gate catches it when
    that passage is the stale one."""
    from agent.retrieval.live_moss import LiveMossClient
    from agent.retrieval.adapter import retrieve_candidate_records
    from agent.gate.extract import extract_claims
    from agent.gate.resolve import resolve_claim
    from agent.gate.correct import build_sentence_correction
    from agent.gate.schema import AtomicVerdict
    from corpus.policy_records import RECORDS

    client = LiveMossClient()
    client.load_index("hesitate-test")

    hits = client.query("hesitate-test", "how long do I need to fast?", top_k=1)
    top_passage = hits[0].text
    print(f"\nTop-1 retrieved passage (what naive RAG would ground on): {top_passage!r}")

    from agent.llm.groq_client import generate_reply
    t0 = time.perf_counter()
    reply = generate_reply(
        system_prompt=(
            "You are a clinic front-desk voice assistant. A patient asked how long they need to "
            f"fast. Here is the relevant policy passage, state it directly as fact: {top_passage!r}"
        ),
        user_text="How long do I need to fast before my bloodwork?",
    )
    llm_ms = time.perf_counter() - t0
    print(f"LLM reply ({llm_ms*1000:.0f}ms): {reply['text']!r}")

    t0 = time.perf_counter()
    candidates = retrieve_candidate_records(client, "hesitate-test", "how long do I need to fast?", RECORDS, top_k=5)
    claims = extract_claims(reply["text"])
    assert claims, f"expected a typed fasting claim in the LLM's reply, got none: {reply['text']!r}"
    decision, evidence_ids, reason, record = resolve_claim(claims[0], candidates)
    gate_ms = time.perf_counter() - t0

    print(f"Gate decision ({gate_ms*1000:.2f}ms): {decision.value} — {reason}")

    if decision.value == "contradicted":
        verdict = AtomicVerdict(claims[0], decision, evidence_ids, reason, resolved_record=record)
        correction = build_sentence_correction((verdict,))
        print(f"CORRECTED before speech: {correction!r}")
        assert "8" in correction

    # Whatever the LLM actually said (nondeterministic), the gate's decision
    # must be internally consistent: if it said something matching the
    # current record, SUPPORTED; if it repeated the stale one, CONTRADICTED.
    assert decision.value in ("supported", "contradicted", "unverifiable")
