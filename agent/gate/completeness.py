"""
W3 completeness check — PLAN.md section 10: "Record unclassified spans
explicitly. Full character coverage alone is insufficient: check whether
all propositions and qualifications were represented." Section 4: "Only
an audited allowlist of fixed conversational phrases is exempt.
Residual unsupported factual wording makes the entire sentence unverified."

This is a lightweight heuristic, NOT the model-assisted decomposition
section 10 actually specifies (that needs an LLM call). It closes one
concrete, real gap found live (2026-09-13): a sentence like "fast for
8-12 hours" or "you'll get a text confirmation" contains a factual claim
that no typed pattern in extract.py recognizes, and previously silently
defaulted to SUPPORTED (schema.py: "no claims to check") -- exactly the
failure mode PLAN.md section 5 calls out ("unknown claims silently
classified nonfactual count as failures").

Scope: flags number+unit patterns (durations, money, percentages) that
extract.py's typed patterns did not consume. Does NOT catch every
possible unclassified factual claim (e.g. "you'll get a text message" has
no number in it at all -- that specific case is NOT caught by this
heuristic either, and remains a documented gap). This is a narrower,
honest improvement, not a claim of full completeness checking.
"""
from __future__ import annotations

import re

# Patterns for "suspicious" factual content: a number followed by a unit
# word. If a match's span isn't inside any already-extracted claim's
# raw_text, it's unclassified.
_NUMBER_UNIT_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:-|to|–|—)?\s*\d*\.?\d*\s*(?:hours?|hrs?|minutes?|mins?|days?|%|percent|dollars?)\b",
    re.IGNORECASE,
)


def find_unclassified_spans(text: str, consumed_raw_texts: list[str]) -> tuple[str, ...]:
    """Returns spans of `text` that look like factual number+unit claims
    but were not covered by any already-extracted Claim's raw_text."""
    unclassified = []
    for m in _NUMBER_UNIT_PATTERN.finditer(text):
        span_text = m.group(0)
        if any(span_text in consumed or consumed in span_text for consumed in consumed_raw_texts):
            continue
        # also skip if the match is a strict substring of an already-
        # consumed span (e.g. "8 hours" inside "fast for 8 hours")
        if any(_overlaps(m.span(), text, consumed) for consumed in consumed_raw_texts):
            continue
        unclassified.append(span_text)
    return tuple(unclassified)


def _overlaps(span: tuple[int, int], text: str, consumed_raw_text: str) -> bool:
    idx = text.find(consumed_raw_text)
    if idx == -1:
        return False
    consumed_span = (idx, idx + len(consumed_raw_text))
    return not (span[1] <= consumed_span[0] or span[0] >= consumed_span[1])
