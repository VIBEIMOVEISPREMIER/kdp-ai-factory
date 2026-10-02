from fastapi import FastAPI,HTTPException,UploadFile,File,Form
from fastapi.responses import FileResponse
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
from .bookflow import generate_outline,generate_manuscript,metadata,export_project,generate_cover,run_stage
from .licensing.client import status as license_status,activate_with_license,create_payment_intent,verify_payment_and_issue_license
from .licensing.models import LicenseActivationRequest
from .hardware import as_dict as hardware_profile
from .ai.image_providers import list_providers, upsert_provider, generate as generate_image_api
from .ai.remote_config import load as load_remote_config, save as save_remote_config
from .ai.user_providers import list_providers as list_ai_providers, upsert_provider as upsert_ai_provider, remove_provider as remove_ai_provider
from .web_persistence import restore_projects, persist_project, persistence_status
from .config import LICENSE_SERVER_URL
from .photo_manager import upload_photos, get_photo_manifest, update_photo_roles
from .print_manager import add_files as add_print_files, manifest as print_manifest, reorder as reorder_print_files, remove_file as remove_print_file, set_role as set_print_role, build_print_pdf
from .print_resize import prepare_uploads as prepare_print_uploads, output_path as print_output_path
app=FastAPI(title="KDP AI Factory",version="1.0.0")
class ProjectCreate(BaseModel): name:str=Field(min_length=1,max_length=200);book_type:str="custom";language:str="pt-BR";subject:str="";edition:str="print";author:str="";content_mode:str="text_and_images";resolution:str="kdp_300dpi";publication_format:str="paperback";print_mode:str="kdp";cover_mode:str="images_only";ai_brief:str="";ai_script:str="";trim_size:str="6x9";print_settings:dict={}
class TextRequest(BaseModel): prompt:str=Field(min_length=1);model:str|None=None
class ImportRequest(BaseModel): path:str
class ValidateRequest(BaseModel): spec:dict;pdf_path:str|None=None
class CheckpointRequest(BaseModel): stage:str;state:dict={}
class PaymentIntentRequest(BaseModel): asset:str=Field(pattern=r"^(USDT|BNB)$")
class PaymentRequest(BaseModel): tx_id:str=Field(min_length=20,max_length=200);asset:str=Field(pattern=r"^(USDT|BNB)$");referral_code:str="";intent_id:str="";intent_secret:str=""
class PrintBuildRequest(BaseModel): paper_size:str="A4";orientation:str="portrait";fit:str="contain";margin_mm:float=0;grayscale:bool=False;name:str="arquivo_para_impressao";custom_width_mm:float=210;custom_height_mm:float=297;output_format:str="pdf"
@app.on_event("startup")
def startup():
    # Never block the HTTP server from binding its port because Neon is
    # unavailable or slow. Persistence is reported as degraded instead.
    restored = 0
    try:
        init_db()
        restored = restore_projects()
        status = persistence_status()
        app.state.web_persistence = status
        print(f"Web persistence: {status}; restored_projects={restored}")
    except Exception as exc:
        status = {
            "enabled": bool(__import__("os").getenv("DATABASE_URL", "").strip()),
            "backend": "neon-postgres",
            "status": "degraded",
            "error": str(exc)[:500],
            "project_archives": 0,
        }
        app.state.web_persistence = status
        print(f"Web persistence degraded: {exc!r}")
@app.get("/api/health")
def health(): return {"ok":True,"service":"kdp-ai-factory","version":"1.0.0","persistence":getattr(app.state,"web_persistence",{"enabled":False,"backend":"local"})}
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
        from .ai.user_providers import OpenAICompatibleTextProvider
        result=OpenAICompatibleTextProvider(cfg).generate("Responda somente: OK", model=cfg.get("model"), timeout=30)
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

@app.get("/api/affiliate/config")
def affiliate_config():
    return {"url": LICENSE_SERVER_URL + "/affiliate", "api_base": LICENSE_SERVER_URL}
