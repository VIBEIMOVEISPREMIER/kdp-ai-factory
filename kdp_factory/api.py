from fastapi import FastAPI,HTTPException
from fastapi.staticfiles import StaticFiles
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
from .bookflow import generate_outline,generate_manuscript,metadata,export_project,generate_cover
from .licensing.client import status as license_status,activate_with_license,verify_payment_and_issue_license
from .licensing.models import LicenseActivationRequest
from .hardware import as_dict as hardware_profile
from .ai.image_providers import list_providers, upsert_provider, generate as generate_image_api
from .ai.remote_config import load as load_remote_config, save as save_remote_config
from .ai.user_providers import list_providers as list_ai_providers, upsert_provider as upsert_ai_provider, remove_provider as remove_ai_provider
app=FastAPI(title="KDP AI Factory",version="1.0.0")
class ProjectCreate(BaseModel): name:str=Field(min_length=1,max_length=200);book_type:str="custom";language:str="pt-BR";subject:str="";edition:str="print"
class TextRequest(BaseModel): prompt:str=Field(min_length=1);model:str|None=None
class ImportRequest(BaseModel): path:str
class ValidateRequest(BaseModel): spec:dict;pdf_path:str|None=None
class CheckpointRequest(BaseModel): stage:str;state:dict={}
class PaymentRequest(BaseModel): tx_id:str=Field(min_length=20,max_length=200);asset:str=Field(pattern=r"^(USDT|BNB)$")
@app.on_event("startup")
def startup(): init_db()
@app.get("/api/health")
def health(): return {"ok":True,"service":"kdp-ai-factory","version":"1.0.0"}
@app.get("/api/doctor")
def doctor(): return run_doctor()
@app.get("/api/hardware")
def hardware(): return hardware_profile()
@app.get("/api/image-providers")
def image_providers():
 return [{k:v for k,v in p.items() if k != "api_key"} for p in list_providers()]
@app.post("/api/image-providers")
def save_image_provider(payload:dict):
 if not payload.get("base_url"): raise HTTPException(400,"base_url é obrigatório")
 return {k:v for k,v in upsert_provider(payload).items() if k != "api_key"}
@app.post("/api/image-providers/generate")
async def generate_image_api_endpoint(payload:dict):
 provider_id=str(payload.get("provider_id","")).strip(); prompt=str(payload.get("prompt","")).strip()
 provider=next((p for p in list_providers() if p.get("id")==provider_id),None)
 if not provider or not prompt: raise HTTPException(400,"provider_id e prompt são obrigatórios")
 try:return await generate_image_api(provider,prompt)
 except Exception as e:raise HTTPException(502,str(e))
@app.get("/api/ai")
def ai_status(): return registry.status()

@app.get("/api/ai/providers")
def ai_providers(): return list_ai_providers()

@app.post("/api/ai/providers")
def save_ai_provider(payload:dict):
    if not payload.get("name") or not payload.get("base_url"):
        raise HTTPException(400,"name e base_url são obrigatórios")
    try:
        return upsert_ai_provider(payload)
    except Exception as e:
        raise HTTPException(400,str(e))

@app.delete("/api/ai/providers/{provider_id}")
def delete_ai_provider(provider_id:str):
    if not remove_ai_provider(provider_id):
        raise HTTPException(404,"Provedor não encontrado")
    return {"ok":True}

@app.post("/api/ai/providers/test")
def test_ai_provider(payload:dict):
    provider_id=str(payload.get("provider_id","")).strip()
    cfg=__import__("kdp_factory.ai.user_providers",fromlist=["get_provider"]).get_provider(provider_id)
    if not cfg: raise HTTPException(404,"Provedor não encontrado")
    kind=cfg.get("kind","text")
    try:
        if kind in ("video",):
            return {"ok":True,"kind":"video","message":"Configuração válida. O teste completo será feito na primeira geração."}
        if kind in ("image",):
            return {"ok":True,"kind":"image","message":"Configuração válida. O teste completo será feito na primeira geração."}
        result=registry.router.text("Responda somente: OK", model=cfg.get("model"))
        return {"ok":True,"kind":"text","model":result.model,"message":"API respondeu corretamente."}
    except Exception as e:
        raise HTTPException(502,str(e))

@app.get("/api/video-providers")
def video_providers():
    return [p for p in list_ai_providers() if p.get("kind") in ("video","all")]

