from __future__ import annotations
import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="KDP AI Engine Server", version="1.0.0")
TOKEN = os.getenv("KDP_ENGINE_TOKEN", "")

class GenerateRequest(BaseModel):
    prompt: str
    model: str | None = None
    workflow: dict | None = None

def auth(token: str | None):
    if TOKEN and token != TOKEN:
        raise HTTPException(401, "Invalid engine token")

@app.get("/health")
def health():
    return {"ok": True, "service": "kdp-ai-engine-server"}

@app.get("/capabilities")
def capabilities():
    return {"text": True, "images": True, "providers": ["ollama", "comfyui"]}

@app.post("/generate")
def generate(req: GenerateRequest, authorization: str | None = Header(default=None)):
    auth(authorization.removeprefix("Bearer ").strip() if authorization else None)
    return {"ok": False, "message": "Configure the Ollama/ComfyUI adapters for this GPU server."}
