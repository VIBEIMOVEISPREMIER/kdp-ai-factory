from __future__ import annotations
import json
from pathlib import Path
class MetadataEngine:
    def generate(self, title:str, description:str, language:str, audience:str, model=None):
        return {"title":title,"description":description,"language":language,"audience":audience,"keywords":[],"categories":[],"ai_generated":True}
    def save(self,data:dict,path:Path):
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
