"""
tests/test_context_graph.py

Unit tests for relay_kit_v3/context/graph_ranker.py (V5.2.1)
Acceptance criteria:
  - Graph builds edges correctly from "Likely next step" sections
  - Neighbours of a matched skill receive a score boost
  - Skills NOT in the graph still appear (no data lost)
  - 2-hop propagation works (neighbour's neighbour also boosted, but less)
  - from_directory() correctly parses real SKILL.md files
"""
from __future__ import annotations

import sys
import textwrap
import traceback
import tempfile
from pathlib import Path

from relay_kit_v3.context_graph import (
    SkillGraph,
    _parse_skill_name,
    _parse_next_steps,
)


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def _make_skill_md(name: str, next_steps: list[str]) -> str:
    steps = "\n".join(f"- {s}" for s in next_steps)
    return textwrap.dedent(f"""\
        ---
        name: {name}
        description: Use when testing graph ranker.
        ---

        # Mission
        Test skill for graph ranker unit tests.

        ## Likely next step
        {steps}
    """)


def _graph_with_chain() -> tuple[SkillGraph, dict[str, str]]:
    """
    Build a small graph:
        debug-hub -> root-cause-debugging -> fix-hub
    Returns (graph, doc_id_map)
    """
    g = SkillGraph()
    ids = {
        "debug-hub":            "/skills/debug-hub/SKILL.md",
        "root-cause-debugging": "/skills/root-cause-debugging/SKILL.md",
        "fix-hub":              "/skills/fix-hub/SKILL.md",
    }
    g.add_skill("debug-hub",            ids["debug-hub"],            ["root-cause-debugging"])
    g.add_skill("root-cause-debugging", ids["root-cause-debugging"], ["fix-hub"])
    g.add_skill("fix-hub",              ids["fix-hub"],              [])
    return g, ids


# ─────────────────────────────────────────────────────────────────────
# Parsing tests
# ─────────────────────────────────────────────────────────────────────

def test_parse_skill_name():
    content = _make_skill_md("api-integration", ["architect"])
    name = _parse_skill_name(content, fallback="fallback")
    assert name == "api-integration", f"Got {name}"
    print("  PASS: _parse_skill_name extracts name from frontmatter")


def test_parse_next_steps_single():
    content = _make_skill_md("api-integration", ["architect"])
    steps = _parse_next_steps(content)
    assert steps == ["architect"], f"Got {steps}"
    print("  PASS: _parse_next_steps parses single step")


def test_parse_next_steps_multiple():
    content = _make_skill_md("debug-hub", ["root-cause-debugging", "fix-hub", "qa-governor"])
    steps = _parse_next_steps(content)
    assert "root-cause-debugging" in steps
    assert "fix-hub" in steps
    assert "qa-governor" in steps
    print(f"  PASS: _parse_next_steps parses multiple steps: {steps}")


def test_parse_next_steps_empty():
    content = "---\nname: lone-skill\n---\n# No next step section"
    steps = _parse_next_steps(content)
    assert steps == []
    print("  PASS: _parse_next_steps returns [] when section missing")


# ─────────────────────────────────────────────────────────────────────
# Graph structure tests
# ─────────────────────────────────────────────────────────────────────

def test_graph_neighbours():
    g, ids = _graph_with_chain()
    assert g.neighbours("debug-hub") == {"root-cause-debugging"}
    assert g.neighbours("root-cause-debugging") == {"fix-hub"}
    assert g.neighbours("fix-hub") == set()
    print("  PASS: graph.neighbours() returns correct sets")


def test_graph_doc_id_lookup():
    g, ids = _graph_with_chain()
    assert g.doc_id_for("debug-hub") == ids["debug-hub"]
    assert g.name_for_doc_id(ids["fix-hub"]) == "fix-hub"
    print("  PASS: doc_id / name bidirectional lookup works")


def test_graph_stats():
    g, _ = _graph_with_chain()
    s = g.stats()
    assert s["nodes"] == 3
    assert s["edges"] == 2   # debug-hub->root-cause, root-cause->fix-hub
    print(f"  PASS: graph stats correct: {s}")


# ─────────────────────────────────────────────────────────────────────
# Score boosting tests
# ─────────────────────────────────────────────────────────────────────

