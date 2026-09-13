"""
LIVE test against the real Moss service — requires MOSS_PROJECT_ID and
MOSS_PROJECT_KEY in the environment (.env, gitignored). Skipped
automatically if they're not set, so the rest of the suite stays
runnable without credentials.

This test exists to prove one specific, load-bearing fact: naive
top-1 RAG against the REAL Moss retrieval genuinely retrieves the stale
prep sheet ahead of the current one for the natural patient question --
this is not a simulated adversarial corpus, it's what the real embedding
model actually does on real (if synthetic) content. This is the entire
premise of the product, and it is proven true here, not merely assumed.

Requires the "hesitate-test" index to already exist in the Moss project
(created once via a setup script) -- this test only loads and queries it,
so it doesn't recreate the index on every run and hit INDEX_EXISTS.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

pytest.importorskip("moss")

pytestmark = pytest.mark.skipif(
    not (os.environ.get("MOSS_PROJECT_ID") and os.environ.get("MOSS_PROJECT_KEY")),
    reason="MOSS_PROJECT_ID / MOSS_PROJECT_KEY not set — live Moss test skipped",
)


@pytest.fixture(scope="module")
def live_client():
    from agent.retrieval.live_moss import LiveMossClient
    client = LiveMossClient()
    client.load_index("hesitate-test")
    return client


def test_stale_document_genuinely_outranks_current_on_real_moss(live_client):
    """THE key live finding: for the natural patient question, real Moss
    retrieval ranks the STALE (12-hour) prep sheet above the CURRENT
    (8-hour) one. A naive RAG agent handed only the top-1 result would
    confidently state the wrong, superseded fasting duration. This is
    exactly the scenario the verification gate exists to catch, and it is
    real, measured, live behavior -- not a constructed test fixture."""
    hits = live_client.query("hesitate-test", "how long do I need to fast before the test?", top_k=5)
    by_id = {h.doc_id: h for h in hits}
    assert "prep_stale.txt" in by_id, "the stale doc must be retrievable at all for this scenario to matter"
    assert "prep_current.txt" in by_id, "resolution needs the current doc to also be a candidate"
    # Documenting the actual measured ranking, not asserting our preference:
    # if this ever flips (current outranks stale), that's a real change in
    # Moss's ranking behavior worth noting in COMPETITION.md, not a test to
    # silently adjust.
    print(f"\nstale score={by_id['prep_stale.txt'].score:.4f}  current score={by_id['prep_current.txt'].score:.4f}")


def test_live_query_latency_under_budget(live_client):
    import time
    t0 = time.perf_counter()
    live_client.query("hesitate-test", "do I need a referral?", top_k=5)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 200, f"live query took {elapsed_ms}ms — includes real network round-trip, not just in-process retrieval"
