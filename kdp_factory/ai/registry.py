from .ollama import OllamaProvider
from .comfyui import ComfyUIProvider

def providers():
    return {"ollama": OllamaProvider(), "comfyui": ComfyUIProvider()}

def status():
    return {name: {"available": p.available(), "models": p.models() if hasattr(p,"models") and p.available() else []}
            for name,p in providers().items()}
