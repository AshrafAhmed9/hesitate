"""
The verification gate's per-sentence entry point.

PLAN.md section 4: "Release the original sentence only if every atomic
claim is supported." This module extracts typed claims (extract.py),
resolves each against the candidate PolicyRecords Moss returned
(resolve.py), and produces a GateDecision (schema.py) whose
sentence_decision implements that release rule exactly.

Note on what "Moss returns candidates" means here: in the deployed agent,
Moss retrieval returns natural-language passages; those passages are
looked up against the curated PolicyRecord table by source_id to get the
structured records to resolve against (section 4: "canonical policies are
manually reviewed structured records"). This module takes the resolved
PolicyRecord list directly so it can be tested and benchmarked without a
live Moss connection -- the Moss-integration layer (W4/agent/livekit) is
a thin adapter in front of this function, not a reimplementation of it.
"""
from __future__ import annotations

import hashlib
import time
import uuid
from datetime import datetime
from typing import Optional

from .completeness import find_unclassified_spans
from .correct import DECLINE_TEXT, build_sentence_correction
from .extract import extract_claims
from .resolve import resolve_claim
from .schema import (
    AtomicVerdict,
    CandidateUnit,
    Claim,
    Decision,
    GateDecision,
    Polarity,
    PolicyRecord,
)


def verify_unit(
    candidate: CandidateUnit,
    candidate_records: list[PolicyRecord],
    at: Optional[datetime] = None,
) -> GateDecision:
    t0 = time.perf_counter()
    claims = extract_claims(candidate.text)
    unclassified = find_unclassified_spans(candidate.text, [c.raw_text for c in claims])
    t1 = time.perf_counter()

    verdicts: list[AtomicVerdict] = []
    for claim in claims:
        decision, evidence_ids, reason, record = resolve_claim(claim, candidate_records, at=at)
        verdicts.append(AtomicVerdict(claim, decision, evidence_ids, reason, resolved_record=record))
    t2 = time.perf_counter()

    decision = GateDecision(
        decision_id=str(uuid.uuid4()),
        candidate=candidate,
        original_text_hash=hashlib.sha256(candidate.text.encode()).hexdigest(),
        replacement_text=None,
        replacement_text_hash=None,
        policy_snapshot_id=candidate.policy_snapshot_id,
        atomic_verdicts=tuple(verdicts),
        unclassified_spans=unclassified,  # agent/gate/completeness.py -- narrow heuristic, see its docstring
        stage_timings_ms={
            "extraction_ms": (t1 - t0) * 1000,
            "resolution_ms": (t2 - t1) * 1000,
            "total_ms": (t2 - t0) * 1000,
        },
        disposition="pending",
    )

    sd = decision.sentence_decision
    if sd == Decision.SUPPORTED:
        decision.disposition = "released"
        decision.replacement_text = candidate.text
    elif sd == Decision.CONTRADICTED:
        decision.disposition = "corrected"
        decision.replacement_text = build_sentence_correction(decision.atomic_verdicts)
    else:
        decision.disposition = "declined"  # CONFLICT or UNVERIFIABLE
        decision.replacement_text = DECLINE_TEXT

    decision.replacement_text_hash = hashlib.sha256(decision.replacement_text.encode()).hexdigest()
    return decision


def verify_sentence(text: str, candidate_records: list[PolicyRecord], session_id: str = "test", turn_id: str = "t0") -> GateDecision:
    """Convenience wrapper for benchmark/test use — wraps a bare sentence
    in a minimal CandidateUnit."""
    unit = CandidateUnit(
        session_id=session_id,
        turn_id=turn_id,
        unit_seq=0,
        text=text,
        char_start=0,
        char_end=len(text),
        caller_context={},
        policy_snapshot_id="test-snapshot",
    )
    return verify_unit(unit, candidate_records)
