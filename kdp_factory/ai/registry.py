from .ollama import OllamaProvider
from .comfyui import ComfyUIProvider
from .remote import RemoteEngineTextProvider, RemoteEngineImageProvider
from ..config import KDP_ENGINE_URL, KDP_ENGINE_TOKEN
from .remote_config import load

class Registry:
    def __init__(self):
        self.text=OllamaProvider()
        self.image=ComfyUIProvider()
        saved=load()
        url=KDP_ENGINE_URL or saved.get("url","")
        token=KDP_ENGINE_TOKEN or saved.get("token","")
        if url:
            self.configure_remote(url,token)
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
