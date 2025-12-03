# sanitizer.py - Input sanitization and prompt-injection detection 
# services/sanitizer.py
import re

def sanitize_input(text: str) -> str:
    # Basic sanitization: strip control chars, long URLs, and excessive whitespace
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)
    text = re.sub(r'https?://\S+', '[REDACTED_URL]', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def detect_prompt_injection(text: str) -> bool:
    # Heuristic checks for common injection patterns
    patterns = [
        r'ignore (previous|all) instructions',
        r'do not follow system',
        r'follow these new instructions',
        r'execute the following'
    ]
    for p in patterns:
        if re.search(p, text, flags=re.I):
            return True
    return False