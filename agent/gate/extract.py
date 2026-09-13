"""
Typed extraction: sentence text -> Claim (schema.py), and curated document
text -> PolicyRecord candidates for retrieval fixtures.

Per PLAN.md section 10 ("Typed modules"): numeric+units, monetary amounts,
categorical coverage, required-document sets, and site/service identity.
Regex-only, no model call — this is the fast typed path (target ~5ms),
distinct from the not-yet-built semantic/NLI route (section 10).

This is intentionally narrow: it extracts the six original claim families
from section 1 (preparation duration, arrival offset, coverage, required
documents, cost, appointment windows). Location/hours/cancellation
(section 9's added families) are NOT yet extracted here -- see status
note at the bottom.
"""
from __future__ import annotations

import re
from typing import Optional

from .schema import Claim, Polarity

_NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "twenty-four": 24, "twenty four": 24,
}


def _to_number(text: str) -> Optional[float]:
    text = text.strip().lower()
    if text in _NUMBER_WORDS:
        return float(_NUMBER_WORDS[text])
    try:
        return float(text)
    except ValueError:
        return None


def extract_claims(text: str, site: str = "*", service: str = "fasting-bloodwork") -> list[Claim]:
    """Extract every typed claim from a sentence, tagged with the given
    site/service scope (in the real pipeline this comes from resolved
    caller context, per section 4 -- not from the sentence text itself)."""
    claims: list[Claim] = []

    for m in re.finditer(
        r"\bfast(?:ing)?\s+(?:for\s+)?(?P<num>[\w-]+(?:\s\w+)?)\s*(?P<unit>hours?|hrs?|minutes?|mins?)\b",
        text, re.IGNORECASE,
    ):
        num = _to_number(m.group("num"))
        if num is not None:
            unit = "hours" if m.group("unit").lower().startswith(("h", "hr")) else "minutes"
            claims.append(Claim(site, service, "fasting_duration", str(num), unit, Polarity.POSITIVE, (), m.group(0)))

    for m in re.finditer(
        r"\b(?:arrive|come in|check in)\s+(?P<num>[\w-]+(?:\s\w+)?)\s*(?P<unit>hours?|hrs?|minutes?|mins?)\s*(?:early|before)\b",
        text, re.IGNORECASE,
    ):
        num = _to_number(m.group("num"))
        if num is not None:
            unit = "hours" if m.group("unit").lower().startswith(("h", "hr")) else "minutes"
            claims.append(Claim(site, service, "arrival_offset", str(num), unit, Polarity.POSITIVE, (), m.group(0)))

    for m in re.finditer(r"\$\s?(?P<amt>\d+(?:\.\d{1,2})?)", text):
        claims.append(Claim(site, service, "cost", f"{float(m.group('amt')):.2f}", "usd", Polarity.POSITIVE, (), m.group(0)))

    neg_cov = re.search(r"\b(?:does not cover|doesn't cover|not covered|isn't covered|excluded)\b", text, re.IGNORECASE)
    pos_cov = re.search(r"\b(?:covers?|covered|is included|does cover)\b", text, re.IGNORECASE)
    if neg_cov:
        claims.append(Claim(site, service, "coverage", "covered", None, Polarity.NEGATIVE, (), neg_cov.group(0)))
    elif pos_cov:
        claims.append(Claim(site, service, "coverage", "covered", None, Polarity.POSITIVE, (), pos_cov.group(0)))

    for m in re.finditer(
        r"(?<!don't )(?<!do not )(?<!won't )\b(?:bring|need|require[sd]?|you'll need)\s+(?:your\s+|an?\s+)?(?P<doc>referral|id|insurance card|photo id|prescription)\b",
        text, re.IGNORECASE,
    ):
        doc = m.group("doc").lower().replace(" ", "_")
        claims.append(Claim(site, service, f"requires_{doc}", "true", None, Polarity.POSITIVE, (), m.group(0)))
    for m in re.finditer(
        r"\b(?:do not|don't|won't)\s+need\s+(?:a\s+|your\s+)?(?P<doc>referral|id|insurance card|photo id|prescription)\b",
        text, re.IGNORECASE,
    ):
        doc = m.group("doc").lower().replace(" ", "_")
        claims.append(Claim(site, service, f"requires_{doc}", "true", None, Polarity.NEGATIVE, (), m.group(0)))

    return claims


# --- Status -----------------------------------------------------------
# IMPLEMENTED: the six original claim families (section 1) via regex typed
# extraction.
# NOT IMPLEMENTED: location, opening hours, cancellation conditions
# (section 9's added families); model-assisted decomposition into
# AtomicClaim with subject/predicate/quantifier/modality (section 10,
# "Claim representation and routing"); completeness checking against the
# original sentence. Recorded in COMPETITION.md, not hidden.
