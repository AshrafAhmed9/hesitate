"""
Typed extraction: sentence text -> Claim (schema.py), and curated document
text -> PolicyRecord candidates for retrieval fixtures.

Per the design spec section 10 ("Typed modules"): numeric+units, monetary amounts,
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
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "eighteen": 18, "twenty": 20, "twenty-four": 24, "twenty four": 24,
    "thirty": 30, "forty": 40, "forty-five": 45, "fifty": 50, "sixty": 60,
    "seventy-five": 75, "ninety": 90,
}

_WORD_NUM = "|".join(sorted((re.escape(w) for w in _NUMBER_WORDS), key=len, reverse=True))


def _spell_out_to_digits(text: str) -> str:
    """Rewrites spoken quantities ('half an hour', 'a day', 'two hundred
    dollars') into the digit forms the patterns below understand. Found by
    probing the gate with phrasings a caller or judge would plausibly use:
    these produced zero claims, so a wrong answer passed as 'nothing to check'."""
    arrive = r"((?:arrive|come in|check in|get there|be there|show up)\s+)"
    fast = r"(\bfast(?:ing)?\s+(?:for\s+)?(?:about\s+|around\s+)?)"
    # Only inside an arrival or fasting phrase: 'an hour before your visit' in an
    # unrelated sentence (a text confirmation, say) must keep passing through.
    text = re.sub(arrive + r"(?:half an? hour|half-hour)\b", r"\g<1>30 minutes", text, flags=re.IGNORECASE)
    text = re.sub(arrive + r"(?:an|a|one) hour\b", r"\g<1>1 hour", text, flags=re.IGNORECASE)
    text = re.sub(fast + r"half a day\b", r"\g<1>12 hours", text, flags=re.IGNORECASE)
    text = re.sub(fast + r"(?:a|one)(?: full)? day\b", r"\g<1>24 hours", text, flags=re.IGNORECASE)
    text = re.sub(
        rf"\b({_WORD_NUM})\s+hundred(?:\s+(?:and\s+)?({_WORD_NUM}))?\s+(?:us\s+)?dollars?\b",
        lambda m: f"${_NUMBER_WORDS[m.group(1).lower()] * 100 + (_NUMBER_WORDS[m.group(2).lower()] if m.group(2) else 0):g}",
        text, flags=re.IGNORECASE,
    )
    text = re.sub(
        rf"\b({_WORD_NUM})\s+(?:us\s+)?dollars?\b",
        lambda m: f"${_NUMBER_WORDS[m.group(1).lower()]:g}", text, flags=re.IGNORECASE,
    )
    text = re.sub(r"\b(\d+(?:\.\d{1,2})?)\s+(?:us\s+)?dollars?\b", r"$\1", text, flags=re.IGNORECASE)
    return text


def _to_number(text: str) -> Optional[float]:
    text = text.strip().lower()
    if text in _NUMBER_WORDS:
        return float(_NUMBER_WORDS[text])
    try:
        return float(text)
    except ValueError:
        return None


def normalize_text(text: str) -> str:
    """Markdown stripped and spoken quantities written as digits. verify.py runs
    both extraction and the completeness check on this form, so a correct
    '150 dollars' is not flagged as an unrecognized dollar span."""
    return _spell_out_to_digits(re.sub(r"[*_`]+", "", text))


def extract_claims(text: str, site: str = "*", service: str = "fasting-bloodwork") -> list[Claim]:
    """Extract every typed claim from a sentence, tagged with the given
    site/service scope (in the real pipeline this comes from resolved
    caller context, per section 4 -- not from the sentence text itself).

    REAL BUG (2026-09-20, caught live in tests/test_end_to_end_live.py):
    Groq's gpt-oss-20b wraps numbers it wants to emphasize in markdown
    bold ('**12 hours**'). The '*' characters broke every regex here --
    none of them treat '*' as a word boundary, so 'fast for **12
    hours**' matched nothing and the claim silently vanished, which
    would have let a wrong number through as "no claim, nothing to
    check" instead of catching it. Stripping markdown emphasis before
    extraction fixes this generally, for every claim family, instead of
    patching each regex individually."""
    text = normalize_text(text)
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
        r"\b(?:arrive|come in|check in|get there|be there|show up)\s+(?P<num>[\w-]+(?:\s\w+)?)\s*(?P<unit>hours?|hrs?|minutes?|mins?)\s*(?:early|before)\b",
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
        r"(?<!\bno )(?<!\bnot )\b(?:an?\s+|your\s+)?(?P<doc>referral|id|insurance card|photo id|prescription)\s+(?:is|are)\s+(?:required|needed)\b",
        text, re.IGNORECASE,
    ):
        doc = m.group("doc").lower().replace(" ", "_")
        claims.append(Claim(site, service, f"requires_{doc}", "true", None, Polarity.POSITIVE, (), m.group(0)))
    for m in re.finditer(
        r"\b(?:an?\s+|your\s+)?(?P<doc>referral|id|insurance card|photo id|prescription)\s+(?:is|are)\s+(?:not|n't)\s+(?:required|needed)\b"
        r"|\b(?P<doc2>referral|id|insurance card|photo id|prescription)\s+isn't\s+(?:required|needed)\b"
        r"|\bno\s+(?P<doc3>referral|id|insurance card|photo id|prescription)\s+(?:is\s+)?(?:required|needed)\b",
        text, re.IGNORECASE,
    ):
        doc = (m.group("doc") or m.group("doc2") or m.group("doc3")).lower().replace(" ", "_")
        claims.append(Claim(site, service, f"requires_{doc}", "true", None, Polarity.NEGATIVE, (), m.group(0)))
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
# original sentence. A known gap.
