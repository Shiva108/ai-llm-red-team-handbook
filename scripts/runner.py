# file: runner.py

import json
import os
from datetime import datetime
from typing import List

from client import LLMClient
from config import DEFAULT_LLM_CONFIG, DEFAULT_TEST_CONFIG
from models import TestResult
from tests import get_all_tests


def serialize_results(results: List[TestResult]) -> List[dict]:
    return [r.__dict__ for r in results]


def main() -> None:
    os.makedirs(DEFAULT_TEST_CONFIG.output_dir, exist_ok=True)

    client = LLMClient(DEFAULT_LLM_CONFIG)
    tests = get_all_tests()

    all_results: List[TestResult] = []

    for test in tests:
        print(f"[+] Running test suite: {test.__class__.__name__} ({test.category})")
        try:
            results = test.run(client)
            all_results.extend(results)
            print(f"    -> {len(results)} cases executed.")
        except Exception as exc:
            print(f"    [!] Error running {test.__class__.__name__}: {exc}")

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = os.path.join(DEFAULT_TEST_CONFIG.output_dir, f"llm_redteam_results_{ts}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(serialize_results(all_results), f, ensure_ascii=False, indent=2)

    print(f"\n[✓] Done. Results written to: {out_path}")
    print(f"[i] Total test cases executed: {len(all_results)}")


if __name__ == "__main__":
    main()
