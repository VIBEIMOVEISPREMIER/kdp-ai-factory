from .ollama import OllamaProvider
from .comfyui import ComfyUIProvider
from .remote import RemoteEngineTextProvider, RemoteEngineImageProvider
from ..config import KDP_ENGINE_URL

class Registry:
    def __init__(self):
        if KDP_ENGINE_URL:
            self.text=RemoteEngineTextProvider()
            self.image=RemoteEngineImageProvider()
        else:
            self.text=OllamaProvider()
            self.image=ComfyUIProvider()
    def status(self):
        return {"provider":self.text.name,"available":self.text.available(),"models":self.text.models() if hasattr(self.text,"models") else []}
registry=Registry()
def providers(): return {"text":registry.text,"image":registry.image}
def status(): return registry.status()
