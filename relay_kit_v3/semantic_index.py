"""
relay_kit_v3/semantic_index.py

V5.2.3 — Embedding Adapter
Abstract interface to load embedding models, encode text, and calculate cosine similarity.
Supports nomic-embed-text-v1.5 and bge-m3.
Does NOT auto-download models. Requires relay-kit[embeddings].
"""
from __future__ import annotations

import math
from typing import Any, Protocol


class EmbeddingModel(Protocol):
    def encode(self, texts: list[str]) -> list[list[float]]:
        ...


class SemanticIndex:
    """Adapter for local semantic search models."""

    SUPPORTED_MODELS = {
        "nomic-embed-text-v1.5": "nomic-ai/nomic-embed-text-v1.5",
        "bge-m3": "BAAI/bge-m3",
    }

    def __init__(self, model_name: str) -> None:
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(f"Model {model_name} is not supported. Supported: {list(self.SUPPORTED_MODELS.keys())}")
        
        self.model_name = model_name
        self.hf_model_id = self.SUPPORTED_MODELS[model_name]
        self._model: Any = None

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise RuntimeError(
                "Semantic search requires the 'sentence-transformers' package. "
                "Please run `pip install relay-kit[embeddings]` to enable Tier 1/2 search."
            )

        # We set trust_remote_code=True for nomic models as they usually require it
        trust = "nomic" in self.hf_model_id.lower()
        self._model = SentenceTransformer(self.hf_model_id, trust_remote_code=trust)
        return self._model

    def encode(self, texts: list[str] | str) -> list[list[float]]:
        """Encode a list of texts into vector embeddings."""
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return []

        model = self._load_model()
        
        # nomic-embed-text requires a specific prefix for search documents
        if self.model_name == "nomic-embed-text-v1.5":
            texts = [f"search_document: {t}" for t in texts]

        # bge-m3 works well without prefixes, or handles them internally
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def encode_query(self, query: str) -> list[float]:
        """Encode a search query. Uses query-specific prefixes if needed."""
        model = self._load_model()
        
        if self.model_name == "nomic-embed-text-v1.5":
            query = f"search_query: {query}"
            
        embeddings = model.encode([query], normalize_embeddings=True)
        return embeddings[0].tolist()

    @staticmethod
    def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
            
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot / (norm_a * norm_b)
