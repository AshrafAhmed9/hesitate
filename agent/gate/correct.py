"""
W3 — deterministic corrections and the decline template.

PLAN.md section 4: "Correct contradictions using audited deterministic
templates populated solely from validated records. No unchecked
LLM-generated correction... If a complete replacement cannot be
established, decline." Section 10 adds a bounded one-shot semantic
correction path -- NOT implemented here (no NLI route exists yet; see
resolve.py status note).
"""
from __future__ import annotations

from .schema import AtomicVerdict, Decision, Polarity

DECLINE_TEXT = "I can't confirm that from this clinic's policy. Please check with the front desk."

_TEMPLATES = {
    "fasting_duration": "Actually — {value} {unit}, per your prep instructions.",
    "arrival_offset": "Actually — please arrive {value} {unit} early.",
    "cost": "Actually — that's ${value}.",
    "coverage": "Actually — {polarity_phrase} covered.",
    "requires_referral": "Actually — {polarity_phrase} need a referral.",
}


def build_correction(verdict: AtomicVerdict) -> str | None:
    """Returns a reviewed-template correction string for one CONTRADICTED
    atomic verdict, populated solely from the resolved PolicyRecord's own
    values (never from the model's original wrong text) — per PLAN.md
    section 4. Returns None if no template exists for this attribute or no
    record was resolved, in which case the caller must decline."""
    if verdict.decision != Decision.CONTRADICTED or verdict.resolved_record is None:
        return None
    template = _TEMPLATES.get(verdict.claim.attribute)
    if template is None:
        return None
    record = verdict.resolved_record
    polarity_phrase = "is" if record.polarity == Polarity.POSITIVE else "is not"
    return template.format(value=record.value, unit=record.unit or "", polarity_phrase=polarity_phrase).replace("  ", " ").strip()


def build_sentence_correction(verdicts: tuple[AtomicVerdict, ...]) -> str:
    """Per-sentence correction/decline text. Section 4: if every
    contradicted claim has a template-backed replacement, use it;
    otherwise decline the whole sentence -- never release a partial
    correction silently missing a claim."""
    contradicted = [v for v in verdicts if v.decision == Decision.CONTRADICTED]
    conflicted_or_unverifiable = [
        v for v in verdicts if v.decision in (Decision.CONFLICT, Decision.UNVERIFIABLE)
    ]
    if conflicted_or_unverifiable:
        return DECLINE_TEXT
    if not contradicted:
        return DECLINE_TEXT  # should not be called when nothing needs correcting
    corrections = [build_correction(v) for v in contradicted]
    if any(c is None for c in corrections):
        return DECLINE_TEXT
    return " ".join(corrections)
