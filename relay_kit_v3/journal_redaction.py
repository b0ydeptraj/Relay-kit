import re
import copy
from typing import Any, Mapping

class RedactionGate:
    """
    V5.3.6 Journal Redaction Gate.
    Redact secrets, tokens, emails, absolute sensitive paths truoc khi ghi vao journal.
    """
    
    # Regex patterns for sensitive data
    PATTERNS = [
        (re.compile(r"Bearer\s+[\w\-._~+/]+=*"), "Bearer [REDACTED]"),
        (re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"), "[REDACTED_EMAIL]"),
        (re.compile(r"(?<![A-Z0-9])AKIA[A-Z0-9]{16}(?![A-Z0-9])"), "[REDACTED_AWS_KEY]"),
        (re.compile(r"api_key=[\w\d]+"), "api_key=[REDACTED_API_KEY]"),
        (re.compile(r"-----BEGIN.*PRIVATE KEY-----.*?-----END.*PRIVATE KEY-----", re.DOTALL), "[REDACTED_PRIVATE_KEY]")
    ]
    
    @staticmethod
    def redact_text(text: str) -> str:
        """Apply all redaction patterns to a single string."""
        if not isinstance(text, str):
            return text
            
        redacted = text
        for pattern, replacement in RedactionGate.PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return redacted

    @staticmethod
    def redact_entry(entry: Mapping[str, Any]) -> dict[str, Any]:
        """
        Recursively redact all string values in an entry dictionary.
        Returns a new redacted dictionary.
        """
        return RedactionGate._redact_recursive(entry)

    @staticmethod
    def _redact_recursive(data: Any) -> Any:
        if isinstance(data, dict):
            return {k: RedactionGate._redact_recursive(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [RedactionGate._redact_recursive(v) for v in data]
        elif isinstance(data, str):
            return RedactionGate.redact_text(data)
        else:
            return data
