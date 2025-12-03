# test_end_to_end.py - integration / smoke tests 
# tests/test_end_to_end.py
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_query_requires_key():
    resp = client.post("/query", json={"text":"What is clause 2?"})
    assert resp.status_code == 422 or resp.status_code == 401  # missing header

def test_ingest_and_query_flow(monkeypatch):
    # This test assumes API key set in env; for CI, set API_MASTER_KEY to 'test'
    # Mock vectorstore and llm for speed in CI if needed
    pass