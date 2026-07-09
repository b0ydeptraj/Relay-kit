"""
relay_kit_v3/search_router.py

V5.2.4 — Tiered Search Router
Dispatches search queries to Tier 0 (Lexical + Graph) or Tier 1/2 (Embeddings).
Tier 0 is the default. If --embedding-model is provided, routes to Tier 1/2.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from relay_kit_v3.context_index import BM25Corpus
from relay_kit_v3.context_graph import SkillGraph


class SearchRouter:
    """Routes search queries to the appropriate tier."""

    def __init__(self, project_root: Path, embedding_model: str | None = None) -> None:
        self.project_root = Path(project_root)
        self.embedding_model = embedding_model

    def _determine_tier(self) -> int:
        if self.embedding_model == "nomic-embed-text-v1.5":
            return 1
        elif self.embedding_model == "bge-m3":
            return 2
        elif self.embedding_model:
            raise ValueError(f"Unknown embedding model: {self.embedding_model}")
        return 0

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Perform search using the configured tier."""
        tier = self._determine_tier()

        if tier == 0:
            return self._tier_0_search(query, top_k)
        else:
            return self._tier_1_2_search(query, top_k)

    def _tier_0_search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        """Tier 0: BM25 + Skill Dependency Graph Ranking"""
        skills_dir = self.project_root / ".agent" / "skills"
        if not skills_dir.exists():
            # Fallback if no skills dir
            corpus = BM25Corpus.from_directory(self.project_root)
            return corpus.search(query, top_k=top_k)

        # 1. Build BM25 Corpus
        corpus = BM25Corpus.from_directory(skills_dir, extensions={".md"})
        
        # 2. Get initial lexical matches
        raw_results = corpus.search(query, top_k=50)
        
        # 3. Build Graph and apply boosts
        graph = SkillGraph.from_directory(skills_dir)
        boosted_results = graph.boost_scores(raw_results, top_k=top_k)
        
        return boosted_results

    def _tier_1_2_search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        """Tier 1/2: Semantic Search using sentence-transformers"""
        from relay_kit_v3.semantic_index import SemanticIndex
        
        skills_dir = self.project_root / ".agent" / "skills"
        if not skills_dir.exists():
            search_dir = self.project_root
        else:
            search_dir = skills_dir

        index = SemanticIndex(self.embedding_model)
        
        # Collect documents
        docs = []
        paths = []
        for p in search_dir.rglob("*.md"):
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")[:80_000]
                docs.append(text)
                paths.append(str(p))
            except OSError:
                continue

        if not docs:
            return []

        # Encode and calculate similarities
        query_vec = index.encode_query(query)
        doc_vecs = index.encode(docs)
        
        results = []
        for path, doc_vec in zip(paths, doc_vecs):
            score = SemanticIndex.cosine_similarity(query_vec, doc_vec)
            if score > 0.3:  # minimum similarity threshold
                results.append({
                    "doc_id": path,
                    "score": round(score, 4),
                    "matched_terms": ["semantic_match"],
                })

        results.sort(key=lambda x: -x["score"])
        return results[:top_k]
