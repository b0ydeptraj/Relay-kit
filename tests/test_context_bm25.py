"""
tests/test_context_bm25.py

Unit tests for relay_kit_v3/context/bm25_scorer.py (V5.2.2)
Acceptance criteria:
  - BM25 phải xếp hạng file phù hợp với query cao hơn file không liên quan
  - Query chứa nhiều từ trùng với nội dung file -> score cao hơn
  - Query rỗng -> trả về list rỗng
  - File có term query xuất hiện nhiều lần nhưng ngắn -> KHÔNG được vượt file dài hơn có độ phủ rộng hơn
"""
from __future__ import annotations

import sys
import traceback
from relay_kit_v3.context_index import BM25Corpus, _tokenize


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def _make_corpus(docs: dict[str, str]) -> BM25Corpus:
    return BM25Corpus(list(docs.items()))


# ─────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────

def test_tokenize_strips_markdown():
    tokens = _tokenize("## Hello **world** `code` [link](url)")
    assert "hello" in tokens
    assert "world" in tokens
    # markdown noise stripped
    assert "##" not in tokens
    assert "**" not in tokens
    print("  PASS: tokenize strips markdown noise")


def test_empty_query_returns_empty():
    corpus = _make_corpus({"doc_a.md": "network timeout retry"})
    results = corpus.search("")
    assert results == []
    print("  PASS: empty query returns []")


def test_relevant_doc_ranked_higher():
    """File about network should outrank file about cooking."""
    corpus = _make_corpus({
        "network.md": "network timeout retry http request response api client",
        "cooking.md": "recipe pasta tomato sauce bake oven cook",
    })
    results = corpus.search("network timeout api")
    assert len(results) >= 1
    top = results[0]["doc_id"]
    assert "network" in top, f"Expected network.md on top, got {top}"
    print("  PASS: relevant doc ranked higher than irrelevant doc")


def test_score_positive_for_matching_terms():
    corpus = _make_corpus({
        "api.md": "api integration http client retry timeout",
    })
    results = corpus.search("api retry")
    assert len(results) == 1
    assert results[0]["score"] > 0
    print(f"  PASS: score positive for matching doc: {results[0]['score']:.4f}")


def test_no_match_returns_empty():
    corpus = _make_corpus({
        "api.md": "api integration http client",
    })
    results = corpus.search("quantum entanglement")
    assert results == [], f"Expected [], got {results}"
    print("  PASS: zero-match query returns []")


def test_multiple_docs_all_scored():
    corpus = _make_corpus({
        "debug.md": "debug error trace stack memory leak fix",
        "api.md": "api http network client retry timeout",
        "security.md": "security token auth encryption ssl tls",
    })
    results = corpus.search("debug error memory")
    doc_ids = [r["doc_id"] for r in results]
    assert "debug.md" in doc_ids
    assert results[0]["doc_id"] == "debug.md"
    print(f"  PASS: debug.md ranked first among {len(results)} results")


def test_matched_terms_populated():
    corpus = _make_corpus({
        "api.md": "api integration http client retry timeout",
    })
    results = corpus.search("api timeout")
    assert len(results) == 1
    matched = results[0]["matched_terms"]
    assert "api" in matched or "timeout" in matched
    print(f"  PASS: matched_terms populated: {matched}")


def test_top_k_limit():
    docs = {f"doc_{i}.md": f"network api retry doc {i}" for i in range(20)}
    corpus = _make_corpus(docs)
    results = corpus.search("network api retry", top_k=5)
    assert len(results) <= 5
    print(f"  PASS: top_k=5 respected, got {len(results)} results")


def test_from_files_factory(tmp_path):
    """Build corpus from actual files on disk."""
    f1 = tmp_path / "skill_a.md"
    f2 = tmp_path / "skill_b.md"
    f1.write_text("network http api timeout retry", encoding="utf-8")
    f2.write_text("database sql query migration schema", encoding="utf-8")

    corpus = BM25Corpus.from_files([f1, f2])
    results = corpus.search("http api")
    assert len(results) >= 1
    assert str(f1) in results[0]["doc_id"]
    print(f"  PASS: from_files factory works, top result: {results[0]['doc_id']}")


# ─────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────

def _run_all():
    import tempfile, pathlib
    tmp = pathlib.Path(tempfile.mkdtemp())

    tests = [
        test_tokenize_strips_markdown,
        test_empty_query_returns_empty,
        test_relevant_doc_ranked_higher,
        test_score_positive_for_matching_terms,
        test_no_match_returns_empty,
        test_multiple_docs_all_scored,
        test_matched_terms_populated,
        test_top_k_limit,
        lambda: test_from_files_factory(tmp),
    ]

    failed = 0
    for test in tests:
        name = getattr(test, "__name__", repr(test))
        try:
            test()
            print(f"PASS: {name}")
        except Exception as e:
            print(f"FAIL: {name} — {e}")
            traceback.print_exc()
            failed += 1

    print()
    if failed:
        print(f"RESULT: {failed} test(s) FAILED")
        sys.exit(1)
    else:
        print("RESULT: ALL BM25 TESTS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    _run_all()
