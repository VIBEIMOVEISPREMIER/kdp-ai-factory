from __future__ import annotations
import base64, hashlib, json
from pathlib import Path
from typing import Any
import httpx
from cryptography.fernet import Fernet
from .base import TextProvider, ImageProvider, AIResponse
from ..config import DATA_DIR
from ..licensing.machine import machine_id

PATH = DATA_DIR / "ai_providers.enc"

def _fernet() -> Fernet:
    raw = hashlib.sha256(("kdp-ai-factory-ai-keys-v1|" + machine_id()).encode()).digest()
    return Fernet(base64.urlsafe_b64encode(raw))

def _load() -> list[dict[str, Any]]:
    if not PATH.exists():
        return []
    try:
        data = _fernet().decrypt(PATH.read_bytes())
        return json.loads(data.decode("utf-8"))
    except Exception:
        return []

def _save(items: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PATH.write_bytes(_fernet().encrypt(json.dumps(items, ensure_ascii=False).encode("utf-8")))

def list_providers() -> list[dict[str, Any]]:
    result=[]
    for p in _load():
        result.append({k:v for k,v in p.items() if k != "api_key"})
        result[-1]["key_configured"] = bool(p.get("api_key"))
    return result

def get_provider(provider_id: str) -> dict[str, Any] | None:
    return next((p for p in _load() if p.get("id")==provider_id), None)

def upsert_provider(data: dict[str, Any]) -> dict[str, Any]:
    p=dict(data)
    p["id"]=str(p.get("id") or p.get("name") or "custom").strip().lower().replace(" ","-")
    items=[x for x in _load() if x.get("id") != p["id"]]
    old=get_provider(p["id"])
    if old and not p.get("api_key"):
        p["api_key"]=old.get("api_key","")
    p.setdefault("kind","text")
    p.setdefault("priority",100)
    p.setdefault("base_url","")
    p.setdefault("endpoint","/v1/chat/completions")
    p.setdefault("model","")
    items.append(p)
    _save(items)
    return {k:v for k,v in p.items() if k!="api_key"} | {"key_configured":bool(p.get("api_key"))}

def remove_provider(provider_id: str) -> bool:
    items=[x for x in _load() if x.get("id") != provider_id]
    changed=len(items) != len(_load())
    if changed: _save(items)
    return changed

class OpenAICompatibleTextProvider(TextProvider):
    def __init__(self, config: dict[str,Any]):
        self.config=config
        self.name=config.get("name") or config.get("id") or "custom"
    def _url(self):
        base=self.config.get("base_url","").rstrip("/")
        ep=self.config.get("endpoint","/v1/chat/completions")
        return f"{base}/{ep.lstrip('/')}"
    def _headers(self):
        h={"Content-Type":"application/json"}
        if self.config.get("api_key"): h["Authorization"]=f"Bearer {self.config['api_key']}"
        h.update(self.config.get("headers") or {})
        return h
    def models(self):
        m=self.config.get("model","")
        return [m] if m else []
    def available(self):
        return bool(self.config.get("api_key") and self.config.get("base_url"))
    def generate(self,prompt,model=None,**kwargs):
        if not self.available(): raise RuntimeError(f"API {self.name} não está configurada.")
        payload={"model":model or self.config.get("model"),"messages":[{"role":"user","content":prompt}]}
        for k in ("temperature","top_p","max_tokens"):
            if k in kwargs: payload[k]=kwargs[k]
        r=httpx.post(self._url(),json=payload,headers=self._headers(),timeout=kwargs.get("timeout",300))
        r.raise_for_status()
        d=r.json()
        choices=d.get("choices") or []
        if not choices: raise RuntimeError(f"{self.name} retornou uma resposta sem choices.")
        msg=choices[0].get("message") or {}
        content=msg.get("content","")
        if isinstance(content,list):
            content="".join(x.get("text","") if isinstance(x,dict) else str(x) for x in content)
        return AIResponse(text=str(content),raw=d,model=d.get("model") or model or self.config.get("model",""))

class UserImageAPIProvider(ImageProvider):
    def __init__(self,config):
        self.config=config; self.name=config.get("name") or config.get("id") or "custom-image"
    def available(self): return bool(self.config.get("api_key") and self.config.get("base_url"))
    def generate(self,prompt,**kwargs):
        base=self.config.get("base_url","").rstrip("/")
        ep=self.config.get("endpoint","/v1/images/generations")
        url=f"{base}/{ep.lstrip('/')}"
        headers={"Content-Type":"application/json","Authorization":f"Bearer {self.config['api_key']"}
        payload={"prompt":prompt}
        if self.config.get("model"): payload["model"]=self.config["model"]
        payload.update(self.config.get("extra_body") or {})
        r=httpx.post(url,json=payload,headers=headers,timeout=kwargs.get("timeout",900))
        r.raise_for_status(); return r.json()
