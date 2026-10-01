from __future__ import annotations
import base64, json, os, time
from pathlib import Path
import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app=FastAPI(title="KDP AI Engine Server",version="1.0.0")
TOKEN=os.getenv("KDP_ENGINE_TOKEN","")
OLLAMA_URL=os.getenv("OLLAMA_URL","http://127.0.0.1:11434").rstrip("/")
COMFYUI_URL=os.getenv("COMFYUI_URL","http://127.0.0.1:8188").rstrip("/")

class TextRequest(BaseModel):
    prompt:str
    model:str|None=None

class ImageRequest(BaseModel):
    prompt:str
    workflow:dict|None=None
    seed:int|None=None

def auth(value:str|None):
    if TOKEN and value != TOKEN:
        raise HTTPException(401,"Invalid engine token")

def headers(token:str|None): return {"Authorization":f"Bearer {token}"} if token else {}

@app.get("/health")
def health():
    return {"ok":True,"service":"kdp-ai-engine-server","ollama":_available_ollama(),"comfyui":_available_comfyui()}

@app.get("/models")
def models():
    try:
        data=httpx.get(OLLAMA_URL+"/api/tags",timeout=5).json()
        return {"models":[m.get("name","") for m in data.get("models",[])]}
    except Exception: return {"models":[]}

@app.post("/text")
def text(req:TextRequest,authorization:str|None=Header(default=None)):
    auth(authorization)
    model=req.model
    if not model:
        model=(models().get("models") or [None])[0]
    if not model: raise HTTPException(503,"No Ollama model installed on the GPU server.")
    r=httpx.post(OLLAMA_URL+"/api/generate",json={"model":model,"prompt":req.prompt,"stream":False},timeout=600)
    r.raise_for_status()
    d=r.json()
    return {"text":d.get("response",""),"model":model}

@app.post("/image")
def image(req:ImageRequest,authorization:str|None=Header(default=None)):
    auth(authorization)
    if not req.workflow: raise HTTPException(400,"A ComfyUI workflow JSON is required.")
    workflow=req.workflow
    seed=req.seed if req.seed is not None else int(time.time())
    def replace(v):
        if isinstance(v,str): return v.replace("{{prompt}}",req.prompt).replace("{{seed}}",str(seed))
        if isinstance(v,dict): return {k:replace(x) for k,x in v.items()}
        if isinstance(v,list): return [replace(x) for x in v]
        return v
    q=httpx.post(COMFYUI_URL+"/prompt",json={"prompt":replace(workflow)},timeout=30); q.raise_for_status()
    pid=q.json()["prompt_id"]
    started=time.time()
    while time.time()-started<900:
        h=httpx.get(COMFYUI_URL+f"/history/{pid}",timeout=10); h.raise_for_status(); data=h.json()
        if pid in data: break
        time.sleep(2)
    else: raise HTTPException(504,"ComfyUI generation timed out.")
    images=[]
    for node in data[pid].get("outputs",{}).values():
        for item in node.get("images",[]):
            p={"filename":item["filename"],"subfolder":item.get("subfolder",""),"type":item.get("type","output")}
            rr=httpx.get(COMFYUI_URL+"/view",params=p,timeout=60); rr.raise_for_status()
            images.append({"filename":item["filename"],"base64":base64.b64encode(rr.content).decode("ascii")})
    return {"images":images,"model":"comfyui","prompt_id":pid}

def _available_ollama():
    try:return httpx.get(OLLAMA_URL+"/api/tags",timeout=3).is_success
    except Exception:return False
def _available_comfyui():
    try:return httpx.get(COMFYUI_URL+"/system_stats",timeout=3).is_success
    except Exception:return False
