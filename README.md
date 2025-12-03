Enterprise grade AI Framework covering RAG pipeline, Trust controls, Explainability, Confidence, Auditability,Extensibility

- RAG pipeline: PDF → text extraction → chunking → embeddings → FAISS vectorstore → retrieval of top-k context → prompt template → OpenAI LLM call.
- Trust controls: input sanitization, prompt separation, prompt-injection detection, output policy filters, PII redaction, RBAC, rate limiting.
- Explainability: perturbation-based token importance for LLM responses (mask tokens and measure response change) and provenance linking to retrieved chunks.
- Confidence: combine model logprob-derived score (when available) with retrieval similarity and calibration to produce a final confidence score.
- Auditability: structured audit logs (SQLite for demo; replace with centralized logging in prod) with immutable records: input hash, prompt template, retrieved chunk IDs, model version, raw output, filtered output, explanation, confidence.
- Extensibility: swap gpt-5-nano model name in llm_client.py to other providers; vectorstore abstraction supports other backends.
