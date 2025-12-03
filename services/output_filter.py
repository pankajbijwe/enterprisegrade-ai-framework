# output_filter.py - PII redaction and policy filters 
# services/output_filter.py
import re
from typing import Tuple, Dict

PII_PATTERNS = {
    "email": r'\b[\w\.-]+@[\w\.-]+\.\w+\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "phone": r'\b(?:\+?\d{1,3})?[-.\s]?(?:\d{2,4}[-.\s]?){2,4}\d{2,4}\b'
}

def filter_output_and_redact(text: str) -> Tuple[str, Dict]:
    redactions = []
    filtered = text
    for label, pat in PII_PATTERNS.items():
        matches = re.findall(pat, filtered)
        if matches:
            redactions.append({"type": label, "matches": matches})
            filtered = re.sub(pat, f"[REDACTED_{label.upper()}]", filtered)
    # Policy checks (example)
    if "confidential" in filtered.lower() and len(filtered) > 1000:
        # Example policy: long confidential dumps are blocked
        filtered = "[REDACTED_FOR_POLICY]"
        redactions.append({"type":"policy_block", "reason":"long confidential content"})
    return filtered, {"redactions": redactions}