@app.post("/api/license/activate")
def activate_license(payload:LicenseActivationRequest):
 try:return activate_with_license(payload.license_token)
 except Exception as e:raise HTTPException(400,str(e))
@app.post("/api/license/payment-intent")
def payment_intent(payload:PaymentIntentRequest):
 try:return create_payment_intent(payload.asset)
 except Exception as e:raise HTTPException(400,str(e))
@app.post("/api/license/payment")
def payment_license(payload:PaymentRequest):
 try:return verify_payment_and_issue_license(payload.tx_id,payload.asset,referral_code=payload.referral_code.strip(),intent_id=payload.intent_id,intent_secret=payload.intent_secret)
 except Exception as e:raise HTTPException(400,str(e))
@app.post("/api/projects")
def new_project(payload:ProjectCreate):
 try:return create_project(payload.name,payload.book_type,payload.language,subject=payload.subject,edition=payload.edition,author=payload.author,content_mode=payload.content_mode,resolution=payload.resolution,publication_format=payload.publication_format,print_mode=payload.print_mode,ai_brief=payload.ai_brief,ai_script=payload.ai_script,trim_size=payload.trim_size,print_settings=payload.print_settings)
 except PermissionError as e:raise HTTPException(402,str(e))
@app.patch("/api/projects/{project_id}")
def patch_project(project_id:str,payload:dict):
 p=update_project(project_id,**payload)
 if not p:raise HTTPException(404,"Projeto não encontrado")
 return p
@app.get("/api/projects/{project_id}/photos")
def project_photos(project_id:str):
    if not get_project(project_id): raise HTTPException(404,"Projeto não encontrado")
    return get_photo_manifest(project_id)

@app.get("/api/projects/{project_id}/photos/{photo_id}")
def project_photo_file(project_id:str,photo_id:str):
    manifest=get_photo_manifest(project_id)
    item=next((x for x in manifest.get("photos",[]) if x.get("id")==photo_id),None)
    if not item: raise HTTPException(404,"Foto não encontrada")
    path=project_dir(project_id)/item["prepared"]
    if not path.exists(): raise HTTPException(404,"Arquivo da foto não encontrado")
    return FileResponse(path,media_type="image/jpeg")

@app.post("/api/projects/{project_id}/photos")
async def upload_project_photos(project_id:str, files:list[UploadFile]=File(...)):
    if not get_project(project_id): raise HTTPException(404,"Projeto não encontrado")
    try:
        result=await upload_photos(project_id, files)
        persist_project(project_id)
        return result
    except ValueError as e: raise HTTPException(400,str(e))
    except Exception as e: raise HTTPException(500,str(e))

@app.patch("/api/projects/{project_id}/photos")
def set_project_photo_roles(project_id:str,payload:dict):
    if not get_project(project_id): raise HTTPException(404,"Projeto não encontrado")
    try:
        result=update_photo_roles(project_id,payload)
        persist_project(project_id)
        return result
    except ValueError as e: raise HTTPException(400,str(e))

@app.get("/api/projects/{project_id}/print-files")
def project_print_files(project_id:str):
    if not get_project(project_id): raise HTTPException(404,"Projeto não encontrado")
    return print_manifest(project_id)

@app.post("/api/projects/{project_id}/print-files")
async def upload_print_files(project_id:str, files:list[UploadFile]=File(...)):
    if not get_project(project_id): raise HTTPException(404,"Projeto não encontrado")
    try:
        names=[f.filename or "arquivo" for f in files]
        payload=[await f.read() for f in files]
        result=add_print_files(project_id, payload, names)
        persist_project(project_id)
        return result
    except ValueError as e: raise HTTPException(400,str(e))
    except Exception as e: raise HTTPException(500,str(e))

@app.delete("/api/projects/{project_id}/print-files/{file_id}")
def delete_project_print_file(project_id:str,file_id:str):
    if not get_project(project_id): raise HTTPException(404,"Projeto não encontrado")
    try:
        result=remove_print_file(project_id,file_id)
        persist_project(project_id)
        return result
    except ValueError as e: raise HTTPException(404,str(e))

