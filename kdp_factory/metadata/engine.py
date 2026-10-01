from __future__ import annotations
import json
from pathlib import Path
class MetadataEngine:
    FIELDS=("title","subtitle","author","contributors","series","edition","description","language","keywords","categories","audience","reading_age_min","reading_age_max","grade","isbn","publication_rights","publisher","trim_size","bleed","page_count")
    def generate(self,title,description,language,audience,model=None,**extra):
        data={"title":title,"subtitle":"","author":"","contributors":[],"series":"","edition":"","description":description,"language":language,"keywords":[],"categories":[],"audience":audience,"reading_age_min":None,"reading_age_max":None,"grade":"","isbn":"","publication_rights":"","publisher":"","trim_size":"","bleed":False,"page_count":None,"ai_generated":True}
        data.update({k:v for k,v in extra.items() if k in self.FIELDS}); data["notes"]="Revise os metadados antes da publicação e mantenha título, autor e idioma consistentes com o arquivo enviado ao KDP."; return data
    def save(self,data,path): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    def package(self,data): return json.dumps(data,ensure_ascii=False,indent=2)
