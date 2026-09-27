"""
The adapter between a Moss-shaped retrieval client and the gate.

the design spec section 4: "Moss retrieves candidates from natural-language
questions/claims; resolve each candidate's key against the complete
applicable set." This module is that step: given retrieved passages
(doc_id, text, score), map each back to its curated PolicyRecord(s) by
source_id, then hand the FULL set of records sharing that source_id's key
to resolve_claim — not just the top-1 hit, per section 4's "top-k must not
hide a conflict."

Works against any client implementing .query(index_name, text, top_k) ->
list of objects with .doc_id/.text/.score — the real Moss SDK or
agent/retrieval/mock_moss.py.
"""
from __future__ import annotations

from agent.gate.schema import PolicyRecord


def build_index_docs(records: list[PolicyRecord]) -> list[dict]:
    """One retrievable doc per unique source_id (a source document may back
    multiple PolicyRecords; retrieval happens at the document level, the
    same way Moss indexes natural-language passages)."""
    by_source: dict[str, str] = {}
    for r in records:
        by_source.setdefault(r.source_id, r.source_span)
    return [{"id": sid, "text": text} for sid, text in by_source.items()]


def build_record_docs(records: list[PolicyRecord]) -> list[dict]:
    """One retrievable doc per policy sentence, id '<source_id>#<attribute>'.
    build_index_docs keeps only the first sentence of each source file, which
    left arrival/coverage/referral facts unsearchable in the live call."""
    return [{"id": f"{r.source_id}#{r.attribute}", "text": r.source_span} for r in records]


def retrieve_candidate_records(
    client,
    index_name: str,
    query_text: str,
    all_records: list[PolicyRecord],
    top_k: int = 5,
) -> list[PolicyRecord]:
    """Query the client, then expand each hit's source_id back to every
    PolicyRecord curated from that source (there may be more than one
    attribute per document). This is the actual candidate set resolve.py
    receives -- retrieval picks *documents*, resolution picks *facts*."""
    hits = client.query(index_name, query_text, top_k=top_k)
    hit_source_ids = {h.doc_id.split("#")[0] for h in hits}
    return [r for r in all_records if r.source_id in hit_source_ids]
