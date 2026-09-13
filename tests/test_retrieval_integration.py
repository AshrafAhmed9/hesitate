"""
End-to-end integration test: caller question -> mock Moss retrieval ->
adapter maps hits back to curated PolicyRecords -> resolve -> correct.

This is the first test that exercises retrieval at all (every other test
hands resolve_claim a pre-selected record list directly). It proves the
adapter wiring works; it does NOT prove anything about the real Moss
service, since MockMossClient is a local embedding stand-in — see
agent/retrieval/mock_moss.py's status note.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

pytest.importorskip("sentence_transformers")

from agent.gate.extract import extract_claims
from agent.gate.resolve import resolve_claim
from agent.gate.correct import build_sentence_correction
from agent.retrieval.adapter import build_index_docs, retrieve_candidate_records
from agent.retrieval.mock_moss import MockMossClient
from corpus.policy_records import RECORDS


@pytest.fixture(scope="module")
def client():
    c = MockMossClient()
    c.create_index("clinic-policy", build_index_docs(RECORDS))
    c.load_index("clinic-policy")
    return c


def test_stale_fasting_claim_caught_via_retrieval(client):
    sentence = "You'll need to fast for twelve hours before the test."
    candidates = retrieve_candidate_records(client, "clinic-policy", sentence, RECORDS, top_k=5)
    assert any(r.source_id == "prep_current.txt" for r in candidates), (
        "retrieval must surface the CURRENT prep sheet, not only the stale one, "
        "or the contradiction can never be detected"
    )
    claims = extract_claims(sentence)
    assert len(claims) == 1
    decision, evidence_ids, reason, record = resolve_claim(claims[0], candidates)
    assert decision.value == "contradicted"
    assert record.value == "8"  # the current record, not the hallucinated 12


def test_correct_fasting_claim_released_via_retrieval(client):
    sentence = "You'll need to fast for 8 hours before the test."
    candidates = retrieve_candidate_records(client, "clinic-policy", sentence, RECORDS, top_k=5)
    claims = extract_claims(sentence)
    decision, evidence_ids, reason, record = resolve_claim(claims[0], candidates)
    assert decision.value == "supported"


def test_unrelated_question_retrieves_no_matching_record(client):
    sentence = "What's the weather like today?"
    candidates = retrieve_candidate_records(client, "clinic-policy", sentence, RECORDS, top_k=2)
    claims = extract_claims(sentence)
    assert claims == []  # no typed claim in this sentence at all
