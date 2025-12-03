# auth.py - Simple API key / RBAC helpers 
# services/auth.py
import os
from fastapi import Header, HTTPException, Depends

MASTER_KEY = os.getenv("API_MASTER_KEY", "dev-key")

def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != MASTER_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True