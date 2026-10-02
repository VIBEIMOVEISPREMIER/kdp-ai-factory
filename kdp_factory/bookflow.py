from __future__ import annotations
from pathlib import Path
import json
import re
from .projects import get_project, project_dir, checkpoint, update_project
from .editorial.engine import EditorialEngine
from .export.engine import ExportEngine
from .metadata.engine import MetadataEngine
from .cover import create_cover
from .kdp.validator import KDPValidator
from .photo_manager import get_photo_manifest

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
    photo_data=get_photo_manifest(project_id)
    photo_map={x["id"]:x["prepared"] for x in photo_data.get("photos",[])}
    interior_images=[str(project_dir(project_id)/photo_map[x]) for x in photo_data.get("interior",[]) if x in photo_map]
    out=project_dir(project_id)/"exports"/f"{p['name'].replace(' ','_')}.{fmt}"; e=ExportEngine()
    if fmt=="pdf": e.pdf(chapters,out,p["name"],author,p["spec"]["trim_size"],p["spec"]["bleed"],interior_images=interior_images)
    elif fmt=="docx": e.docx(chapters,out,p["name"],author)
    elif fmt=="epub": e.epub(chapters,out,p["name"],p["language"])
    else: raise ValueError("Formato inválido")
    update_project(project_id,status="exported",progress=100); checkpoint(project_id,"export",{"file":str(out)}); return out

def metadata(project_id,description="",audience="",**extra):
    p=get_project(project_id); data=MetadataEngine().generate(p["name"],description,p["language"],audience,book_type=p.get("book_type","custom"),subject=p.get("spec",{}).get("subject",""),**extra)
    out=project_dir(project_id)/"metadata.json"; MetadataEngine().save(data,out); return data

def generate_cover(project_id,author="",description="",pages=None,front_image=None,back_image=None):
    p=get_project(project_id)
    if not p: raise ValueError("Projeto não encontrado")
    pages=int(p["spec"].get("target_pages") or pages or 100)
    photo_data=get_photo_manifest(project_id)
    photo_map={x["id"]:x["prepared"] for x in photo_data.get("photos",[])}
    back_image=back_image or (str(project_dir(project_id)/photo_map[photo_data["back_cover"]]) if photo_data.get("back_cover") in photo_map else None)
    front_image=front_image or (str(project_dir(project_id)/photo_map[photo_data["cover"]]) if photo_data.get("cover") in photo_map else None)
    result=create_cover(project_dir(project_id),p["name"],author,description,p["spec"]["trim_size"],pages,back_image,front_image)
    update_project(project_id,status="cover",progress=max(80,int(p.get("progress",0)))); checkpoint(project_id,"cover",result); return result

