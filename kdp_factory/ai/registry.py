from .ollama import OllamaProvider
from .comfyui import ComfyUIProvider
from .remote import RemoteEngineTextProvider, RemoteEngineImageProvider
from ..config import KDP_ENGINE_URL, KDP_ENGINE_TOKEN

class Registry:
    def __init__(self):
        self.text=OllamaProvider()
        self.image=ComfyUIProvider()
        if KDP_ENGINE_URL:
            self.configure_remote(KDP_ENGINE_URL,KDP_ENGINE_TOKEN)
    def configure_remote(self,url:str,token:str=""):
        if url:
            self.text=RemoteEngineTextProvider(url,token)
            self.image=RemoteEngineImageProvider(url,token)
        else:
            self.text=OllamaProvider()
            self.image=ComfyUIProvider()
    def status(self):
        return {"provider":self.text.name,"available":self.text.available(),"models":self.text.models() if hasattr(self.text,"models") else []}
registry=Registry()
def providers(): return {"text":registry.text,"image":registry.image}
def status(): return registry.status()
