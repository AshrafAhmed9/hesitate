"""Tier 2 semantic route tests. Requires .venv with sentence-transformers
installed (network access to download the model on first run)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

pytest.importorskip("sentence_transformers")

from agent.gate.semantic import verify_semantic_claim_against_passages
from bench.semantic_cases import CASES


@pytest.mark.parametrize("claim_text,passages,expected", CASES)
def test_semantic_case(claim_text, passages, expected):
    decision, _ = verify_semantic_claim_against_passages(claim_text, passages)
    assert decision.value == expected


def test_semantic_route_latency_measured_not_asserted():
    """No fixed '15ms NLI' claim without measurement (PLAN.md section 10).
    This asserts a generous ceiling to catch regressions, not a tight bound."""
    import time
    from agent.gate.semantic import verify_semantic_claim, _get_model
    _get_model()
    t0 = time.perf_counter()
    verify_semantic_claim("Parking is free.", "Free parking is available in the lot.")
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 500, f"warm semantic call took {elapsed_ms}ms"
