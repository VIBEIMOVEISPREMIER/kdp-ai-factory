import httpx
from .base import TextProvider, AIResponse
from ..config import OLLAMA_URL

class OllamaProvider(TextProvider):
    name = "ollama"
    def __init__(self, base_url=OLLAMA_URL): self.base_url=base_url.rstrip("/")
    def available(self):
        try: return httpx.get(self.base_url+"/api/tags", timeout=3).is_success
        except Exception: return False
    def models(self):
        try:
            data=httpx.get(self.base_url+"/api/tags", timeout=5).json()
            return [m.get("name","") for m in data.get("models",[])]
        except Exception: return []
    def generate(self, prompt, model=None, **kwargs):
        if not model:
            models=self.models()
            if not models: raise RuntimeError("Nenhum modelo Ollama instalado.")
            model=models[0]
        payload={"model":model,"prompt":prompt,"stream":False}
        payload.update({k:v for k,v in kwargs.items() if k in {"temperature","top_p","num_ctx"}})
        r=httpx.post(self.base_url+"/api/generate",json=payload,timeout=kwargs.get("timeout",300))
        r.raise_for_status(); data=r.json()
        return AIResponse(text=data.get("response",""),raw=data,model=model)
