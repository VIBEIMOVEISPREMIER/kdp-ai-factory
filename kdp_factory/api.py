from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from pathlib import Path
from .db import init_db
from .projects import create_project,list_projects,get_project,update_project,checkpoint,project_dir
from .doctor import run_doctor
from .jobs import list_tasks,create_task,update_task
from .ai.registry import registry
from .editorial.engine import EditorialEngine
from .imports.engine import import_file,normalize_to_text
from .kdp.validator import KDPValidator
from .models.manager import ModelManager
from .export.engine import ExportEngine
from .bookflow import generate_outline,generate_manuscript,metadata
from .licensing.client import status as license_status,activate_with_license,verify_payment_and_issue_license
from .licensing.models import LicenseActivationRequest
app=FastAPI(title="KDP AI Factory",version="1.0.0")
class ProjectCreate(BaseModel):name:str=Field(min_length=1,max_length=200);book_type:str="custom";language:str="pt-BR"
class TextRequest(BaseModel):prompt:str=Field(min_length=1);model:str|None=None
class ImportRequest(BaseModel):path:str
class ValidateRequest(BaseModel):spec:dict;pdf_path:str|None=None
class CheckpointRequest(BaseModel):stage:str;state:dict={}
class PaymentRequest(BaseModel):tx_id:str=Field(min_length=20,max_length=200);asset:str=Field(pattern=r"^(USDT|BNB)$")
@app.on_event("startup")
def startup():init_db()
@app.get("/api/health")
def health():return {"ok":True,"service":"kdp-ai-factory","version":"1.0.0"}
@app.get("/api/doctor")
def doctor():return run_doctor()
@app.get("/api/ai")
def ai_status():return registry.status()
@app.get("/api/models")
def models():
 m=ModelManager();return {"hardware":m.hardware(),"ollama":m.ollama_models(),"recommended":m.recommendations()}
@app.get("/api/projects")
def projects():return list_projects()
@app.get("/api/projects/{project_id}")
def project(project_id:str):
 p=get_project(project_id)
 if not p:raise HTTPException(404,"Projeto não encontrado")
 return p
@app.get("/api/license")
def license():return license_status()
@app.post("/api/license/activate")
def activate_license(payload:LicenseActivationRequest):
 try:return activate_with_license(payload.license_token)
 except Exception as e:raise HTTPException(400,str(e))
@app.post("/api/license/payment")
def payment_license(payload:PaymentRequest):
 try:return verify_payment_and_issue_license(payload.tx_id,payload.asset)
 except Exception as e:raise HTTPException(400,str(e))
@app.post("/api/projects")
def new_project(payload:ProjectCreate):
 try:return create_project(payload.name,payload.book_type,payload.language)
 except PermissionError as e:raise HTTPException(402,str(e))
@app.patch("/api/projects/{project_id}")
def patch_project(project_id:str,payload:dict):
 p=update_project(project_id,**payload)
 if not p:raise HTTPException(404,"Projeto não encontrado")
 return p
@app.get("/api/projects/{project_id}/tasks")
def tasks(project_id:str):return list_tasks(project_id)
@app.post("/api/projects/{project_id}/tasks")
def add_task(project_id:str,payload:dict):
 if not get_project(project_id):raise HTTPException(404,"Projeto não encontrado")
 return {"id":create_task(project_id,payload.get("name","Tarefa"))}
@app.post("/api/ai/generate")
def generate(req:TextRequest):
 try:
  result=registry.text.generate(req.prompt,req.model);return {"text":result.text,"model":result.model,"raw":result.raw}
 except Exception as e:raise HTTPException(503,str(e))
@app.post("/api/editorial/outline")
def outline(req:TextRequest):
 try:return EditorialEngine().outline(req.prompt,model=req.model)
 except Exception as e:raise HTTPException(503,str(e))
@app.post("/api/import")
def do_import(req:ImportRequest):
 try:data=import_file(req.path);return {"data":data,"text":normalize_to_text(data)}
 except Exception as e:raise HTTPException(400,str(e))
@app.post("/api/projects/{project_id}/checkpoint")
def save_checkpoint(project_id:str,req:CheckpointRequest):
 if not get_project(project_id):raise HTTPException(404,"Projeto não encontrado")
 return checkpoint(project_id,req.stage,req.state)
@app.post("/api/validate")
def validate(req:ValidateRequest):
 issues=KDPValidator().validate_pdf(req.pdf_path,req.spec) if req.pdf_path else KDPValidator().validate_spec(req.spec)
 return {"ok":not any(x.level=="error" for x in issues),"issues":[x.__dict__ for x in issues]}
