"""
Runs the pre-declared contract-suite cases (bench/cases.py) and publishes
denominators per PLAN.md section 5: "Publish counts and denominators ...
full verdict confusion matrix." Every number in the README/PRD/video must
trace back to a script here, re-runnable from a clean checkout.

Usage: python -m bench.run_benchmark
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.gate.verify import verify_sentence
from bench.cases import CASES, _NOW


def main() -> int:
    correct = 0
    confusion: dict[tuple[str, str], int] = {}
    timings = []

    for sentence, records, expected_decision, expected_disposition in CASES:
        result = verify_sentence(sentence, records)
        actual_decision = result.sentence_decision
        actual_disposition = result.disposition
        ok = actual_decision == expected_decision and actual_disposition == expected_disposition
        confusion[(expected_decision.value, actual_decision.value)] = (
            confusion.get((expected_decision.value, actual_decision.value), 0) + 1
        )
        timings.append(result.stage_timings_ms["total_ms"])
        mark = "PASS" if ok else "FAIL"
        if ok:
            correct += 1
        print(f"[{mark}] expected={expected_decision.value:13s} actual={actual_decision.value:13s} "
              f"disposition={actual_disposition:9s} | {sentence}")
        if not ok:
            for v in result.atomic_verdicts:
                print(f"       claim={v.claim.attribute} decision={v.decision.value} reason={v.reason}")

    n = len(CASES)
    timings.sort()
    p50 = timings[n // 2]
    p95 = timings[min(n - 1, int(n * 0.95))]

    print()
    print(f"Score: {correct}/{n} ({100 * correct / n:.1f}%)")
    print(f"Gate latency (extraction+resolution only, no Moss network round-trip): "
          f"p50={p50:.4f}ms p95={p95:.4f}ms  (n={n} -- NOT the section-5 target of 1,000 warm evaluations)")
    print()
    print("Confusion matrix (expected, actual) -> count:")
    for k, v in sorted(confusion.items()):
        print(f"  {k}: {v}")

    print()
    print("STATUS: starter suite only (13 cases). PLAN.md section 5 specifies a")
    print("200-case suite (100 dev / 100 holdout, independently human-reviewed,")
    print("locked holdout hash) as the actual evaluation target. Not yet built.")

    return 0 if correct == n else 1


if __name__ == "__main__":
    raise SystemExit(main())
