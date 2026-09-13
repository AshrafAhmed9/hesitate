"""
W3 typed resolution route — PLAN.md section 4 ("Canonical policies",
"Claims and decisions") and section 10 ("Typed modules").

Given a Claim (extracted from the outgoing sentence) and the full set of
PolicyRecords Moss retrieved as candidates, resolve the applicable set for
that claim's key, apply supersession, detect unresolved conflicts, and
return a Decision. This is the typed route only — the semantic/NLI route
(section 10, "Semantic verification") is not implemented; see status note
at the bottom of this file.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from .schema import Decision, PolicyRecord, Claim, Polarity


def _active_and_matching(records: list[PolicyRecord], claim_key: tuple, at: datetime) -> list[PolicyRecord]:
    """Every record whose key matches the claim and which is active at `at`.
    'Top-k must not hide a conflict' (section 4): this looks at every
    candidate Moss returned, not just the top match."""
    return [r for r in records if r.key() == claim_key and r.is_active_at(at)]


def _drop_superseded(records: list[PolicyRecord]) -> list[PolicyRecord]:
    """Explicit supersession only — never 'latest upload' or highest
    similarity (section 4)."""
    superseded_ids = {r.supersedes for r in records if r.supersedes}
    return [r for r in records if r.policy_id not in superseded_ids]


def resolve_claim(
    claim: Claim,
    candidate_records: list[PolicyRecord],
    at: Optional[datetime] = None,
) -> tuple[Decision, tuple[str, ...], str, Optional[PolicyRecord]]:
    """Returns (decision, evidence_policy_ids, reason).

    Decision table (section 4, exact):
      same applicable key, conditions, polarity, normalized value -> SUPPORTED
      same applicable key, incompatible value/polarity            -> CONTRADICTED
      missing scope/evidence, unsupported wording, incomplete parse -> UNVERIFIABLE
      unresolved applicable authorities disagree                  -> CONFLICT
    """
    at = at or datetime.now()

    applicable = _active_and_matching(candidate_records, claim.key(), at)
    applicable = _drop_superseded(applicable)

    if not applicable:
        return (
            Decision.UNVERIFIABLE,
            (),
            "no active policy record matches this site/service/attribute/conditions",
            None,
        )

    # Do every applicable record agree on value+polarity? If not, and none
    # supersedes the others, this is an unresolved conflict -- not a pick
    # by similarity, not an automatic approval.
    distinct = {(r.value, r.unit, r.polarity) for r in applicable}
    if len(distinct) > 1:
        return (
            Decision.CONFLICT,
            tuple(r.policy_id for r in applicable),
            f"{len(applicable)} equally applicable records disagree and no supersession resolves it",
            None,
        )

    record = applicable[0]
    if record.polarity == claim.polarity and _values_equal(claim, record):
        return (Decision.SUPPORTED, (record.policy_id,), "matches active applicable record", record)

    return (
        Decision.CONTRADICTED,
        (record.policy_id,),
        f"active record says {record.polarity.value} {record.value}{record.unit or ''}, "
        f"claim says {claim.polarity.value} {claim.value}{claim.unit or ''}",
        record,
    )


_MINUTES_PER_HOUR = 60
_DURATION_UNITS = {"hours", "minutes"}


def _values_equal(claim: Claim, record: PolicyRecord) -> bool:
    if claim.unit in _DURATION_UNITS and record.unit in _DURATION_UNITS:
        cv = float(claim.value) / (_MINUTES_PER_HOUR if claim.unit == "minutes" else 1)
        rv = float(record.value) / (_MINUTES_PER_HOUR if record.unit == "minutes" else 1)
        return abs(cv - rv) < 1e-6
    if claim.unit == "usd" and record.unit == "usd":
        return abs(float(claim.value) - float(record.value)) < 1e-2
    return claim.value == record.value


# --- Status ---------------------------------------------------------------
# IMPLEMENTED: typed route above (numeric duration, cost, categorical
# coverage/document/polarity claims), with explicit supersession and
# conflict detection per section 4.
#
# NOT IMPLEMENTED (PLAN.md section 10, "Semantic verification"): the local
# entailment/NLI route for eligible nonnumeric claims, its calibration
# split, and abstention thresholds. Per section 4's decision table, claims
# that reach this stub because no typed parser covers them currently
# return UNVERIFIABLE via the caller's routing logic (agent/gate/verify.py),
# which is a safe default but is NOT the completed semantic route the plan
# specifies. This gap is recorded in COMPETITION.md's claims ledger, not
# hidden here.
