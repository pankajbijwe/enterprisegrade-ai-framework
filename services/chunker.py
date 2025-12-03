# chunker.py - Text chunking utilities 
# services/chunker.py
from typing import List, Dict
import re

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """
    Simple sliding window chunker returning list of dicts: {'id':..., 'text':...}
    """
    text = re.sub(r'\s+', ' ', text).strip()
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk_text = text[start:end]
        chunks.append({"id": f"chunk-{idx}", "text": chunk_text})
        idx += 1
        start = end - overlap
        if start < 0:
            start = 0
    return chunks