@app.post("/api/projects/{project_id}/video")
def generate_project_video(project_id:str,payload:dict):
    project=get_project(project_id)
    if not project: raise HTTPException(404,"Projeto não encontrado")
    provider_id=str(payload.get("provider_id","")).strip()
    prompt=str(payload.get("prompt","")).strip()
    if not prompt:
        spec=project.get("spec") or {}
        prompt=f"Crie um vídeo vertical de divulgação para o livro '{project.get('name','')}'. Tema: {spec.get('subject','')}. Idioma: {project.get('language','pt-BR')}. Mostre atmosfera, personagens/elementos visuais e chamada para conhecer o livro, sem inventar informações que não estejam no projeto."
    try:
        from .ai.user_providers import get_provider, UserVideoAPIProvider
        cfg=get_provider(provider_id) if provider_id else None
        if not cfg or cfg.get("kind") not in ("video","all"):
            raise HTTPException(400,"Selecione uma API de vídeo cadastrada.")
        result=UserVideoAPIProvider(cfg).generate(prompt, duration=payload.get("duration"), aspect_ratio=payload.get("aspect_ratio","9:16"), resolution=payload.get("resolution"))
        out=project_dir(project_id)/"exports"/"social_video_result.json"
        out.write_text(__import__("json").dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
        checkpoint(project_id,"social_video",{"provider":cfg.get("name"),"prompt":prompt,"result_file":str(out)})
        return {"ok":True,"provider":cfg.get("name"),"result":result,"saved":str(out)}
    except HTTPException: raise
    except Exception as e: raise HTTPException(502,str(e))

@app.post("/v1/chat/completions")
def openai_compatible_chat(payload:dict):
    messages=payload.get("messages") or []
    if not messages:
        raise HTTPException(400,"messages é obrigatório")
    prompt="\n\n".join(str(m.get("content","")) for m in messages if m.get("role")!="system")
    system="\n".join(str(m.get("content","")) for m in messages if m.get("role")=="system")
    full=(system+"\n\n"+prompt).strip()
    try:
        result=registry.router.text(full, model=payload.get("model"), temperature=payload.get("temperature"), max_tokens=payload.get("max_tokens"))
        return {"id":"kdp-local-chat","object":"chat.completion","model":result.model,"choices":[{"index":0,"message":{"role":"assistant","content":result.text},"finish_reason":"stop"}]}
    except Exception as e:
        raise HTTPException(503,str(e))
@app.get("/api/engine")
def engine_config():
 data=load_remote_config()
 return {"url":data.get("url",""),"configured":bool(data.get("url")),"token_configured":bool(data.get("token"))}
@app.post("/api/engine")
def configure_engine(payload:dict):
 url=str(payload.get("url","")).strip()
 token=str(payload.get("token","")).strip()
 save_remote_config(url,token)
 registry.configure_remote(url,token)
 return {"url":url,"configured":bool(url),"token_configured":bool(token),"status":registry.status()}
@app.get("/api/models")
def models():
 m=ModelManager();return {"hardware":m.hardware(),"ollama":m.ollama_models(),"recommended":m.recommendations()}
@app.get("/api/projects")
def projects(): return list_projects()
@app.get("/api/projects/{project_id}")
def project(project_id:str):
 p=get_project(project_id)
 if not p: raise HTTPException(404,"Projeto não encontrado")
 return p
@app.get("/api/license")
def license(): return license_status()
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
 try:return create_project(payload.name,payload.book_type,payload.language,subject=payload.subject,edition=payload.edition)
 except PermissionError as e:raise HTTPException(402,str(e))
@app.patch("/api/projects/{project_id}")
def patch_project(project_id:str,payload:dict):
 p=update_project(project_id,**payload)
 if not p:raise HTTPException(404,"Projeto não encontrado")
 return p
@app.get("/api/projects/{project_id}/tasks")
def tasks(project_id:str): return list_tasks(project_id)
@app.post("/api/projects/{project_id}/tasks")
def add_task(project_id:str,payload:dict):
 if not get_project(project_id):raise HTTPException(404,"Projeto não encontrado")
 return {"id":create_task(project_id,payload.get("name","Tarefa"))}
@app.post("/api/ai/generate")
def generate(req:TextRequest):
 try:
  result=registry.router.text(req.prompt,req.model);return {"text":result.text,"model":result.model,"raw":result.raw}
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
@app.post("/api/projects/{project_id}/import")
def project_import(project_id:str,req:ImportRequest):
 p=get_project(project_id)
 if not p:raise HTTPException(404,"Projeto não encontrado")
 data=import_file(req.path);src=Path(req.path);dest=project_dir(project_id)/"imports"/src.name;dest.write_bytes(src.read_bytes())
 (project_dir(project_id)/"imports"/(src.stem+".txt")).write_text(normalize_to_text(data),encoding="utf-8")
 return {"ok":True,"filename":src.name,"type":data.get("type")}
class OutlineRequest(BaseModel): brief:str=Field(min_length=1);chapters:int=10;model:str|None=None
@app.post("/api/projects/{project_id}/outline")
def create_outline(project_id:str,req:OutlineRequest):
 try:return generate_outline(project_id,req.brief,req.chapters,req.model)
 except Exception as e:raise HTTPException(400,str(e))
@app.post("/api/projects/{project_id}/manuscript")
def create_manuscript(project_id:str,payload:dict):
 try:return generate_manuscript(project_id,payload["outline"],payload.get("model"))
 except Exception as e:raise HTTPException(400,str(e))
@app.post("/api/projects/{project_id}/metadata")
def create_metadata(project_id:str,payload:dict):
 try:return metadata(project_id,payload.get("description",""),payload.get("audience",""))
 except Exception as e:raise HTTPException(400,str(e))

@app.post("/api/projects/{project_id}/export")
def export_book(project_id:str,payload:dict):
 try:
  fmt=str(payload.get("format","pdf")).lower()
  return {"file":str(export_project(project_id,fmt,payload.get("author",""))),"format":fmt}
 except Exception as e: raise HTTPException(400,str(e))

@app.post("/api/projects/{project_id}/cover")
def create_cover_file(project_id:str,payload:dict):
 try:
  return generate_cover(project_id,payload.get("author",""),payload.get("description",""),payload.get("pages"),payload.get("front_image"),payload.get("back_image"))
 except Exception as e: raise HTTPException(400,str(e))


# The packaged desktop build serves the dashboard locally when its static bundle exists.
_static_dir = Path(__file__).resolve().parent / "static"
if _static_dir.exists():
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="dashboard")
