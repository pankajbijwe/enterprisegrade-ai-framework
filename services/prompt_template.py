# prompt_template.py - Prompt templating utilities 
# services/prompt_template.py
from typing import List, Dict

def build_prompt(system_instructions: str, user_text: str, context_chunks: List[Dict]) -> Dict:
    """
    Returns a dict with 'template_id' and 'text' to keep template metadata for audits.
    """
    template_id = "contract_miner_v1"
    context_text = "\n\n---\n\n".join([f"[{c['id']}]\n{c['text']}" for c in context_chunks])
    prompt_text = (
        f"SYSTEM: {system_instructions}\n\n"
        f"CONTEXT:\n{context_text}\n\n"
        f"USER QUESTION: {user_text}\n\n"
        "INSTRUCTIONS: Answer concisely, cite chunk ids in square brackets for provenance. "
        "If the answer is not supported by the context, say 'Insufficient context' and list follow-ups."
    )
    return {"template_id": template_id, "text": prompt_text}