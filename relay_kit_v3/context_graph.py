"""
relay_kit_v3/context/graph_ranker.py

V5.2.1 — Skill Dependency Graph Builder
Parses SKILL.md files to extract "Likely next step" links, builds a directed
dependency graph, then provides graph-aware score boosting on top of BM25
raw scores.

Algorithm:
  1. Parse all SKILL.md files under a skill directory (e.g. .agent/skills/).
  2. Build edges: skill_A --[next]--> skill_B for every "Likely next step" entry.
  3. When ranking search results, propagate boost to neighbour nodes:
       neighbour_boost = parent_score * EDGE_WEIGHT
     so skills adjacent to a high-scoring result also surface.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any


# ── Graph parameters ─────────────────────────────────────────────────
_EDGE_WEIGHT       = 0.35   # fraction of a parent's BM25 score passed to neighbours
_MAX_PROPAGATION   = 2      # hop depth — 1 = direct neighbours, 2 = neighbours of neighbours
_BOOST_DECAY       = 0.5    # each extra hop multiplied by this factor

# Regex patterns for SKILL.md parsing
_FRONTMATTER_NAME  = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
_NEXT_STEP_SECTION = re.compile(
    r"##\s+Likely next step[s]?\s*\n((?:[ \t]*[-*]\s*.+\n?)*)",
    re.IGNORECASE,
)
_LIST_ITEM         = re.compile(r"^[ \t]*[-*]\s*(.+)$", re.MULTILINE)


# ─────────────────────────────────────────────────────────────────────
# Parsing helpers
# ─────────────────────────────────────────────────────────────────────

def _parse_skill_name(content: str, fallback: str) -> str:
    """Extract 'name' from YAML frontmatter block."""
    m = _FRONTMATTER_NAME.search(content)
    return m.group(1).strip() if m else fallback


def _parse_next_steps(content: str) -> list[str]:
    """Return list of skill names listed under '## Likely next step'."""
    m = _NEXT_STEP_SECTION.search(content)
    if not m:
        return []
    block = m.group(1)
    items = _LIST_ITEM.findall(block)
    # strip inline markdown or trailing punctuation
    return [re.sub(r"[`*\[\]()]", "", item).strip().rstrip(".") for item in items if item.strip()]


# ─────────────────────────────────────────────────────────────────────
# Skill Graph
# ─────────────────────────────────────────────────────────────────────

class SkillGraph:
    """
    Directed graph of skill dependencies.

    Nodes  : skill names (str)
    Edges  : skill_A -> skill_B  (A recommends B as likely next step)

    Usage:
        graph = SkillGraph.from_directory(Path(".agent/skills"))
        boosted = graph.boost_scores(bm25_results)
    """

    def __init__(self) -> None:
        # adjacency: name -> set of neighbour names
        self._edges: dict[str, set[str]] = defaultdict(set)
        # reverse map: path_fragment -> canonical name
        self._path_to_name: dict[str, str] = {}
        # canonical name -> doc_id (file path string)
        self._name_to_docid: dict[str, str] = {}

    # ── construction ────────────────────────────────────────────────

    def add_skill(self, name: str, doc_id: str, next_steps: list[str]) -> None:
        self._name_to_docid[name] = doc_id
        # also register path fragments so we can look up by file path
        self._path_to_name[doc_id] = name
        for step in next_steps:
            self._edges[name].add(step)

    @classmethod
    def from_directory(cls, skills_root: Path) -> "SkillGraph":
        """
        Recursively scan skills_root for SKILL.md files and build the graph.

        Accepts any directory structure:
            <skills_root>/<skill-name>/SKILL.md
        """
        graph = cls()
        for skill_md in skills_root.rglob("SKILL.md"):
            try:
                content = skill_md.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            # derive skill name: try frontmatter, fall back to parent directory name
            parent_name = skill_md.parent.name
            name = _parse_skill_name(content, fallback=parent_name)
            next_steps = _parse_next_steps(content)
            graph.add_skill(name, str(skill_md), next_steps)

        return graph

    # ── graph queries ────────────────────────────────────────────────

    def neighbours(self, name: str) -> set[str]:
        """Direct next-step neighbours of a skill."""
        return self._edges.get(name, set())

    def doc_id_for(self, name: str) -> str | None:
        return self._name_to_docid.get(name)

    def name_for_doc_id(self, doc_id: str) -> str | None:
        return self._path_to_name.get(doc_id)

    # ── score boosting ───────────────────────────────────────────────

    def boost_scores(
        self,
        bm25_results: list[dict[str, Any]],
        top_k: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Apply graph-aware score boosting to BM25 results.

        For each result, propagate EDGE_WEIGHT * score to its direct neighbours
        (up to _MAX_PROPAGATION hops, with _BOOST_DECAY per hop).

        Args:
            bm25_results: output from BM25Corpus.search() —
                          [{"doc_id": ..., "score": ..., "matched_terms": ...}, ...]
            top_k: number of results to return after boosting.

        Returns:
            Merged and re-sorted result list with boosted scores.
        """
        # Build a score map from initial BM25 results
        score_map: dict[str, float] = {}
        meta_map:  dict[str, dict[str, Any]] = {}

        for item in bm25_results:
            doc_id = item["doc_id"]
            score_map[doc_id] = item["score"]
            meta_map[doc_id] = item

        # Propagate boosts hop by hop
        for hop in range(_MAX_PROPAGATION):
            decay = _BOOST_DECAY ** hop
            new_boosts: dict[str, float] = {}

            for doc_id, score in list(score_map.items()):
                name = self.name_for_doc_id(doc_id)
                if not name:
                    continue
                for neighbour_name in self.neighbours(name):
                    neighbour_doc = self.doc_id_for(neighbour_name)
                    if not neighbour_doc:
                        continue
                    boost = score * _EDGE_WEIGHT * decay
                    new_boosts[neighbour_doc] = new_boosts.get(neighbour_doc, 0.0) + boost

            for doc_id, boost in new_boosts.items():
                if doc_id in score_map:
                    score_map[doc_id] += boost
                else:
                    # new node surfaced by graph traversal
                    score_map[doc_id] = boost
                    meta_map[doc_id] = {
                        "doc_id": doc_id,
                        "score": 0.0,
                        "matched_terms": [],
                        "graph_boosted": True,
                    }

        # Rebuild result list
        results: list[dict[str, Any]] = []
        for doc_id, final_score in score_map.items():
            item = dict(meta_map[doc_id])
            item["score"] = round(final_score, 4)
            results.append(item)

        results.sort(key=lambda r: -r["score"])
        return results[:top_k]

    # ── stats ─────────────────────────────────────────────────────────

    def stats(self) -> dict[str, int]:
        """Return basic graph statistics."""
        total_edges = sum(len(v) for v in self._edges.values())
        return {
            "nodes": len(self._name_to_docid),
            "edges": total_edges,
        }
