"""
Runs the Tier 2 semantic-route benchmark and publishes its own confusion
matrix and latency, separate from the typed-route benchmark (PLAN.md
section 10). Usage: source .venv/bin/activate && python -m bench.run_semantic_benchmark
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.gate.semantic import verify_semantic_claim_against_passages, _get_model
from bench.semantic_cases import CASES


def main() -> int:
    _get_model()  # warm the model before timing
    correct = 0
    timings = []
    for claim_text, passages, expected in CASES:
        t0 = time.perf_counter()
        decision, evidence_id = verify_semantic_claim_against_passages(claim_text, passages)
        timings.append((time.perf_counter() - t0) * 1000)
        actual = decision.value
        ok = actual == expected
        correct += ok
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] expected={expected:13s} actual={actual:13s} evidence={evidence_id} | {claim_text}")

    n = len(CASES)
    timings.sort()
    print()
    print(f"Score: {correct}/{n}")
    print(f"Semantic route latency (warm, single passage): p50={timings[n//2]:.2f}ms p95={timings[min(n-1, int(n*0.95))]:.2f}ms")
    print("STATUS: starter calibration set (4 cases). Not the independently-labeled")
    print("calibration split PLAN.md section 10 requires before thresholds are 'tuned'.")
    return 0 if correct == n else 1


if __name__ == "__main__":
    raise SystemExit(main())
