"""
A local mock of the Moss client interface documented at
docs.moss.dev/docs/reference/python/api.md (create_index / load_index /
query), backed by a local sentence-transformers embedding model instead of
the real Moss Cloud service.

WHY THIS EXISTS: `agent/gate/resolve.py` deliberately takes a
`list[PolicyRecord]` directly so it's testable without any live
connection. But PLAN.md's mandatory deliverable is a *deployed* agent
using Moss for retrieval (section 23), and that adapter code — "take a
caller's spoken question, retrieve candidate policy passages, map them
back to curated PolicyRecords by source_id" — did not exist and could not
be tested. This mock lets that adapter be written and tested NOW; the only
change needed to use the real Moss SDK instead is swapping this class for
one that calls `moss.Client`, once an account/API key exists (an account
decision, not an engineering one).

THIS IS NOT MOSS. It does not have Moss's sub-10ms in-process runtime,
its hybrid search, or its infrastructure. It exists solely to let the
retrieval->resolution adapter be built and tested honestly, and every
place it's used says so.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class QueryResult:
    doc_id: str
    text: str
    score: float


class MockMossClient:
    """Mimics the shape of Moss's documented Python client closely enough
    that agent/retrieval/adapter.py doesn't need to change when a real
    account exists — only this class gets swapped out."""

    def __init__(self):
        self._indexes: dict[str, list[dict]] = {}

    def create_index(self, name: str, docs: list[dict]) -> None:
        """docs: [{'id': str, 'text': str}, ...] — matches the documented
        Moss SDK shape exactly."""
        self._indexes[name] = docs

    def load_index(self, name: str) -> None:
        if name not in self._indexes:
            raise KeyError(f"index {name!r} was not created — call create_index first")

    def query(self, index_name: str, text: str, top_k: int = 5) -> list[QueryResult]:
        docs = self._indexes.get(index_name)
        if docs is None:
            raise KeyError(f"index {index_name!r} not loaded")
        model = _embedder()
        query_vec = model.encode(text)
        scored = []
        for d in docs:
            doc_vec = _embed_cached(model, d["id"], d["text"])
            score = _cosine(query_vec, doc_vec)
            scored.append(QueryResult(d["id"], d["text"], float(score)))
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]


@lru_cache(maxsize=1)
def _embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


_doc_vec_cache: dict[str, object] = {}


def _embed_cached(model, doc_id: str, text: str):
    if doc_id not in _doc_vec_cache:
        _doc_vec_cache[doc_id] = model.encode(text)
    return _doc_vec_cache[doc_id]


def _cosine(a, b) -> float:
    import numpy as np
    a, b = np.asarray(a), np.asarray(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else 0.0
