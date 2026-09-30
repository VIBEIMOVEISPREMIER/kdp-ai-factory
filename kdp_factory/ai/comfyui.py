from __future__ import annotations
import time, json
from pathlib import Path
import httpx
from .base import ImageProvider, AIResponse
from ..config import COMFYUI_URL

class ComfyUIProvider(ImageProvider):
    name="comfyui"
    def __init__(self,base_url=COMFYUI_URL): self.base_url=base_url.rstrip("/")
    def available(self):
        try: return httpx.get(self.base_url+"/system_stats",timeout=3).is_success
        except Exception: return False
    def queue(self,workflow:dict,client_id="kdp-ai-factory"):
        r=httpx.post(self.base_url+"/prompt",json={"prompt":workflow,"client_id":client_id},timeout=30); r.raise_for_status(); return r.json()
    def wait(self,prompt_id:str,timeout=900,poll=2):
        started=time.time()
        while time.time()-started<timeout:
            r=httpx.get(self.base_url+f"/history/{prompt_id}",timeout=10); r.raise_for_status()
            data=r.json()
            if prompt_id in data: return data[prompt_id]
            time.sleep(poll)
        raise TimeoutError(f"ComfyUI não concluiu o job {prompt_id} em {timeout}s.")
    def generate(self,prompt,workflow_path=None,output_dir=None,timeout=900,**kwargs):
        if workflow_path is None: raise ValueError("Informe um workflow JSON do ComfyUI.")
        workflow=json.loads(Path(workflow_path).read_text(encoding="utf-8"))
        seed=kwargs.get("seed",int(time.time()))
        def replace(v):
            if isinstance(v,str): return v.replace("{{prompt}}",prompt).replace("{{seed}}",str(seed))
            if isinstance(v,dict): return {k:replace(x) for k,x in v.items()}
            if isinstance(v,list): return [replace(x) for x in v]
            return v
        result=self.queue(replace(workflow))
        history=self.wait(result["prompt_id"],timeout=timeout)
        files=[]
        if output_dir:
            out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
            for node in history.get("outputs",{}).values():
                for img in node.get("images",[]):
                    params={"filename":img["filename"],"subfolder":img.get("subfolder",""),"type":img.get("type","output")}
                    rr=httpx.get(self.base_url+"/view",params=params,timeout=60); rr.raise_for_status()
                    dest=out/img["filename"]; dest.write_bytes(rr.content); files.append(str(dest))
        return AIResponse(text=json.dumps({"prompt_id":result["prompt_id"],"files":files}),raw=history,model="comfyui")