def run_stage(project_id, stage, model=None, author=""):
    """Run one of the nine editorial stages and persist its checkpoint."""
    p = get_project(project_id)
    if not p: raise ValueError("Projeto não encontrado.")
    stage = str(stage).strip().lower()
    brief_base = str(p.get("spec", {}).get("subject") or p.get("name") or "").strip()
    spec = p.get("spec", {}) or {}
    ai_brief = str(spec.get("ai_brief") or "").strip()
    ai_script = str(spec.get("ai_script") or "").strip()
    brief = "\n\n".join(x for x in [brief_base, "BRIEFING DO USUÁRIO:\n"+ai_brief if ai_brief else "", "SCRIPT/ESBOÇO DO USUÁRIO:\n"+ai_script if ai_script else ""] if x).strip()
    if stage == "brief":
        state = {"project_id": project_id, "subject": brief, "book_type": p.get("book_type"), "language": p.get("language"), "edition": p.get("edition"), "author": spec.get("author",""), "content_mode": spec.get("content_mode","text_and_images"), "resolution": spec.get("resolution","kdp_300dpi"), "publication_format": spec.get("publication_format","paperback"), "trim_size": spec.get("trim_size","6x9"), "print_mode": spec.get("print_mode","kdp")}
        checkpoint(project_id, "brief", state); update_project(project_id, status="brief", progress=10); return {"stage": stage, "status": "brief", "progress": 10, "state": state}
    if stage == "outline": return generate_outline(project_id, brief, 10, model)
    if stage == "manuscript":
        op = project_dir(project_id) / "outline.json"
        outline = json.loads(op.read_text(encoding="utf-8")) if op.exists() else generate_outline(project_id, brief, 10, model)
        return generate_manuscript(project_id, outline, model)
    if stage == "revision":
        mp = project_dir(project_id) / "manuscript.json"
        if not mp.exists(): raise ValueError("Gere o manuscrito antes da revisão.")
        data = json.loads(mp.read_text(encoding="utf-8"))
        instructions = "Revise ortografia, gramática, clareza, coerência, transições e repetição. Preserve fatos, intenção e estrutura do capítulo. Não invente fontes."
        engine = EditorialEngine(); revised = []
        for ch in data.get("chapters", []):
            revised.append({**ch, "content": engine.revise(str(ch.get("content", "")), instructions, model)})
        data["chapters"] = revised; mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        checkpoint(project_id, "revision", {"file": str(mp), "chapters": len(revised)}); update_project(project_id, status="revision", progress=45)
        return {"stage": stage, "status": "revision", "progress": 45, "chapters": len(revised)}
    if stage == "assets":
        mp = project_dir(project_id) / "manuscript.json"
        if not mp.exists(): raise ValueError("Gere o manuscrito antes dos assets.")
        data = json.loads(mp.read_text(encoding="utf-8")); assets_dir = project_dir(project_id) / "assets"; assets_dir.mkdir(parents=True, exist_ok=True); assets = []
        for i, ch in enumerate(data.get("chapters", []), 1):
            title = str(ch.get("title") or f"Capítulo {i}"); safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", title).strip("_")[:60] or f"chapter_{i}"; svg = assets_dir / f"{i:03d}_{safe}.svg"
            label = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")[:70]
            svg_text = '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><rect width="1600" height="900" fill="#203a5f"/><circle cx="1280" cy="180" r="120" fill="#fff" opacity=".35"/><text x="800" y="430" text-anchor="middle" fill="#fff" font-family="Arial" font-size="54" font-weight="700">' + label + '</text><text x="800" y="500" text-anchor="middle" fill="#d9e6f5" font-family="Arial" font-size="28">KDP AI Factory • asset editorial</text></svg>'
            svg.write_text(svg_text, encoding="utf-8"); assets.append({"chapter": i, "title": title, "file": str(svg.relative_to(project_dir(project_id)))})
        out = project_dir(project_id) / "assets.json"; out.write_text(json.dumps({"assets": assets}, ensure_ascii=False, indent=2), encoding="utf-8")
        checkpoint(project_id, "assets", {"file": str(out), "count": len(assets)}); update_project(project_id, status="assets", progress=55); return {"stage": stage, "status": "assets", "progress": 55, "count": len(assets)}
    if stage == "layout":
        spec = dict(p.get("spec") or {}); layout = {"trim_size": spec.get("trim_size"), "bleed": bool(spec.get("bleed")), "bleed_inches": spec.get("bleed_inches", 0.125), "margins": spec.get("margins", 0.5), "target_pages": spec.get("target_pages"), "language": p.get("language"), "book_type": p.get("book_type")}
        out = project_dir(project_id) / "layout.json"; out.write_text(json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8"); checkpoint(project_id, "layout", layout); update_project(project_id, status="layout", progress=65); return {"stage": stage, "status": "layout", "progress": 65, "layout": layout}
    if stage == "cover": return generate_cover(project_id, author=author)
    if stage == "validation":
        issues = KDPValidator().validate_spec(dict(p.get("spec") or {})); result = {"ok": not any(x.level == "error" for x in issues), "issues": [x.__dict__ for x in issues]}
        out = project_dir(project_id) / "validation.json"; out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"); checkpoint(project_id, "validation", result); update_project(project_id, status="validated" if result["ok"] else "validation_error", progress=90 if result["ok"] else 85); return {"stage": stage, **result, "progress": 90 if result["ok"] else 85}
    if stage == "export": return {"stage": stage, "file": str(export_project(project_id, "pdf", author)), "status": "exported", "progress": 100}
    raise ValueError("Etapa inválida.")
