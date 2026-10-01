from __future__ import annotations
from .base import AIResponse
from .ollama import OllamaProvider
from .comfyui import ComfyUIProvider
from .user_providers import list_providers as stored_providers, OpenAICompatibleTextProvider, UserImageAPIProvider, get_provider

class AIRouter:
    def __init__(self):
        self.local_text=OllamaProvider()
        self.local_image=ComfyUIProvider()
    def _text_candidates(self, requested=None):
        candidates=[]
        if self.local_text.available():
            candidates.append((0,self.local_text))
        for p in sorted(stored_providers(), key=lambda x:int(x.get("priority",100))):
            if p.get("kind","text") in ("text","both") and p.get("key_configured"):
                cfg=get_provider(p["id"])
                if cfg: candidates.append((int(cfg.get("priority",100)),OpenAICompatibleTextProvider(cfg)))
        return candidates
    def generate(self,prompt,model=None,**kwargs):
        return self.text(prompt,model,**kwargs)
    def text(self,prompt,model=None,**kwargs):
        errors=[]
        for _,provider in self._text_candidates(model):
            try: return provider.generate(prompt,model,**kwargs)
            except Exception as exc: errors.append(f"{provider.name}: {exc}")
        raise RuntimeError("Nenhum provedor de texto disponível. Configure uma API própria/gratuita ou instale um modelo local. | "+" | ".join(errors))
    def image_candidates(self):
        candidates=[]
        if self.local_image.available(): candidates.append(self.local_image)
        for p in stored_providers():
            if p.get("kind") in ("image","both") and p.get("key_configured"):
                cfg=get_provider(p["id"])
                if cfg: candidates.append(UserImageAPIProvider(cfg))
        return candidates
    def image(self,prompt,**kwargs):
        errors=[]
        for provider in self.image_candidates():
            try: return provider.generate(prompt,**kwargs)
            except Exception as exc: errors.append(f"{provider.name}: {exc}")
        raise RuntimeError("Nenhum provedor de imagem disponível. Configure uma API de imagem ou ComfyUI local. | "+" | ".join(errors))
    def status(self):
        text=[{"name":"ollama","kind":"local","available":self.local_text.available(),"models":self.local_text.models()}]
        for p in stored_providers():
            text.append({"id":p["id"],"name":p.get("name",p["id"]),"kind":p.get("kind","text"),"key_configured":p.get("key_configured",False),"model":p.get("model",""),"priority":p.get("priority",100)})
        return {"text":text,"image":{"comfyui_local":self.local_image.available(),"providers":[x for x in text if x["kind"] in ("image","both")]}}
