"""
W1/W2 — canonical, manually curated PolicyRecord fixtures.

PLAN.md section 4: "Author readable synthetic passages and manually
reviewed structured records." These records are the actual authority the
gate compares against; corpus/*.txt are the natural-language source
documents Moss retrieves (source_span traces back to them). All fictional,
all synthetic -- see corpus/provenance.md.
"""
from datetime import datetime

from agent.gate.schema import PolicyRecord, Polarity

SITE = "*"  # applies to all sites in this fixture set
SERVICE = "fasting-bloodwork"

RECORDS = [
    PolicyRecord(
        policy_id="prep-2026-08-fasting",
        source_id="prep_current.txt",
        source_span="Fast for 8 hours before your appointment.",
        site=SITE, service=SERVICE, attribute="fasting_duration",
        value="8", unit="hours", polarity=Polarity.POSITIVE, conditions=(),
        effective_from=datetime(2026, 8, 1), effective_to=None,
        supersedes="prep-2024-01-fasting",
    ),
    PolicyRecord(
        policy_id="prep-2024-01-fasting",
        source_id="prep_stale.txt",
        source_span="Fast for 12 hours before your appointment.",
        site=SITE, service=SERVICE, attribute="fasting_duration",
        value="12", unit="hours", polarity=Polarity.POSITIVE, conditions=(),
        effective_from=datetime(2024, 1, 1), effective_to=datetime(2026, 8, 1),
    ),
    PolicyRecord(
        policy_id="prep-arrival",
        source_id="prep_current.txt",
        source_span="Arrive 15 minutes early to complete check-in.",
        site=SITE, service=SERVICE, attribute="arrival_offset",
        value="15", unit="minutes", polarity=Polarity.POSITIVE, conditions=(),
        effective_from=datetime(2026, 8, 1), effective_to=None,
    ),
    # NOTE on service/conditions: extract.py does not yet resolve caller
    # context (site/service/conditions) from the sentence -- it defaults
    # every claim to service="fasting-bloodwork", conditions=() (documented
    # gap in extract.py). These fixture records use that same default so
    # the typed comparison keys actually match; a real deployment resolves
    # service/conditions from session state (PLAN.md section 4) rather
    # than needing this workaround.
    PolicyRecord(
        policy_id="prep-coverage",
        source_id="prep_current.txt",
        source_span="This test is covered by most insurance plans; your plan covers this when ordered by your physician.",
        site=SITE, service=SERVICE, attribute="coverage",
        value="covered", unit=None, polarity=Polarity.POSITIVE, conditions=(),
        effective_from=datetime(2026, 8, 1), effective_to=None,
    ),
    PolicyRecord(
        policy_id="intake-cost",
        source_id="intake_faq.txt",
        source_span="A consultation visit costs $150.",
        site=SITE, service=SERVICE, attribute="cost",
        value="150.00", unit="usd", polarity=Polarity.POSITIVE, conditions=(),
        effective_from=datetime(2026, 1, 1), effective_to=None,
    ),
    PolicyRecord(
        policy_id="intake-referral",
        source_id="intake_faq.txt",
        source_span="You do not need a referral for a routine bloodwork visit.",
        site=SITE, service=SERVICE, attribute="requires_referral",
        value="true", unit=None, polarity=Polarity.NEGATIVE, conditions=(),
        effective_from=datetime(2026, 1, 1), effective_to=None,
    ),
]
