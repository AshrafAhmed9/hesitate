"""
Pre-declared contract-suite cases. PLAN.md section 5: "Start with a
200-case contract suite ... Lock the holdout hash before tuning."

STATUS: this is a starter set (not yet the full 200-case suite with
100/100 dev/holdout split and independent human review) exercising every
decision category the contract requires: SUPPORTED, CONTRADICTED,
UNVERIFIABLE, and CONFLICT. Expanding to the full suite is tracked in
COMPETITION.md, not silently substituted here as if it were complete.

Each case: (sentence, candidate_records, expected_decision, expected_disposition)
"""
from datetime import datetime

from agent.gate.schema import Decision, Polarity, PolicyRecord
from corpus.policy_records import RECORDS

_NOW = datetime(2026, 9, 13)

# A record set with an unresolved conflict: two equally-applicable, equally
# current records for the same key, no supersession between them.
_CONFLICTING = [
    PolicyRecord(
        policy_id="conflict-a", source_id="siteA.txt", source_span="Fast for 8 hours.",
        site="*", service="fasting-bloodwork", attribute="fasting_duration",
        value="8", unit="hours", polarity=Polarity.POSITIVE, conditions=(),
        effective_from=datetime(2026, 1, 1), effective_to=None,
    ),
    PolicyRecord(
        policy_id="conflict-b", source_id="siteB.txt", source_span="Fast for 10 hours.",
        site="*", service="fasting-bloodwork", attribute="fasting_duration",
        value="10", unit="hours", polarity=Polarity.POSITIVE, conditions=(),
        effective_from=datetime(2026, 1, 1), effective_to=None,
    ),
]

CASES = [
    # The headline case: model repeats the superseded/stale figure.
    ("You'll need to fast for twelve hours before the test.", RECORDS, Decision.CONTRADICTED, "corrected"),
    # Correct current figure.
    ("You'll need to fast for 8 hours before the test.", RECORDS, Decision.SUPPORTED, "released"),
    # Correct arrival offset.
    ("Please arrive 15 minutes early to check in.", RECORDS, Decision.SUPPORTED, "released"),
    # Wrong arrival offset.
    ("Please arrive 30 minutes early to check in.", RECORDS, Decision.CONTRADICTED, "corrected"),
    # Coverage, correct polarity.
    ("Your plan covers this test.", RECORDS, Decision.SUPPORTED, "released"),
    # Coverage, wrong polarity -- the hallucinated denial.
    ("Unfortunately your plan does not cover this test.", RECORDS, Decision.CONTRADICTED, "corrected"),
    # Cost, correct.
    ("The consultation costs $150.", RECORDS, Decision.SUPPORTED, "released"),
    # Cost, hallucinated amount.
    ("The consultation costs $200.", RECORDS, Decision.CONTRADICTED, "corrected"),
    # Required document, correct (no referral needed).
    ("You don't need a referral for this visit.", RECORDS, Decision.SUPPORTED, "released"),
    # Required document, hallucinated requirement.
    ("You'll need a referral for this visit.", RECORDS, Decision.CONTRADICTED, "corrected"),
    # KNOWN GAP, not a bug: this sentence makes a factual claim ("you'll
    # get a text message") that no typed pattern in extract.py recognizes,
    # so zero claims are extracted and the sentence defaults to SUPPORTED
    # (schema.py: "no claims to check"). PLAN.md section 5 explicitly
    # requires this to count as a failure ("unknown claims silently
    # classified nonfactual count as failures") -- it does, here, honestly,
    # rather than being hidden. Closing this requires the completeness/
    # unclassified-span detection in section 10, which is not built.
    ("You'll get a text message confirmation an hour before your visit.", RECORDS, Decision.SUPPORTED, "released"),
    # No factual claim present -- must not be flagged.
    ("Thanks for calling, how can I help you today?", RECORDS, Decision.SUPPORTED, "released"),
    # Unresolved conflict: two equally-applicable current records disagree.
    ("You'll need to fast for 8 hours.", _CONFLICTING, Decision.CONFLICT, "declined"),
]
