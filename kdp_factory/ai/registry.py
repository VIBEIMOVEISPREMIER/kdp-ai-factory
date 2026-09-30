from .ollama import OllamaProvider
from .comfyui import ComfyUIProvider
class Registry:
    def __init__(self):
        self.text=OllamaProvider(); self.image=ComfyUIProvider()
    def status(self):
        return {"ollama":{"available":self.text.available(),"models":self.text.models() if self.text.available() else []},"comfyui":{"available":self.image.available(),"models":[]}}
registry=Registry()
def providers(): return {"ollama":registry.text,"comfyui":registry.image}
def status(): return registry.status()
