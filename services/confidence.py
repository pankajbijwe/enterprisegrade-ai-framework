# confidence.py - Confidence scoring and calibration helpers 
# services/confidence.py
import math
from typing import List, Optional

def compute_confidence(logprobs: Optional[dict], retrieval_scores: List[float], calibration_model=None) -> float:
    """
    Combine model-derived confidence (from logprobs) and retrieval similarity.
    - logprobs: provider logprobs object; compute avg token probability
    - retrieval_scores: list of similarity scores (0..1)
    - calibration_model: placeholder for production calibration (Platt scaling, isotonic)
    Returns a float in [0,1]
    """
    model_conf = _logprobs_to_confidence(logprobs)
    retrieval_conf = max(retrieval_scores) if retrieval_scores else 0.0
    # Weighted combination: give more weight to retrieval for RAG tasks
    combined = 0.4 * model_conf + 0.6 * retrieval_conf
    # Simple smoothing
    return max(0.0, min(1.0, combined))

def _logprobs_to_confidence(logprobs_obj):
    if not logprobs_obj:
        return 0.5  # unknown -> neutral
    try:
        toks = logprobs_obj.get("token_logprobs") or []
        if not toks:
            return 0.5
        # convert average logprob to probability
        avg_logp = sum(toks) / len(toks)
        prob = math.exp(avg_logp)
        # clamp
        return max(0.0, min(1.0, prob))
    except Exception:
        return 0.5