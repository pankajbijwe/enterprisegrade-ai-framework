# services/llm_client.py (excerpt)
import os, time, logging
import openai
from typing import List

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")

class OpenAIClient:
    def __init__(self, max_retries: int = 3, backoff: float = 1.0):
        self.model = MODEL
        self.embed_model = EMBED_MODEL
        self.max_retries = max_retries
        self.backoff = backoff

    def embed_text(self, text: str) -> List[float]:
        # batch small texts if needed; simple single-call with retry
        for attempt in range(self.max_retries):
            try:
                resp = openai.Embedding.create(model=self.embed_model, input=text)
                return resp["data"][0]["embedding"]
            except Exception as e:
                time.sleep(self.backoff * (2 ** attempt))
        raise RuntimeError("Embedding call failed after retries")

    def generate(self, prompt: Dict[str, str], return_logprobs: bool = False) -> Dict:
        for attempt in range(self.max_retries):
            try:
                completion = openai.Completion.create(
                    model=self.model,
                    prompt=prompt["text"],
                    max_tokens=512,
                    temperature=0.0,
                    top_p=1.0,
                    logprobs=5 if return_logprobs else None
                )
                text = completion["choices"][0]["text"].strip()
                logprobs = completion["choices"][0].get("logprobs")
                return {"text": text, "model": self.model, "logprobs": logprobs}
            except Exception as e:
                time.sleep(self.backoff * (2 ** attempt))
        raise RuntimeError("LLM generate failed after retries")