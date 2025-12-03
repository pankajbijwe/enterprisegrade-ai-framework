# explainability.py - Explainability helpers (perturbation, provenance) 
# services/explainability.py
from typing import List, Dict, Any
import copy
import math

def explain_response_perturbation(llm_client, prompt: Dict[str, Any], response: str, retrieved_chunks: List[Dict], top_n: int = 5) -> Dict:
    """
    Lightweight perturbation-based token importance:
    - Mask tokens in the response and re-run LLM to see change in logprob or semantic similarity.
    - For efficiency, we mask groups of tokens (words) and measure delta in confidence or similarity.
    - Also return provenance: which chunks were cited.
    """
    tokens = response.split()
    n = len(tokens)
    if n == 0:
        return {"token_importance": [], "provenance": [c["id"] for c in retrieved_chunks]}

    # For demo: mask each token and measure whether LLM answer changes (cheap proxy)
    base = llm_client.generate(prompt, return_logprobs=True)
    base_text = base["text"]
    base_score = _avg_logprob(base.get("logprobs"))

    importances = []
    for i in range(min(n, top_n)):
        masked_tokens = tokens.copy()
        masked_tokens[i] = "[MASK]"
        masked_resp_text = " ".join(masked_tokens)
        # Build a new prompt that asks model to score similarity (cheap approach)
        pert_prompt = {"template_id": prompt["template_id"], "text": prompt["text"] + f"\n\nEVALUATE: Is the following paraphrase equivalent? \"{masked_resp_text}\""}
        pert = llm_client.generate(pert_prompt, return_logprobs=True)
        pert_score = _avg_logprob(pert.get("logprobs"))
        delta = base_score - pert_score if base_score is not None and pert_score is not None else 0.0
        importances.append({"token": tokens[i], "delta": delta})

    # Sort by delta descending
    importances = sorted(importances, key=lambda x: -x["delta"])
    provenance = [c["id"] for c in retrieved_chunks]
    return {"token_importance": importances, "provenance": provenance}

def _avg_logprob(logprobs_obj):
    if not logprobs_obj:
        return None
    # logprobs_obj structure depends on provider; attempt to compute average of top token logprobs
    try:
        toks = logprobs_obj.get("token_logprobs") or []
        if not toks:
            return None
        return sum(toks) / len(toks)
    except Exception:
        return None