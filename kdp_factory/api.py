from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
from .db import init_db
from .projects import create_project, list_projects, get_project, update_project, checkpoint, project_dir
from .doctor import run_doctor
from .jobs import list_tasks, create_task, update_task
from .ai.registry import registry
from .editorial.engine import EditorialEngine
from .imports.engine import import_file, normalize_to_text
from .kdp.validator import KDPValidator
from .models.manager import ModelManager
from .export.engine import ExportEngine
from .bookflow import generate_outline, generate_manuscript, metadata

app=FastAPI(title="KDP AI Factory",version="1.0.0")

class ProjectCreate(BaseModel):
    name:str=Field(min_length=1,max_length=200)
    book_type:str="custom"
    language:str="pt-BR"
class TextRequest(BaseModel):
    prompt:str=Field(min_length=1)
    model:str|None=None
class ImportRequest(BaseModel):
    path:str
class ValidateRequest(BaseModel):
    spec:dict
    pdf_path:str|None=None
class CheckpointRequest(BaseModel):
    stage:str
    state:dict={}

@app.on_event("startup")
def startup(): init_db()

@app.get("/api/health")
def health(): return {"ok":True,"service":"kdp-ai-factory","version":"1.0.0"}

@app.get("/api/doctor")
def doctor(): return run_doctor()

@app.get("/api/ai")
def ai_status(): return registry.status()

@app.get("/api/models")
def models():
    m=ModelManager()
    return {"hardware":m.hardware(),"ollama":m.ollama_models(),"recommended":m.recommendations()}

@app.get("/api/projects")
def projects(): return list_projects()

@app.get("/api/projects/{project_id}")
def project(project_id:str):
    p=get_project(project_id)
    if not p: raise HTTPException(404,"Projeto não encontrado")
    return p

@app.post("/api/projects")
def new_project(payload:ProjectCreate):
    return create_project(payload.name,payload.book_type,payload.language)

@app.patch("/api/projects/{project_id}")
def patch_project(project_id:str,payload:dict):
    p=update_project(project_id,**payload)
    if not p: raise HTTPException(404,"Projeto não encontrado")
    return p

@app.get("/api/projects/{project_id}/tasks")
def tasks(project_id:str): return list_tasks(project_id)

@app.post("/api/projects/{project_id}/tasks")
def add_task(project_id:str,payload:dict):
    if not get_project(project_id): raise HTTPException(404,"Projeto não encontrado")
    return {"id":create_task(project_id,payload.get("name","Tarefa"))}

@app.post("/api/ai/generate")
def generate(req:TextRequest):
    try:
        result=registry.text.generate(req.prompt,req.model)
        return {"text":result.text,"model":result.model,"raw":result.raw}
    except Exception as e:
        raise HTTPException(503,str(e))

@app.post("/api/editorial/outline")
def outline(req:TextRequest):
    try: return EditorialEngine().outline(req.prompt,model=req.model)
    except Exception as e: raise HTTPException(503,str(e))

@app.post("/api/import")
def do_import(req:ImportRequest):
    try: data=import_file(req.path); return {"data":data,"text":normalize_to_text(data)}
    except Exception as e: raise HTTPException(400,str(e))

@app.post("/api/projects/{project_id}/checkpoint")
def save_checkpoint(project_id:str,req:CheckpointRequest):
    if not get_project(project_id): raise HTTPException(404,"Projeto não encontrado")
    return checkpoint(project_id,req.stage,req.state)

@app.post("/api/validate")
def validate(req:ValidateRequest):
    issues=KDPValidator().validate_pdf(req.pdf_path,req.spec) if req.pdf_path else KDPValidator().validate_spec(req.spec)
    return {"ok":not any(x.level=="error" for x in issues),"issues":[x.__dict__ for x in issues]}

@app.post("/api/projects/{project_id}/import")
def project_import(project_id:str,req:ImportRequest):
    p=get_project(project_id)
    if not p: raise HTTPException(404,"Projeto não encontrado")
    data=import_file(req.path); src=Path(req.path)
    dest=project_dir(project_id)/"imports"/src.name
    dest.write_bytes(src.read_bytes())
    (project_dir(project_id)/"imports"/(src.stem+".txt")).write_text(normalize_to_text(data),encoding="utf-8")
    return {"ok":True,"filename":src.name,"type":data.get("type")}


@app.post("/api/projects/{project_id}/export")
def export_project(project_id:str, payload:dict):
    project=get_project(project_id)
    if not project: raise HTTPException(404,"Projeto não encontrado")
    chapters=payload.get("chapters",[])
    fmt=payload.get("format","pdf").lower()
    out=project_dir(project_id)/"exports"/f"{project_id}.{fmt}"
    try:
        engine=ExportEngine()
        if fmt=="pdf": engine.pdf(chapters,out,payload.get("title",project["name"]),payload.get("author",""),project["spec"].get("trim_size","8.5x11"),project["spec"].get("bleed",False))
        elif fmt=="docx": engine.docx(chapters,out,payload.get("title",project["name"]),payload.get("author",""))
        elif fmt=="epub": engine.epub(chapters,out,payload.get("title",project["name"]),project["language"])
        else: raise HTTPException(400,"Formato de exportação inválido.")
        return {"ok":True,"format":fmt,"path":str(out)}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500,str(e))


class OutlineRequest(BaseModel):
    brief:str=Field(min_length=1)
    chapters:int=10
    model:str|None=None

@app.post("/api/projects/{project_id}/outline")
def create_outline(project_id:str,req:OutlineRequest):
    try: return generate_outline(project_id,req.brief,req.chapters,req.model)
    except Exception as e: raise HTTPException(400,str(e))

@app.post("/api/projects/{project_id}/manuscript")
def create_manuscript(project_id:str,payload:dict):
    try: return generate_manuscript(project_id,payload["outline"],payload.get("model"))
    except Exception as e: raise HTTPException(400,str(e))

@app.post("/api/projects/{project_id}/metadata")
def create_metadata(project_id:str,payload:dict):
    try: return metadata(project_id,payload.get("description",""),payload.get("audience",""))
    except Exception as e: raise HTTPException(400,str(e))
