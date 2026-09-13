"""W7 cross-domain generalization test — see bench/cross_domain_cases.py
for the finding this documents."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.gate.extract import extract_claims
from agent.gate.resolve import resolve_claim
from bench.cross_domain_cases import CASES, RESOLUTION_CASES, UNRECOGNIZED_VOCABULARY_CASES


def test_typed_extraction_generalizes_structurally():
    """Same regex patterns, different domain, different service string --
    proves extract.py has no clinic-specific hardcoding."""
    for sentence, _, expected in CASES:
        claims = extract_claims(sentence, service="auto-claims")
        assert len(claims) == 1
        c = claims[0]
        assert c.attribute == expected["attribute"]
        assert c.value == expected["value"]


def test_unrecognized_document_vocabulary_extracts_nothing():
    """Documents the vocabulary-hardcoding finding: this is a silent
    zero-claim result, not a crash and not a wrong value -- worth knowing
    because a real deployment could silently fail to check a claim family
    the corpus never anticipated."""
    for sentence in UNRECOGNIZED_VOCABULARY_CASES:
        assert extract_claims(sentence, service="auto-claims") == []


def test_conditional_claims_currently_fail_to_resolve():
    """Documents the real, named generalization gap: condition resolution
    doesn't exist yet, so conditional records in this domain can't be
    matched. This test PASSES by confirming the known-wrong behavior,
    which is what 'publish mistakes' means -- it will need to be updated
    (not deleted) once condition resolution is built."""
    for sentence, records, expected in RESOLUTION_CASES:
        claims = extract_claims(sentence, service="auto-claims")
        assert len(claims) == 1
        decision, _, _, _ = resolve_claim(claims[0], records)
        assert decision.value == expected, (
            f"expected the DOCUMENTED gap behavior ({expected}) for {sentence!r}; "
            f"got {decision.value} -- if this now passes correctly, update this test "
            f"to assert the correct behavior and close the finding in COMPETITION.md"
        )
