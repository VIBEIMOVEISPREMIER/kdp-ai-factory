from __future__ import annotations
import json
from ..config import DATA_DIR
PATH=DATA_DIR/"remote_engine.json"

def load()->dict:
    if not PATH.exists(): return {}
    try:return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:return {}

def save(url:str,token:str)->dict:
    DATA_DIR.mkdir(parents=True,exist_ok=True)
    data={"url":url.rstrip("/"),"token":token}
    PATH.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
    return data
