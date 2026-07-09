import re
from pathlib import Path
from typing import Any, Sequence

from relay_kit_v3.field_journal import FieldJournal

class PatternRetriever:
    """
    V5.3.3 Pattern Retriever.
    Scan journal for entries with similar `error_signature`.
    Only inject entries with `confidence >= medium` (e.g. medium, high).
    """
    
    def __init__(self, project_path: str | Path):
        self.journal = FieldJournal(project_path)
        
    def _tokenize(self, text: str) -> set[str]:
        if not text:
            return set()
        # Basic tokenization
        tokens = re.findall(r"\w+", text.lower())
        stopwords = {"in", "at", "the", "a", "an", "on", "for", "with", "and"}
        return set(t for t in tokens if t not in stopwords)
        
    def retrieve_similar_patterns(self, error_signature: str, top_k: int = 3) -> list[dict[str, Any]]:
        """
        Retrieve journal entries with similar error signatures.
        Filters out low confidence entries.
        """
        entries = self.journal.list_entries()
        
        # Filter confidence >= medium
        # Valid statuses: "medium", "high"
        trusted_entries = [
            e for e in entries 
            if e.get("confidence") in {"medium", "high"}
        ]
        
        if not trusted_entries or not error_signature:
            return []
            
        query_tokens = self._tokenize(error_signature)
        if not query_tokens:
            return []
            
        scored_entries = []
        for entry in trusted_entries:
            sig = entry.get("error_signature", "")
            sig_tokens = self._tokenize(sig)
            if not sig_tokens:
                continue
                
            intersection = query_tokens.intersection(sig_tokens)
            union = query_tokens.union(sig_tokens)
            score = len(intersection) / len(union) if union else 0
            
            if score > 0.1: # Minimum threshold
                scored_entries.append((score, entry))
                
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        
        return [entry for score, entry in scored_entries[:top_k]]
