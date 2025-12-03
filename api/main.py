# main.py - FastAPI entrypoint 
# api/main.py
import os, hashlib, time, json
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.auth import require_api_key
from services.pdf_ingest import extract_text_from_pdf
from services.chunker import chunk_text
from storage.vectorstore import VectorStore
from services.retriever import Retriever
from services.prompt_template import build_prompt
from services.sanitizer import sanitize_input, detect_prompt_injection
from services.llm_client import OpenAIClient
from services.output_filter import filter_output_and_redact
from services.explainability import explain_response_perturbation
from services.confidence import compute_confidence
from storage.audit_store import AuditStore
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ContractMiner API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Init components
VECTOR_PATH = os.getenv("VECTORSTORE_PATH", "./storage/faiss_index")
vectorstore = VectorStore(VECTOR_PATH)
retriever = Retriever(vectorstore)
llm = OpenAIClient()
audit = AuditStore(os.getenv("AUDIT_DB", "sqlite:///./storage/audit.db"))

class QueryRequest(BaseModel):
    text: str
    top_k: int = 5
    include_explain: bool = True

@app.post("/ingest_pdf", dependencies=[Depends(require_api_key)])
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF supported")
    content = await file.read()
    text = extract_text_from_pdf(content)
    chunks = chunk_text(text)
    ids = vectorstore.add_documents(chunks)
    return {"status":"ok", "chunks_indexed": len(ids)}

@app.post("/query")
@limiter.limit(f"{int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))}/minute")
async def query_endpoint(req: QueryRequest, request: Request, api_key: str = Depends(require_api_key)):
    user_text = req.text
    sanitized = sanitize_input(user_text)
    if detect_prompt_injection(user_text):
        raise HTTPException(status_code=400, detail="Prompt injection detected")

    # Retrieve context
    query_embedding = llm.embed_text(sanitized)
    retrieved = retriever.retrieve_by_embedding(query_embedding, top_k=req.top_k)

    # Build prompt with strict separation
    prompt = build_prompt(system_instructions=llm.system_prompt(), user_text=sanitized, context_chunks=retrieved)

    # Call LLM
    llm_resp = llm.generate(prompt, return_logprobs=True)

    # Output filtering and redaction
    filtered_text, redaction_meta = filter_output_and_redact(llm_resp["text"])

    # Explainability (perturbation-based token importance + provenance)
    explanation = None
    if req.include_explain:
        explanation = explain_response_perturbation(
            llm_client=llm,
            prompt=prompt,
            response=llm_resp["text"],
            retrieved_chunks=retrieved
        )

    # Confidence scoring
    confidence = compute_confidence(
        logprobs=llm_resp.get("logprobs"),
        retrieval_scores=[r["score"] for r in retrieved],
        calibration_model=None  # placeholder for production calibration
    )

    # Audit log
    input_hash = hashlib.sha256(sanitized.encode()).hexdigest()
    audit_id = audit.log({
        "ts": time.time(),
        "input_hash": input_hash,
        "prompt_template": prompt["template_id"],
        "prompt_text": prompt["text"],
        "retrieved_ids": [r["id"] for r in retrieved],
        "model_version": llm_resp.get("model"),
        "raw_response": llm_resp["text"],
        "filtered_response": filtered_text,
        "confidence": confidence,
        "explanation": explanation,
        "redaction": redaction_meta
    })

    return JSONResponse({
        "response": filtered_text,
        "confidence_score": confidence,
        "explanation": explanation,
        "model_version": llm_resp.get("model"),
        "input_hash": input_hash,
        "audit_id": audit_id
    })