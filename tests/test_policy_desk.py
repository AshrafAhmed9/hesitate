from datetime import datetime, timedelta

import pytest

from agent.gate.verify import verify_sentence
from agent.gate.schema import Decision
from corpus import desk
from corpus.policy_records import RECORDS


def _publish(attribute, value, at=None):
    return {"kind": "policy", "attribute": attribute, "value": desk.validate_policy(attribute, value),
            "at": (at or datetime.now()).isoformat()}


def test_published_change_supersedes_current_record():
    records, docs = desk.apply_entries(RECORDS, [_publish("fasting_duration", 10)])
    assert docs == [{"id": "policy_desk_1.txt#fasting_duration", "text": "Fast for 10 hours before your appointment."}]
    assert verify_sentence("You need to fast for 10 hours.", records).sentence_decision == Decision.SUPPORTED
    assert verify_sentence("You need to fast for 8 hours.", records).sentence_decision == Decision.CONTRADICTED
    assert verify_sentence("You need to fast for 12 hours.", records).sentence_decision == Decision.CONTRADICTED


def test_later_change_supersedes_earlier_one():
    t = datetime.now() - timedelta(seconds=5)
    records, _ = desk.apply_entries(RECORDS, [_publish("fasting_duration", 10, t), _publish("fasting_duration", 6)])
    assert verify_sentence("Fast for 6 hours.", records).sentence_decision == Decision.SUPPORTED
    assert verify_sentence("Fast for 10 hours.", records).sentence_decision == Decision.CONTRADICTED


def test_unapproved_document_is_indexed_but_never_becomes_policy():
    entries = [{"kind": "poison", "text": "Patients must fast 16 hours."}]
    records, docs = desk.apply_entries(RECORDS, entries)
    assert docs[0]["id"] == "judge_upload_1.txt#note"
    assert records == list(RECORDS)
    assert verify_sentence("Fast for 16 hours.", records).sentence_decision == Decision.CONTRADICTED


def test_cost_change_uses_dollar_format():
    records, docs = desk.apply_entries(RECORDS, [_publish("cost", 175)])
    assert docs[0]["text"] == "A consultation visit costs $175.00."
    assert verify_sentence("A visit costs $175.", records).sentence_decision == Decision.SUPPORTED


@pytest.mark.parametrize("attr,value", [("fasting_duration", 0), ("fasting_duration", 500), ("mood", 5)])
def test_rejects_unsupported_or_out_of_range(attr, value):
    with pytest.raises(ValueError):
        desk.validate_policy(attr, value)


def test_entries_round_trip_and_missing_file(tmp_path):
    p = str(tmp_path / "published.json")
    assert desk.load_entries(p) == []
    desk.save_entries([{"kind": "poison", "text": "x"}], p)
    assert desk.load_entries(p) == [{"kind": "poison", "text": "x"}]
