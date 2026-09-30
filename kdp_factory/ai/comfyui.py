import httpx
from .base import ImageProvider
from ..config import COMFYUI_URL

class ComfyUIProvider(ImageProvider):
    name="comfyui"
    def __init__(self, base_url=COMFYUI_URL): self.base_url=base_url.rstrip("/")
    def available(self):
        try: return httpx.get(self.base_url+"/system_stats",timeout=3).is_success
        except Exception: return False
    def generate(self,prompt,**kwargs):
        raise NotImplementedError("Workflow ComfyUI será conectado pelo Image Engine.")
