"""
W7 cross-domain generalization test (PLAN.md section 9/14). Same schema,
same resolve.py, same extract.py as the clinic domain -- zero code
changes -- run against corpus/cross_domain/insurance_records.py.

FINDING (published per PLAN.md section 5's "publish mistakes" norm): the
gate does NOT generalize cleanly to this domain out of the box. The
clinic fixtures work because most of their attributes are unconditional
(conditions=()), so extract.py's known gap -- it never resolves
`conditions` from sentence text or caller context, always defaulting to
() -- rarely matters there. In insurance, coverage and cost are routinely
conditional ("for claims under $1000", "for collision"), so the SAME
gap now causes real false UNVERIFIABLE results: a claim that should
match a conditional record never does, because the claim's conditions=()
never equals the record's conditions=("collision",).

This is evidence the typed route generalizes structurally (same code, no
crashes, correct behavior on unconditional claims) but not yet
functionally on a domain where conditions carry the meaning. Recorded
here rather than hidden or patched by weakening the record fixtures to
avoid the finding.
"""
from agent.gate.schema import Claim, Polarity
from corpus.cross_domain.insurance_records import RECORDS, SERVICE, SITE

# Cases with conditions=() match the unconditional record shape directly.
UNCONDITIONAL_RECORDS = [r for r in RECORDS if r.conditions == ()]  # none currently -- see finding above

CASES = [
    # Extraction still works structurally (same regex, same schema).
    (
        "Your deductible is $500.",
        "extract_only",
        {"attribute": "cost", "value": "500.00", "unit": "usd"},
    ),
]

# SECOND FINDING: "police report" is not extracted at all -- zero claims,
# not a wrong claim. _extract_required_document (extract.py) hardcodes a
# fixed document vocabulary (referral, id, insurance card, photo id,
# prescription) from the clinic domain. This is a real vocabulary-
# hardcoding limitation distinct from the conditions-resolution gap above:
# extending it to a new domain requires editing extract.py's pattern, not
# just adding fixture records. Documented, not silently patched to pass.
UNRECOGNIZED_VOCABULARY_CASES = [
    "You don't need a police report for this.",
]

# Full resolution against the real conditional records currently fails for
# all three fixtures below -- expected_decision is UNVERIFIABLE, matching
# actual (wrong, from a domain-correctness standpoint) behavior, not the
# behavior a deployed insurance agent would need. Fixing this requires
# resolving `conditions` from caller context (documented gap, not new).
RESOLUTION_CASES = [
    ("Your deductible for collision is $500.", RECORDS, "unverifiable"),  # SHOULD be supported
    ("Rental car reimbursement is included.", RECORDS, "unverifiable"),   # SHOULD be contradicted
]