def test_direct_neighbour_boosted():
    """root-cause-debugging should receive a score boost when debug-hub matches."""
    g, ids = _graph_with_chain()

    bm25_results = [
        {"doc_id": ids["debug-hub"], "score": 10.0, "matched_terms": ["debug"]},
    ]
    boosted = g.boost_scores(bm25_results, top_k=10)

    doc_ids = [r["doc_id"] for r in boosted]
    assert ids["root-cause-debugging"] in doc_ids, (
        "root-cause-debugging should appear after boost"
    )
    # Find the boosted entry
    rcd = next(r for r in boosted if r["doc_id"] == ids["root-cause-debugging"])
    assert rcd["score"] > 0, "Boosted score must be positive"
    print(f"  PASS: direct neighbour boosted to score={rcd['score']:.4f}")


def test_two_hop_neighbour_boosted():
    """fix-hub (2 hops from debug-hub) should also receive some boost."""
    g, ids = _graph_with_chain()

    bm25_results = [
        {"doc_id": ids["debug-hub"], "score": 10.0, "matched_terms": ["debug"]},
    ]
    boosted = g.boost_scores(bm25_results, top_k=10)

    doc_ids = [r["doc_id"] for r in boosted]
    assert ids["fix-hub"] in doc_ids, "fix-hub should appear via 2-hop propagation"
    fix = next(r for r in boosted if r["doc_id"] == ids["fix-hub"])
    rcd = next(r for r in boosted if r["doc_id"] == ids["root-cause-debugging"])
    # 2-hop boost must be LESS than 1-hop boost
    assert fix["score"] < rcd["score"], (
        f"2-hop boost ({fix['score']}) should be less than 1-hop ({rcd['score']})"
    )
    print(f"  PASS: 2-hop neighbour boosted: fix-hub={fix['score']:.4f} < rcd={rcd['score']:.4f}")


def test_unrelated_node_not_boosted():
    """A skill not connected to the matched node should NOT appear."""
    g = SkillGraph()
    g.add_skill("debug-hub",  "/skills/debug-hub/SKILL.md",  ["root-cause-debugging"])
    g.add_skill("root-cause-debugging", "/skills/rcd/SKILL.md", [])
    g.add_skill("cooking",    "/skills/cooking/SKILL.md",    [])  # isolated

    bm25_results = [
        {"doc_id": "/skills/debug-hub/SKILL.md", "score": 10.0, "matched_terms": ["debug"]},
    ]
    boosted = g.boost_scores(bm25_results, top_k=10)
    doc_ids = [r["doc_id"] for r in boosted]
    assert "/skills/cooking/SKILL.md" not in doc_ids, "Isolated skill should not appear"
    print("  PASS: isolated skill not surfaced by graph boost")


def test_original_scores_preserved():
    """Original BM25 scores must be preserved (only boosted, never reduced)."""
    g, ids = _graph_with_chain()
    bm25_results = [
        {"doc_id": ids["debug-hub"], "score": 7.5, "matched_terms": ["debug"]},
    ]
    boosted = g.boost_scores(bm25_results, top_k=10)
    top = next(r for r in boosted if r["doc_id"] == ids["debug-hub"])
    assert top["score"] >= 7.5, f"Original score must not decrease: got {top['score']}"
    print(f"  PASS: original score preserved/boosted: {top['score']:.4f} >= 7.5")


# ─────────────────────────────────────────────────────────────────────
# Integration: from_directory()
# ─────────────────────────────────────────────────────────────────────

def test_from_directory_builds_graph(tmp_path: Path):
    # Create fake skill directories
    for name, next_steps in [
        ("api-integration", ["architect"]),
        ("architect",       ["developer"]),
        ("developer",       []),
    ]:
        skill_dir = tmp_path / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            _make_skill_md(name, next_steps), encoding="utf-8"
        )

    g = SkillGraph.from_directory(tmp_path)
    stats = g.stats()
    assert stats["nodes"] == 3, f"Expected 3 nodes, got {stats['nodes']}"
    assert stats["edges"] == 2, f"Expected 2 edges, got {stats['edges']}"
    assert "architect" in g.neighbours("api-integration")
    print(f"  PASS: from_directory built graph: {stats}")


# ─────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────

def _run_all():
    import tempfile
    tmp = Path(tempfile.mkdtemp())

    tests = [
        test_parse_skill_name,
        test_parse_next_steps_single,
        test_parse_next_steps_multiple,
        test_parse_next_steps_empty,
        test_graph_neighbours,
        test_graph_doc_id_lookup,
        test_graph_stats,
        test_direct_neighbour_boosted,
        test_two_hop_neighbour_boosted,
        test_unrelated_node_not_boosted,
        test_original_scores_preserved,
        lambda: test_from_directory_builds_graph(tmp),
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
        print("RESULT: ALL GRAPH RANKER TESTS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    _run_all()
