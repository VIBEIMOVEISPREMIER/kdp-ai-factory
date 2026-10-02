from __future__ import annotations
import io, json, shutil, tempfile, uuid
from pathlib import Path
import fitz
from PIL import Image, ImageOps

MM_PER_INCH = 25.4
BLEED_MM = 3.175

TRIM_MM = {
    "5x8": (127.0,203.2), "5.06x7.81": (128.5,198.4), "5.25x8": (133.35,203.2),
    "5.5x8.5": (139.7,215.9), "6x9": (152.4,228.6), "6.14x9.21": (156.0,233.93),
    "6.69x9.61": (169.93,244.09), "7x10": (177.8,254.0), "7.44x9.69": (189.0,246.13),
    "7.5x9.25": (190.5,234.95), "8x10": (203.2,254.0), "8.25x6": (209.55,152.4),
    "8.25x8.25": (209.55,209.55), "8.5x8.5": (215.9,215.9),
    "8.27x11.69": (210.0,296.93), "8.5x11": (215.9,279.4),
}

def mm_pt(mm: float) -> float:
    return mm * 72.0 / MM_PER_INCH

def _dims(options: dict, role: str) -> tuple[float,float]:
    mode = str(options.get("mode","kdp"))
    if mode == "independent":
        key = "cover" if role == "cover" else "interior"
        w = float(options.get(f"{key}_width_mm", 210))
        h = float(options.get(f"{key}_height_mm", 297))
        if str(options.get(f"{key}_orientation","portrait")) == "landscape": w,h=h,w
        return w,h
    trim = str(options.get("trim_size","6x9"))
    tw,th = TRIM_MM.get(trim,TRIM_MM["6x9"])
    if str(options.get("orientation","portrait")) == "landscape": tw,th=th,tw
    if role == "interior":
        bleed = bool(options.get("bleed",False))
        return tw + (BLEED_MM if bleed else 0), th + (BLEED_MM*2 if bleed else 0)
    pages = max(24,int(options.get("page_count",24)))
    paper = str(options.get("paper","white"))
    ink = str(options.get("ink","black"))
    if ink == "premium_color":
        spine = pages * 0.0596
    elif ink == "standard_color":
        spine = pages * 0.0572
    elif paper == "cream":
        spine = pages * 0.0635
    else:
        spine = pages * 0.0572
    return tw*2 + spine + BLEED_MM*2, th + BLEED_MM*2

def _canvas(w_mm: float,h_mm: float):
    w,h=round(mm_pt(w_mm)/72*300),round(mm_pt(h_mm)/72*300)
    return max(1,w),max(1,h)

def _place_image(im: Image.Image,w_mm:float,h_mm:float,fit:str,gray:bool) -> Image.Image:
    if gray: im=ImageOps.exif_transpose(im).convert("L")
    else: im=ImageOps.exif_transpose(im).convert("RGB")
    cw,ch=_canvas(w_mm,h_mm)
    scale=max(cw/im.width,ch/im.height) if fit=="cover" else min(cw/im.width,ch/im.height)
    nw,nh=max(1,round(im.width*scale)),max(1,round(im.height*scale))
    im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    bg=0 if gray else (255,255,255)
    canvas=Image.new(im.mode,(cw,ch),bg)
    canvas.paste(im,((cw-nw)//2,(ch-nh)//2))
    return canvas

def _source_pages(path:Path):
    if path.suffix.lower()==".pdf":
        doc=fitz.open(path)
        try:
            for i in range(doc.page_count):
                pix=doc[i].get_pixmap(dpi=300,alpha=False)
                yield Image.open(io.BytesIO(pix.tobytes("png"))).copy()
        finally: doc.close()
    elif path.suffix.lower() in {".jpg",".jpeg",".png",".webp"}:
        yield Image.open(path).copy()
    else:
        raise ValueError(f"Formato não suportado: {path.name}")

def _write_pdf(paths:list[Path],out:Path,w_mm:float,h_mm:float,fit:str,gray:bool):
    pages=[]
    for path in paths:
        for im in _source_pages(path):
            pages.append(_place_image(im,w_mm,h_mm,fit,gray))
    if not pages: raise ValueError("Nenhum arquivo válido foi enviado.")
    pages[0].save(out,"PDF",resolution=300.0,save_all=True,append_images=pages[1:])
    return out

def prepare_uploads(files:list[tuple[str,bytes,str]],options:dict) -> dict:
    token=uuid.uuid4().hex
    root=Path(tempfile.gettempdir())/"kdp-ai-factory-print"/token
    root.mkdir(parents=True,exist_ok=True)
    paths={"interior":[],"cover":[]}
    try:
        for i,(name,data,role) in enumerate(files):
            role=str(role or "").lower()
            if role not in paths: raise ValueError("Cada arquivo deve ser marcado como Interior ou Capa.")
            ext=Path(name).suffix.lower()
            if ext not in {".pdf",".jpg",".jpeg",".png",".webp"}: raise ValueError(f"Formato não suportado: {name}")
            p=root/f"{i:03d}_{Path(name).name}"
            p.write_bytes(data); paths[role].append(p)
        if not paths["interior"] and not paths["cover"]: raise ValueError("Envie pelo menos um arquivo.")
        if len(paths["cover"])>1: raise ValueError("Envie apenas um arquivo marcado como Capa.")
        outputs=[]
        fit=str(options.get("fit","contain"))
        gray=bool(options.get("grayscale",False))
        for role in ("interior","cover"):
            if not paths[role]: continue
            w,h=_dims(options,role)
            out=root/("INTERIOR_KDP.pdf" if role=="interior" and options.get("mode")=="kdp" else "INTERIOR_GRAFICA.pdf" if role=="interior" else "CAPA_KDP.pdf" if options.get("mode")=="kdp" else "CAPA_GRAFICA.pdf")
            _write_pdf(paths[role],out,w,h,fit,gray)
            outputs.append({"role":role,"filename":out.name,"width_mm":round(w,3),"height_mm":round(h,3),"url":f"/api/print/download/{token}/{out.name}"})
        return {"ok":True,"token":token,"outputs":outputs}
    except Exception:
        shutil.rmtree(root,ignore_errors=True)
        raise

def output_path(token:str,filename:str) -> Path:
    root=Path(tempfile.gettempdir())/"kdp-ai-factory-print"/Path(token).name
    path=root/Path(filename).name
    if not root.exists() or not path.exists(): raise FileNotFoundError(filename)
    return path

def cleanup(token:str):
    shutil.rmtree(Path(tempfile.gettempdir())/"kdp-ai-factory-print"/Path(token).name,ignore_errors=True)
