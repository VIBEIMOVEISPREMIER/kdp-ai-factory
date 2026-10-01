from __future__ import annotations
from pathlib import Path
import json
from .projects import get_project, project_dir, checkpoint, update_project
from .editorial.engine import EditorialEngine
from .export.engine import ExportEngine
from .metadata.engine import MetadataEngine
from .cover import create_cover

def _chapters(project_id):
    p=project_dir(project_id)/"manuscript.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def save_manuscript(project_id,title,chapters,language="pt-BR"):
    data={"title":title,"language":language,"chapters":chapters}
    p=project_dir(project_id)/"manuscript.json"; p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    checkpoint(project_id,"manuscript",{"file":str(p),"chapters":len(chapters)}); update_project(project_id,status="manuscript",progress=35); return data

def generate_outline(project_id,brief,chapters=10,model=None):
    p=get_project(project_id)
    if not p: raise ValueError("Projeto não encontrado")
    result=EditorialEngine().outline(brief,chapters,model); out=project_dir(project_id)/"outline.json"; out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    checkpoint(project_id,"outline",result); update_project(project_id,status="outline",progress=20); return result

def generate_manuscript(project_id,outline,model=None):
    title=outline.get("title") or get_project(project_id)["name"]; chapters=[]
    for i,ch in enumerate(outline.get("chapters",[]),1):
        chapters.append({"title":ch.get("title",f"Capítulo {i}"),"content":EditorialEngine().write_chapter(ch.get("title",f"Capítulo {i}"),ch.get("purpose",""),model=model)})
    return save_manuscript(project_id,title,chapters,get_project(project_id)["language"])

def export_project(project_id,fmt="pdf",author=""):
    p=get_project(project_id); chapters=_chapters(project_id)
    if not p or not chapters: raise ValueError("Projeto sem manuscrito.")
    out=project_dir(project_id)/"exports"/f"{p['name'].replace(' ','_')}.{fmt}"; e=ExportEngine()
    if fmt=="pdf": e.pdf(chapters,out,p["name"],author,p["spec"]["trim_size"],p["spec"]["bleed"])
    elif fmt=="docx": e.docx(chapters,out,p["name"],author)
    elif fmt=="epub": e.epub(chapters,out,p["name"],p["language"])
    else: raise ValueError("Formato inválido")
    update_project(project_id,status="exported",progress=100); checkpoint(project_id,"export",{"file":str(out)}); return out

def metadata(project_id,description="",audience="",**extra):
    p=get_project(project_id); data=MetadataEngine().generate(p["name"],description,p["language"],audience,**extra)
    out=project_dir(project_id)/"metadata.json"; MetadataEngine().save(data,out); return data

def generate_cover(project_id,author="",description="",pages=None,front_image=None,back_image=None):
    p=get_project(project_id)
    if not p: raise ValueError("Projeto não encontrado")
    pages=int(p["spec"].get("target_pages") or pages or 100)
    result=create_cover(project_dir(project_id),p["name"],author,description,p["spec"]["trim_size"],pages,back_image,front_image)
    update_project(project_id,status="cover",progress=max(80,int(p.get("progress",0)))); checkpoint(project_id,"cover",result); return result
