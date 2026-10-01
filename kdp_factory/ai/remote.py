from __future__ import annotations
import base64, httpx
from .base import TextProvider, ImageProvider, AIResponse
from ..config import KDP_ENGINE_URL, KDP_ENGINE_TOKEN

class RemoteEngineTextProvider(TextProvider):
    name = "remote-engine"
    def __init__(self, base_url=KDP_ENGINE_URL, token=KDP_ENGINE_TOKEN):
        self.base_url=base_url.rstrip("/")
        self.token=token
    def available(self):
        if not self.base_url: return False
        try:
            r=httpx.get(self.base_url+"/health",timeout=5)
            return r.is_success
        except Exception: return False
    def models(self):
        if not self.available(): return []
        try: return httpx.get(self.base_url+"/models",headers=self._headers(),timeout=5).json().get("models",[])
        except Exception: return []
    def _headers(self): return {"Authorization":f"Bearer {self.token}"} if self.token else {}
    def generate(self,prompt,model=None,**kwargs):
        r=httpx.post(self.base_url+"/text",json={"prompt":prompt,"model":model},headers=self._headers(),timeout=kwargs.get("timeout",300))
        r.raise_for_status(); d=r.json()
        return AIResponse(text=d.get("text",""),raw=d,model=d.get("model") or model or "remote")

class RemoteEngineImageProvider(ImageProvider):
    name = "remote-engine"
    def __init__(self, base_url=KDP_ENGINE_URL, token=KDP_ENGINE_TOKEN):
        self.base_url=base_url.rstrip("/")
        self.token=token
    def available(self):
        if not self.base_url: return False
        try: return httpx.get(self.base_url+"/health",timeout=5).is_success
        except Exception: return False
    def _headers(self): return {"Authorization":f"Bearer {self.token}"} if self.token else {}
    def generate(self,prompt,workflow_path=None,output_dir=None,**kwargs):
        workflow=None
        if workflow_path:
            import json
            from pathlib import Path
            workflow=json.loads(Path(workflow_path).read_text(encoding="utf-8"))
        r=httpx.post(self.base_url+"/image",json={"prompt":prompt,"workflow":workflow},headers=self._headers(),timeout=kwargs.get("timeout",900))
        r.raise_for_status(); d=r.json()
        files=[]
        if output_dir and d.get("images"):
            from pathlib import Path
            out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
            for i,item in enumerate(d["images"]):
                raw=base64.b64decode(item["base64"])
                dest=out/(item.get("filename") or f"image-{i+1}.png")
                dest.write_bytes(raw); files.append(str(dest))
        d["files"]=files
        return AIResponse(text=str(d),raw=d,model=d.get("model","remote-engine"))
