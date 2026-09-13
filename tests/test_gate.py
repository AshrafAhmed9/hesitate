"""
PLAN.md section 14 verification requirement: 'pytest over the case suite
with pre-declared expected verdicts; it must fail loudly when the support
threshold is wrong.'
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from agent.gate.verify import verify_sentence
from bench.cases import CASES


@pytest.mark.parametrize("sentence,records,expected_decision,expected_disposition", CASES)
def test_case(sentence, records, expected_decision, expected_disposition):
    result = verify_sentence(sentence, records)
    assert result.sentence_decision == expected_decision, (
        f"decision mismatch for {sentence!r}: got {result.sentence_decision}, want {expected_decision}"
    )
    assert result.disposition == expected_disposition


def test_contradicted_never_releases_original_text():
    """The one guarantee the whole product depends on: a contradicted
    claim's replacement_text must never equal the original wrong text."""
    from corpus.policy_records import RECORDS
    result = verify_sentence("You'll need to fast for twelve hours before the test.", RECORDS)
    assert result.disposition == "corrected"
    assert result.replacement_text != result.candidate.text
    assert "8" in result.replacement_text  # the real current value, not the hallucinated 12


def test_gate_latency_budget():
    """PLAN.md section 5 target: warm gate p95 <= 60ms. This is the typed
    route only (no Moss network round-trip, no semantic/NLI route -- both
    out of scope of this measurement, see resolve.py status note)."""
    from corpus.policy_records import RECORDS
    timings = []
    for sentence, records, _, _ in CASES:
        r = verify_sentence(sentence, records)
        timings.append(r.stage_timings_ms["total_ms"])
    timings.sort()
    p95 = timings[int(len(timings) * 0.95)]
    assert p95 < 60, f"p95={p95}ms exceeds section-5 target"
