"""
W7 cross-domain generalization pack — PLAN.md section 9: "Fictional
insurance servicing policy pack using the same core and explicit
adaptation contract... Run coverage limits, deadlines, required
documents, exceptions, and ambiguous applicability cases."

Uses the SAME schema (PolicyRecord), SAME resolve.py, SAME extract.py --
no code changes. This is the point: if the gate genuinely generalizes,
these records plug in unmodified. All fictional/synthetic.

Adaptation contract: attribute names below reuse the existing typed
extractors (cost, coverage, requires_*) where the domain maps directly;
"claim deadline days" is a NEW attribute this pack introduces to test
whether the core generalizes to an attribute it wasn't built for --
STATUS: extract.py has no pattern for it, so claims about it will
currently be UNVERIFIABLE. This is an honest generalization gap, not
concealed.
"""
from datetime import datetime

from agent.gate.schema import Polarity, PolicyRecord

SITE = "*"
SERVICE = "auto-claims"

RECORDS = [
    PolicyRecord(
        policy_id="ins-deductible",
        source_id="policy_terms.txt",
        source_span="Your deductible for collision claims is $500.",
        site=SITE, service=SERVICE, attribute="cost",
        value="500.00", unit="usd", polarity=Polarity.POSITIVE, conditions=("collision",),
        effective_from=datetime(2026, 1, 1), effective_to=None,
    ),
    PolicyRecord(
        policy_id="ins-coverage-rental",
        source_id="policy_terms.txt",
        source_span="Rental car reimbursement is not included in the standard plan.",
        site=SITE, service=SERVICE, attribute="coverage",
        value="covered", unit=None, polarity=Polarity.NEGATIVE, conditions=("rental_reimbursement",),
        effective_from=datetime(2026, 1, 1), effective_to=None,
    ),
    PolicyRecord(
        policy_id="ins-required-doc",
        source_id="claims_faq.txt",
        source_span="You do not need a police report for claims under $1000.",
        site=SITE, service=SERVICE, attribute="requires_police_report",
        value="true", unit=None, polarity=Polarity.NEGATIVE, conditions=("claim_under_1000",),
        effective_from=datetime(2026, 1, 1), effective_to=None,
    ),
]
