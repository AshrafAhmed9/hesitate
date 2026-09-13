"""
W0 Contracts — versioned policy fact and claim/decision schemas.
PLAN.md section 4 ("Canonical policies", "Claims and decisions").

This is the shared contract every other module (verification, ingestion,
evaluation) imports. Do not duplicate these fields elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class Polarity(str, Enum):
    POSITIVE = "positive"   # the attribute holds / is required / is included
    NEGATIVE = "negative"   # the attribute does not hold / is not required / excluded


class Decision(str, Enum):
    """PLAN.md section 4 evidence table. Four outcomes, not three — CONFLICT
    is distinct from UNVERIFIABLE: it means multiple applicable authorities
    disagree, not that evidence is missing."""
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    UNVERIFIABLE = "unverifiable"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class PolicyRecord:
    """A single curated, structured policy fact. Author these by hand (or
    generate then manually review) — this is not free-text auto-extraction.
    PLAN.md section 4: 'canonical policies' are manually reviewed structured
    records; Moss retrieves natural-language passages, but the comparison
    key is always this structured record, not the passage text."""
    policy_id: str
    source_id: str          # which document this was curated from
    source_span: str        # the exact sentence/phrase in that document
    site: str                # e.g. "downtown-clinic"; "*" = applies to all sites
    service: str             # e.g. "fasting-bloodwork"
    attribute: str           # e.g. "fasting_duration_hours"
    value: str                # normalized value, e.g. "8"
    unit: Optional[str]
    polarity: Polarity
    conditions: tuple[str, ...]  # e.g. ("ordered_by_physician",); () = unconditional
    effective_from: datetime
    effective_to: Optional[datetime]  # None = open-ended / still active
    supersedes: Optional[str] = None  # policy_id of the record this replaces, if any

    def is_active_at(self, at: datetime) -> bool:
        if at < self.effective_from:
            return False
        if self.effective_to is not None and at >= self.effective_to:
            return False
        return True

    def key(self) -> tuple:
        """The resolution key: everything except value/polarity/temporal/
        provenance fields. Two records with the same key are candidates for
        the same real-world fact and must be reconciled by supersession or
        flagged as CONFLICT — never picked by similarity."""
        return (self.site, self.service, self.attribute, self.conditions)


@dataclass(frozen=True)
class Claim:
    """A factual assertion extracted from either the outgoing agent sentence
    or a retrieved passage, normalized onto the same key space as
    PolicyRecord so the two can be compared directly."""
    site: str
    service: str
    attribute: str
    value: str
    unit: Optional[str]
    polarity: Polarity
    conditions: tuple[str, ...]
    raw_text: str  # original span, for display/debugging only — never compared

    def key(self) -> tuple:
        return (self.site, self.service, self.attribute, self.conditions)


# --- Section 10: audit-grade record types ------------------------------

@dataclass(frozen=True)
class AtomicClaim:
    """One decomposed proposition from a CandidateUnit. subject/predicate/
    object mirror PLAN.md section 10's decomposition fields; site/service/
    attribute/value/unit/polarity/conditions carry the typed comparison key
    so this can flow directly into resolve_claim()."""
    subject: str
    predicate: str
    object_value: str
    site: str
    service: str
    attribute: str
    value: str
    unit: Optional[str]
    polarity: Polarity
    quantifier: Optional[str]
    modality: str            # "will" | "may" | "usually" | "always" etc.
    conditions: tuple[str, ...]
    source_span: tuple[int, int]  # character offsets into the CandidateUnit text
    route: str                # "typed" | "semantic" | "approved_phrase" | "unclassified"

    def key(self) -> tuple:
        return (self.site, self.service, self.attribute, self.conditions)


@dataclass(frozen=True)
class CandidateUnit:
    """One sentence/unit awaiting the gate. session_id/turn_id/unit_seq
    identify it for cancellation and ordered release (Section 4, 'Stream
    lifecycle')."""
    session_id: str
    turn_id: str
    unit_seq: int
    text: str
    char_start: int
    char_end: int
    caller_context: dict            # resolved site/service/etc, with provenance
    policy_snapshot_id: str
    generation_metadata: dict = None  # model name/version, temperature, etc.


@dataclass(frozen=True)
class AtomicVerdict:
    # NOTE: typed "AtomicClaim" per section 10's naming, but the current
    # typed route (extract.py) produces the simpler `Claim` type, not a
    # full model-decomposed AtomicClaim. Left as Claim here to match what
    # is actually produced; unifying onto AtomicClaim is future work once
    # decomposition (section 10) is built.
    claim: Claim
    decision: Decision
    evidence_policy_ids: tuple[str, ...]
    reason: str
    resolved_record: Optional["PolicyRecord"] = None  # the winning applicable record, if any


@dataclass
class GateDecision:
    """Section 10 'Decisions and auditability'. One per CandidateUnit."""
    decision_id: str
    candidate: CandidateUnit
    original_text_hash: str
    replacement_text: Optional[str]
    replacement_text_hash: Optional[str]
    policy_snapshot_id: str
    atomic_verdicts: tuple[AtomicVerdict, ...]
    unclassified_spans: tuple[str, ...]  # decomposition coverage gaps — must be empty to release
    stage_timings_ms: dict
    disposition: str  # "released" | "corrected" | "declined"

    @property
    def sentence_decision(self) -> Decision:
        """Section 4: release only if every atomic claim is supported.
        Any contradiction or conflict wins; else any unverifiable claim
        blocks release; unclassified spans always block release."""
        if self.unclassified_spans:
            return Decision.UNVERIFIABLE
        if not self.atomic_verdicts:
            return Decision.SUPPORTED
        decisions = [v.decision for v in self.atomic_verdicts]
        if Decision.CONTRADICTED in decisions:
            return Decision.CONTRADICTED
        if Decision.CONFLICT in decisions:
            return Decision.CONFLICT
        if Decision.UNVERIFIABLE in decisions:
            return Decision.UNVERIFIABLE
        return Decision.SUPPORTED


@dataclass
class AudioEvent:
    """Section 10: distinguishes server-generated audio from client-
    confirmed playout. Neither alone proves what a human perceived."""
    decision_id: str
    state: str  # "submitted" | "queued" | "playing" | "interrupted" | "finished"
    server_timestamp: float
    client_confirmed: bool = False
