from __future__ import annotations
import platform, shutil
try:
 import psutil
except ImportError: psutil=None
from ..ai.ollama import OllamaProvider
class ModelManager:
    def hardware(self):
        ram=round((psutil.virtual_memory().total if psutil else 0)/1024**3,1)
        return {"os":platform.system(),"arch":platform.machine(),"ram_gb":ram,"ollama_installed":shutil.which("ollama") is not None}
    def ollama_models(self):
        try: return OllamaProvider().models()
        except Exception: return []
    def recommendations(self):
        ram=self.hardware()["ram_gb"]
        if ram>=32: return [{"model":"qwen3:8b","reason":"boa capacidade geral"},{"model":"llama3.1:8b","reason":"texto geral"}]
        if ram>=16: return [{"model":"qwen3:4b","reason":"equilíbrio entre qualidade e memória"}]
        return [{"model":"qwen3:1.7b","reason":"perfil leve"}]