@app.patch("/api/projects/{project_id}/print-files/role")
def set_project_print_role(project_id:str,payload:dict):
    if not get_project(project_id): raise HTTPException(404,"Projeto não encontrado")
    try:
        result=set_print_role(project_id,str(payload.get("id","")),str(payload.get("role","interior")))
        persist_project(project_id)
        return result
    except ValueError as e: raise HTTPException(400,str(e))

@app.patch("/api/projects/{project_id}/print-files/order")
def reorder_project_print_files(project_id:str,payload:dict):
    if not get_project(project_id): raise HTTPException(404,"Projeto não encontrado")
    try:
        result=reorder_print_files(project_id,[str(x) for x in payload.get("ids",[])])
        persist_project(project_id)
        return result
    except Exception as e: raise HTTPException(400,str(e))

@app.post("/api/projects/{project_id}/print-files/build")
def build_project_print_file(project_id:str,req:PrintBuildRequest):
    if not get_project(project_id): raise HTTPException(404,"Projeto não encontrado")
    try:
        mf=print_manifest(project_id)
        result=build_print_pdf(project_id,mf.get("files",[]),req.model_dump())
        persist_project(project_id)
        return {"ok":True,"file":str(result),"filename":result.name}
    except Exception as e: raise HTTPException(400,str(e))

@app.get("/api/projects/{project_id}/print-files/download/{filename}")
def download_project_print_file(project_id:str,filename:str):
    if not get_project(project_id): raise HTTPException(404,"Projeto não encontrado")
    path=project_dir(project_id)/"exports"/"print_ready"/Path(filename).name
    if not path.exists(): raise HTTPException(404,"Arquivo não encontrado")
    media_type="application/pdf" if path.suffix.lower()==".pdf" else "application/zip"
    return FileResponse(path,media_type=media_type,filename=path.name)

@app.post("/api/print/resize")
async def resize_print_files(files:list[UploadFile]=File(...), roles:str=Form(...), options:str=Form(...)):
    try:
        role_list=__import__("json").loads(roles)
        cfg=__import__("json").loads(options)
        if not isinstance(role_list,list) or len(role_list)!=len(files):
            raise ValueError("Informe a função de cada arquivo: Interior ou Capa.")
        payload=[]
        for upload,role in zip(files,role_list):
            payload.append((upload.filename or "arquivo",await upload.read(),str(role).lower()))
        return prepare_print_uploads(payload,cfg)
    except ValueError as e: raise HTTPException(400,str(e))
    except Exception as e: raise HTTPException(500,str(e))

@app.get("/api/print/download/{token}/{filename}")
def download_print_output(token:str,filename:str):
    try: path=print_output_path(token,filename)
    except FileNotFoundError: raise HTTPException(404,"Arquivo temporário não encontrado.")
    return FileResponse(path,media_type="application/pdf",filename=path.name)

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
 persist_project(project_id)
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
@app.post("/api/projects/{project_id}/stage/{stage}")
def run_editorial_stage(project_id:str,stage:str,payload:dict|None=None):
 try:
  payload=payload or {}
  project=get_project(project_id)
  if not project: raise HTTPException(404,"Projeto não encontrado")
  current=int(project.get("progress",0) or 0)
  required={"brief":0,"outline":10,"manuscript":20,"revision":35,"assets":45,"layout":55,"cover":65,"validation":80,"export":90}
  key=str(stage).strip().lower()
  if key not in required: raise HTTPException(400,"Etapa inválida.")
  if current < required[key]:
   raise HTTPException(409,f"Conclua a etapa anterior antes de executar '{key}'.")
  result=run_stage(project_id,key,payload.get("model"),payload.get("author",""))
  persist_project(project_id)
  return result
 except HTTPException: raise
 except Exception as e:
  raise HTTPException(400,str(e))

@app.post("/api/projects/{project_id}/metadata")
def create_metadata(project_id:str,payload:dict):
 try:
  result=metadata(project_id,payload.get("description",""),payload.get("audience",""))
  persist_project(project_id)
  return result
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