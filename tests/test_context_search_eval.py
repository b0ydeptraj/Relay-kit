"""
tests/test_context_search_eval.py

V5.2.5 — Context Search Eval Suite runner.
Tests Tier 0 search accuracy against predefined evaluation cases.
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

from relay_kit_v3.search_router import SearchRouter


def load_eval_cases() -> list[dict]:
    eval_file = Path(__file__).parent / "context_search_eval.json"
    if not eval_file.exists():
        raise FileNotFoundError(f"Missing {eval_file}")
    with open(eval_file, "r", encoding="utf-8") as f:
        return json.load(f)


def test_tier0_eval_suite():
    cases = load_eval_cases()
    project_root = Path(__file__).parent.parent
    router = SearchRouter(project_root)
    
    total_cases = len(cases)
    hits = 0

    print(f"Running {total_cases} eval cases for Tier 0...")
    
    for case in cases:
        query = case["query"]
        expected_top = case["expected_top_3"]
        
        results = router.search(query, top_k=5)
        returned_skills = []
        for r in results:
            # extract skill name from doc_id, e.g., .../.agent/skills/api-integration/SKILL.md
            doc_id = r["doc_id"]
            if "SKILL.md" in doc_id:
                parts = Path(doc_id).parts
                skill_name = parts[-2]
                returned_skills.append(skill_name)
        
        # We count a hit if ANY of the expected top 3 are in the returned top 5
        case_hit = False
        for expected in expected_top:
            if expected in returned_skills:
                case_hit = True
                break
                
        if case_hit:
            hits += 1
            print(f"  [PASS] {query[:30]:<30} -> Found {expected_top[0]} etc.")
        else:
            print(f"  [FAIL] {query[:30]:<30} -> Expected {expected_top}, Got {returned_skills}")

    accuracy = (hits / total_cases) * 100
    print(f"\nTier 0 Accuracy: {accuracy:.2f}% ({hits}/{total_cases})")
    
    # Requirement: Benchmark Tier 0 vs Tier 1
    # Tier 0 (Lexical) might only achieve 40-50% on Vietnamese queries.
    assert accuracy >= 40.0, f"Tier 0 Accuracy {accuracy:.2f}% is too low (expected >= 40%)"
    print("RESULT: Eval Suite PASSED (Tier 0 benchmark)")


def _run_all():
    tests = [
        test_tier0_eval_suite,
    ]

    failed = 0
    for test in tests:
        name = getattr(test, "__name__", repr(test))
        try:
            test()
        except Exception as e:
            print(f"FAIL: {name} — {e}")
            traceback.print_exc()
            failed += 1

    if failed:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    _run_all()
