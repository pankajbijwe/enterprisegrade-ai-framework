Enterprise grade AI Framework covering RAG pipeline, Trust controls, Explainability, Confidence, Auditability,Extensibility

- RAG pipeline: PDF → text extraction → chunking → embeddings → FAISS vectorstore → retrieval of top-k context → prompt template → OpenAI LLM call.
- Trust controls: input sanitization, prompt separation, prompt-injection detection, output policy filters, PII redaction, RBAC, rate limiting.
- Explainability: perturbation-based token importance for LLM responses (mask tokens and measure response change) and provenance linking to retrieved chunks.
- Confidence: combine model logprob-derived score (when available) with retrieval similarity and calibration to produce a final confidence score.
- Auditability: structured audit logs (SQLite for demo; replace with centralized logging in prod) with immutable records: input hash, prompt template, retrieved chunk IDs, model version, raw output, filtered output, explanation, confidence.
- Extensibility: swap gpt-5-nano model name in llm_client.py to other providers; vectorstore abstraction supports other backends.


**Setup Instructions**
Recommended (easy, reliable) — use conda-forge binary (no compiler needed)
If you can use conda, this is the simplest and most robust option on Windows.
# create and activate conda env with Python 3.11.9
conda create -n contractminer python=3.11.9 -y
conda activate contractminer

# install hnswlib (binary) from conda-forge
conda install -c conda-forge hnswlib -y

# install the rest of pip requirements (without hnswlib in requirements.txt)
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

Notes
- Remove hnswlib from requirements.txt (or keep it but install conda package first).
- If you prefer FAISS, install faiss-cpu via conda install -c pytorch faiss-cpu -y instead.

Option B — install Microsoft C++ Build Tools (if you must pip-build)
If you cannot use conda, install the Visual C++ Build Tools so pip can compile hnswlib.
- Download and install Build Tools:
- Open: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- During install, select "C++ build tools" workload (MSVC v142 or later, Windows 10/11 SDK).
- Restart your terminal (important — PATH updates take effect after restart).
- Create venv and install:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install hnswlib
pip install -r requirements.txt


Troubleshooting
- If build still fails, open "x64 Native Tools Command Prompt for VS" and run pip there.
- Ensure your Python architecture (x64) matches the installed MSVC toolchain.

