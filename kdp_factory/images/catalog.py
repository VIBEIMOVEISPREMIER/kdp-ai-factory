from __future__ import annotations
from pathlib import Path
import json, uuid
def register_asset(project_dir:Path,source:Path,kind="image",prompt="",model="")->dict:
    asset={"id":str(uuid.uuid4()),"source":str(source),"kind":kind,"prompt":prompt,"model":model}
    p=project_dir/"images"/"assets.json"; p.parent.mkdir(parents=True,exist_ok=True)
    items=json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    items.append(asset); p.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
    return asset
def list_assets(project_dir:Path): 
    p=project_dir/"images"/"assets.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
