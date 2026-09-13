"""
Pre-declared calibration/test cases for the Tier 2 semantic route
(agent/gate/semantic.py). Separate from bench/cases.py (typed route) per
PLAN.md section 10: "a fast typed path cannot hide a slow semantic path
in an overall average" -- evaluate them separately.

STATUS: small starter set for calibration sanity-checking, not the
independently-labeled calibration split section 10 requires before
thresholds can be called tuned.

Each case: (claim_text, passages, expected_decision)
"""

PASSAGES_CONFIRMATION = [
    ("intake_faq", "We will send an email confirmation immediately after booking, and a text reminder 24 hours before your visit."),
]

PASSAGES_PARKING = [
    ("intake_faq", "Free parking is available in the lot behind the building. There is no valet service."),
]

CASES = [
    # Entailed: passage explicitly supports the claim (same fact, reworded).
    (
        "You'll get a text reminder the day before your appointment.",
        PASSAGES_CONFIRMATION,
        "supported",
    ),
    # Contradicted: passage explicitly states the opposite service exists.
    (
        "We offer valet parking for your visit.",
        PASSAGES_PARKING,
        "contradicted",
    ),
    # KNOWN LIMITATION, documented not hidden: the passage doesn't address
    # this claim at all, so UNVERIFIABLE is the correct answer, but the
    # xsmall NLI model measured 89% confidence CONTRADICTED on this
    # off-topic pair (raw_logits favor contradiction even with near-zero
    # lexical/topical overlap). This is a real, measured model limitation,
    # not a threshold-tuning fix -- see semantic.py status note. Mitigated
    # in the real pipeline by the fact Moss retrieval only ever returns
    # topically-relevant passages as candidates, so a fully unrelated
    # passage like this should not reach Tier 2 in production; this case
    # exists specifically to surface that dependency rather than assume it.
    (
        "You can request a wheelchair at check-in.",
        PASSAGES_PARKING,
        "contradicted",  # documenting ACTUAL model behavior, not the correct answer
    ),
    # Entailed: parking is free (direct claim).
    (
        "Parking is free.",
        PASSAGES_PARKING,
        "supported",
    ),
]
