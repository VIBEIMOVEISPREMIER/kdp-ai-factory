from __future__ import annotations
from .base import AIResponse
from .ollama import OllamaProvider
from .comfyui import ComfyUIProvider
from .user_providers import list_providers as stored_providers, OpenAICompatibleTextProvider, UserImageAPIProvider, UserVideoAPIProvider, get_provider
from .remote import RemoteEngineTextProvider, RemoteEngineImageProvider

class AIRouter:
    def __init__(self):
        self.local_text=OllamaProvider()
        self.local_image=ComfyUIProvider()
        self.remote_text=None
        self.remote_image=None
    def configure_remote(self,url:str,token:str=""):
        self.remote_text=RemoteEngineTextProvider(url,token) if url else None
        self.remote_image=RemoteEngineImageProvider(url,token) if url else None
    def _text_candidates(self, requested=None):
        candidates=[]
        # Cloud/user APIs are preferred. Local Ollama is an automatic fallback,
        # which keeps weak computers responsive.
        for p in sorted(stored_providers(), key=lambda x:int(x.get("priority",100))):
            if p.get("kind","text") in ("text","both","all") and p.get("key_configured"):
                cfg=get_provider(p["id"])
                if cfg: candidates.append((int(cfg.get("priority",100)),OpenAICompatibleTextProvider(cfg)))
        if self.remote_text and self.remote_text.available():
            candidates.append((50,self.remote_text))
        if self.local_text.available():
            candidates.append((1000,self.local_text))
        return sorted(candidates,key=lambda x:x[0])
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
        for p in sorted(stored_providers(), key=lambda x:int(x.get("priority",100))):
            if p.get("kind") in ("image","both","all") and p.get("key_configured"):
                cfg=get_provider(p["id"])
                if cfg: candidates.append(UserImageAPIProvider(cfg))
        if self.remote_image and self.remote_image.available(): candidates.append(self.remote_image)
        if self.local_image.available(): candidates.append(self.local_image)
        return candidates

    def video_candidates(self):
        candidates=[]
        for p in sorted(stored_providers(), key=lambda x:int(x.get("priority",100))):
            if p.get("kind") in ("video","all") and p.get("key_configured"):
                cfg=get_provider(p["id"])
                if cfg: candidates.append((int(cfg.get("priority",100)),UserVideoAPIProvider(cfg)))
        return [x[1] for x in sorted(candidates,key=lambda x:x[0])]

    def video(self,prompt,**kwargs):
        errors=[]
        for provider in self.video_candidates():
            try: return provider.generate(prompt,**kwargs)
            except Exception as exc: errors.append(f"{provider.name}: {exc}")
        raise RuntimeError("Nenhum provedor de vídeo disponível. Cadastre uma API de vídeo na aba Vídeo. | "+" | ".join(errors))
    def image(self,prompt,**kwargs):
        errors=[]
        for provider in self.image_candidates():
            try: return provider.generate(prompt,**kwargs)
            except Exception as exc: errors.append(f"{provider.name}: {exc}")
        raise RuntimeError("Nenhum provedor de imagem disponível. Configure uma API de imagem ou ComfyUI local. | "+" | ".join(errors))
    def status(self):
        providers=[{"id":p["id"],"name":p.get("name",p["id"]),"kind":p.get("kind","text"),"key_configured":p.get("key_configured",False),"model":p.get("model",""),"priority":p.get("priority",100)} for p in stored_providers()]
        return {"text":{"providers":providers,"ollama_local":self.local_text.available()},"image":{"comfyui_local":self.local_image.available(),"remote_engine":bool(self.remote_image and self.remote_image.available()),"providers":[x for x in providers if x["kind"] in ("image","both","all")]},"video":{"providers":[x for x in providers if x["kind"] in ("video","all")]}}
