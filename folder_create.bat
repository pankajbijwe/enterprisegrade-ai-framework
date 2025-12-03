@echo off
REM create_structure.bat
REM Creates contract_miner project folders and placeholder files

set "ROOT=contract_miner"

echo Creating project structure under "%CD%\%ROOT%"

REM Create directories
mkdir "%ROOT%" 2>nul
mkdir "%ROOT%\api" 2>nul
mkdir "%ROOT%\services" 2>nul
mkdir "%ROOT%\storage" 2>nul
mkdir "%ROOT%\tests" 2>nul

REM Create placeholder files in api
echo # main.py - FastAPI entrypoint > "%ROOT%\api\main.py"
echo # schemas.py - Pydantic schemas and request/response models > "%ROOT%\api\schemas.py"

REM Create placeholder files in services
echo # llm_client.py - OpenAI / provider client wrapper > "%ROOT%\services\llm_client.py"
echo # pdf_ingest.py - PDF extraction utilities > "%ROOT%\services\pdf_ingest.py"
echo # chunker.py - Text chunking utilities > "%ROOT%\services\chunker.py"
echo # retriever.py - Retrieval logic / vectorstore adapter > "%ROOT%\services\retriever.py"
echo # prompt_template.py - Prompt templating utilities > "%ROOT%\services\prompt_template.py"
echo # sanitizer.py - Input sanitization and prompt-injection detection > "%ROOT%\services\sanitizer.py"
echo # output_filter.py - PII redaction and policy filters > "%ROOT%\services\output_filter.py"
echo # explainability.py - Explainability helpers (perturbation, provenance) > "%ROOT%\services\explainability.py"
echo # confidence.py - Confidence scoring and calibration helpers > "%ROOT%\services\confidence.py"
echo # auth.py - Simple API key / RBAC helpers > "%ROOT%\services\auth.py"

REM Create placeholder files in storage
echo # vectorstore.py - FAISS / vector DB wrapper > "%ROOT%\storage\vectorstore.py"
echo # audit_store.py - Audit logging (SQLite / persistent store) > "%ROOT%\storage\audit_store.py"

REM Create placeholder tests
echo # test_end_to_end.py - integration / smoke tests > "%ROOT%\tests\test_end_to_end.py"
echo # test_prompt_injection.py - unit tests for sanitizer > "%ROOT%\tests\test_prompt_injection.py"

REM Top-level files
echo fastapi==0.95.2 > "%ROOT%\requirements.txt"
echo # ContractMiner README - overview, setup, run instructions > "%ROOT%\README.md"
echo OPENAI_API_KEY=your_openai_api_key_here> "%ROOT%\.env.example"
echo OPENAI_MODEL=gpt-5-nano>> "%ROOT%\.env.example"
echo EMBEDDING_MODEL=text-embedding-3-large>> "%ROOT%\.env.example"
echo VECTORSTORE_PATH=./storage/faiss_index>> "%ROOT%\.env.example"
echo AUDIT_DB=sqlite:///./storage/audit.db>> "%ROOT%\.env.example"
echo API_MASTER_KEY=replace_with_strong_key>> "%ROOT%\.env.example"
echo RATE_LIMIT_PER_MINUTE=60>> "%ROOT%\.env.example"

REM Confirm
echo.
echo Created folders and files:
tree "%ROOT%" /F
echo.
echo Done.
pause