"""Phrasings a caller or judge might plausibly try. Each of the wrong ones
passed the gate as 'nothing to check' before the extractor learned spoken
quantities; the right ones must not be blocked."""
import pytest

from agent.gate.schema import Decision
from agent.gate.verify import verify_sentence
from corpus.policy_records import RECORDS

WRONG = [
    "You need to fast for twelve hours before the test.",
    "Fast for half a day before the test.",
    "Please fast for one day.",
    "Fast for 720 minutes before the test.",
    "Please arrive half an hour before your appointment.",
    "Get there an hour early.",
    "The visit is two hundred dollars.",
    "A consultation costs $200.",
    "A referral is required for bloodwork.",
    "You will need a referral from your doctor.",
    "This test isn't covered by your plan.",
    "**Fast for 12 hours** before your appointment.",
]

UNSURE = [
    "You should fast for 8 to 12 hours.",
    "Fast for 12-hours before your appointment.",
    "Fasting is required for about 12 hours.",
]

RIGHT = [
    "Fast for 8 hours before your appointment.",
    "Please fast for eight hours.",
    "Arrive 15 minutes early to complete check-in.",
    "A consultation visit costs $150.",
    "It costs 150 dollars.",
    "It costs one hundred fifty dollars.",
    "You do not need a referral for a routine bloodwork visit.",
    "A referral isn't required for bloodwork.",
    "No referral is needed for a routine bloodwork visit.",
    "You'll get a text confirmation an hour before your visit.",
    "This test is covered by most insurance plans.",
]


@pytest.mark.parametrize("s", WRONG)
def test_wrong_claims_are_corrected(s):
    assert verify_sentence(s, RECORDS).sentence_decision == Decision.CONTRADICTED


@pytest.mark.parametrize("s", UNSURE)
def test_ambiguous_claims_are_never_passed_through(s):
    assert verify_sentence(s, RECORDS).sentence_decision != Decision.SUPPORTED


@pytest.mark.parametrize("s", RIGHT)
def test_correct_claims_are_not_blocked(s):
    assert verify_sentence(s, RECORDS).sentence_decision == Decision.SUPPORTED
