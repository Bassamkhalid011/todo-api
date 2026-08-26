"""
Eval runner — tests all cases in evals/cases.json against the live /triage endpoint.

Usage:
    python evals/run_eval.py
"""
import json
import sys
from pathlib import Path

import requests

BASE_URL = "http://localhost:8001"
CASES_FILE = Path(__file__).parent / "cases.json"


def run():
    cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    passed = 0
    failed = 0
    errors = 0

    print(f"Running {len(cases)} eval cases against {BASE_URL}/triage\n")
    print(f"{'ID':<4} {'STATUS':<8} {'EXP_CAT':<10} {'GOT_CAT':<10} {'EXP_PRI':<10} {'GOT_PRI':<10} SUMMARY")
    print("-" * 80)

    for case in cases:
        try:
            resp = requests.post(
                f"{BASE_URL}/triage",
                json={"text": case["text"], "source": case["source"]},
                timeout=40,
            )
            if resp.status_code != 200:
                errors += 1
                print(f"{case['id']:<4} {'ERROR':<8} HTTP {resp.status_code}: {resp.text[:60]}")
                continue

            result = resp.json()
            cat_ok = result["category"] == case["expected_category"]
            pri_ok = result["priority"] == case["expected_priority"]
            ok = cat_ok and pri_ok

            status = "PASS" if ok else "FAIL"
            if ok:
                passed += 1
            else:
                failed += 1

            print(
                f"{case['id']:<4} {status:<8} "
                f"{case['expected_category']:<10} {result['category']:<10} "
                f"{case['expected_priority']:<10} {result['priority']:<10} "
                f"{result['summary'][:40]}"
            )

        except Exception as e:
            errors += 1
            print(f"{case['id']:<4} {'ERROR':<8} {str(e)[:60]}")

    total = len(cases)
    print("-" * 80)
    print(f"\nResults: {passed}/{total} passed, {failed} failed, {errors} errors")
    accuracy = passed / total * 100 if total > 0 else 0
    print(f"Accuracy: {accuracy:.1f}%")

    sys.exit(0 if failed == 0 and errors == 0 else 1)


if __name__ == "__main__":
    run()
