"""
Thin wrapper around the real Moss SDK (moss.MossClient), normalizing its
async API and QueryResultDocumentInfo shape to what agent/retrieval/adapter.py
expects (a sync-callable .query(index_name, text, top_k) returning objects
with .doc_id/.text/.score) -- the same shape agent/retrieval/mock_moss.py
provides, so adapter.py needs zero changes to use either.

Requires MOSS_PROJECT_ID and MOSS_PROJECT_KEY in the environment (see
.env, gitignored, never committed). The real moss SDK is fully async;
this wrapper runs it synchronously via asyncio.run() for callers (like
adapter.py and the benchmark scripts) that are not themselves async yet.
The LiveKit integration (not yet built) should call the async methods
directly instead of through this sync wrapper, once it exists.
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass

from moss import DocumentInfo, MossClient, QueryOptions


@dataclass(frozen=True)
class QueryHit:
    doc_id: str
    text: str
    score: float


class LiveMossClient:
    """Same interface shape as MockMossClient (create_index/load_index/
    query), backed by the real Moss Cloud service."""

    def __init__(self, project_id: str | None = None, project_key: str | None = None):
        project_id = project_id or os.environ["MOSS_PROJECT_ID"]
        project_key = project_key or os.environ["MOSS_PROJECT_KEY"]
        self._client = MossClient(project_id, project_key)

    def create_index(self, name: str, docs: list[dict]) -> None:
        asyncio.run(self._client.create_index(
            name, [DocumentInfo(id=d["id"], text=d["text"]) for d in docs]
        ))

    def load_index(self, name: str) -> None:
        asyncio.run(self._client.load_index(name))

    def query(self, index_name: str, text: str, top_k: int = 5) -> list[QueryHit]:
        result = asyncio.run(self._client.query(index_name, text, QueryOptions(top_k=top_k)))
        return [QueryHit(doc_id=d.id, text=d.text, score=d.score) for d in result.docs]
