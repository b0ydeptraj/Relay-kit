import json
import logging
import uuid
import datetime
from pathlib import Path
from typing import Any, Mapping

from relay_kit_v3.evidence_quality import EvidenceGate, EvidenceGateError
from relay_kit_v3.journal_redaction import RedactionGate

logger = logging.getLogger(__name__)

class FieldJournal:
    """
    V5.3.1 Journal Capture.
    Ghi nhan entries vao `.relay-kit/memory/journal.jsonl`.
    Moi entry phai qua EvidenceGate va RedactionGate.
    """
    
    DEFAULT_JOURNAL_PATH = ".relay-kit/memory/journal.jsonl"
    
    def __init__(self, project_path: str | Path):
        self.project_path = Path(project_path)
        self.journal_file = self.project_path / self.DEFAULT_JOURNAL_PATH
        
    def _ensure_dir(self):
        self.journal_file.parent.mkdir(parents=True, exist_ok=True)
        
    def capture(self, entry: Mapping[str, Any], *, promotion_recommended: bool = False) -> dict[str, Any]:
        """
        Capture a memory entry into the field journal.
        Returns the captured (and redacted) entry.
        Raises EvidenceGateError if it lacks required evidence.
        """
        # 1. Enforce Evidence Gate
        EvidenceGate.enforce(entry)
        
        # 2. Base entry shape
        # V5.3.5 No Auto-Promote Guard: ALWAYS candidate, ALWAYS low confidence by default.
        captured_entry = {
            "id": entry.get("id", str(uuid.uuid4())),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "candidate",
            "confidence": "low",
            "promotion_recommended": promotion_recommended,
            "evidence_ref": entry.get("evidence_ref"),
            "content": entry.get("content", ""),
            "error_signature": entry.get("error_signature"),
            "metadata": entry.get("metadata", {})
        }
        
        # 3. Apply Redaction Gate
        redacted_entry = RedactionGate.redact_entry(captured_entry)
        
        # 4. Append to file
        self._ensure_dir()
        with open(self.journal_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(redacted_entry, ensure_ascii=False) + "\n")
            
        logger.info(f"Captured journal entry {redacted_entry['id']}")
        return redacted_entry

    def list_entries(self) -> list[dict[str, Any]]:
        """Read all entries from the journal."""
        if not self.journal_file.exists():
            return []
            
        entries = []
        with open(self.journal_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return entries
        
    def get_entry(self, entry_id: str) -> dict[str, Any] | None:
        """Find a specific entry by id."""
        for entry in self.list_entries():
            if entry.get("id") == entry_id:
                return entry
        return None

    def promote_entry(self, entry_id: str) -> bool:
        """
        Human-approved promotion (V5.3.5).
        Modifies status to 'promoted' and confidence to 'high'.
        Rewrites the jsonl file.
        Returns True if found and promoted, False otherwise.
        """
        entries = self.list_entries()
        promoted = False
        
        for entry in entries:
            if entry.get("id") == entry_id:
                entry["status"] = "promoted"
                entry["confidence"] = "high"
                promoted = True
                break
                
        if not promoted:
            return False
            
        # Rewrite the entire file (safe for relatively small journals, otherwise we'd append a state change event)
        self._ensure_dir()
        with open(self.journal_file, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                
        return True
