from __future__ import annotations
import io
import json
import re
from pathlib import Path
from typing import Iterable
import fitz
from PIL import Image, ImageOps

MAX_FILES = 100
MAX_FILE_MB = 50
ALLOWED = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}

PAPER_SIZES_MM = {
    "A4": (210.0, 297.0),
    "A5": (148.0, 210.0),
    "LETTER": (215.9, 279.4),
    "LEGAL": (215.9, 355.6),
    "OFICIO": (216.0, 330.0),
}

def _safe_name(name: str) -> str:
    stem = re.sub(r"[^\w\-. ]+", "_", Path(name).stem, flags=re.UNICODE).strip() or "arquivo"
    return stem[:100]

def _mm_to_pt(mm: float) -> float:
    return float(mm) * 72.0 / 25.4

def _paper_mm(size: str, orientation: str) -> tuple[float, float]:
    key = str(size or "A4").upper()
    if key == "CUSTOM":
        w, h = 210.0, 297.0
    else:
        w, h = PAPER_SIZES_MM.get(key, PAPER_SIZES_MM["A4"])
    if str(orientation).lower() == "landscape":
        w, h = h, w
    return w, h

def _rect_fit(src_w: float, src_h: float, dst: fitz.Rect, mode: str = "contain") -> fitz.Rect:
    if src_w <= 0 or src_h <= 0:
        return dst
    scale = max(dst.width / src_w, dst.height / src_h) if mode == "cover" else min(dst.width / src_w, dst.height / src_h)
    w, h = src_w * scale, src_h * scale
    return fitz.Rect(dst.x0 + (dst.width-w)/2, dst.y0 + (dst.height-h)/2,
                     dst.x0 + (dst.width+w)/2, dst.y0 + (dst.height+h)/2)

def _image_bytes(path: Path, grayscale: bool) -> tuple[bytes, int, int]:
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("L" if grayscale else "RGB")
        out = io.BytesIO()
        im.save(out, format="JPEG", quality=95, dpi=(300, 300))
        return out.getvalue(), im.width, im.height

def _append_pdf(src: fitz.Document, out: fitz.Document, page_no: int, target: fitz.Rect, mode: str) -> None:
    page = src[page_no]
    rect = _rect_fit(page.rect.width, page.rect.height, target, mode)
    out_page = out.new_page(width=target.width + target.x0, height=target.height + target.y0)
    out_page.show_pdf_page(rect, src, page_no, keep_proportion=True, overlay=True)

def build_print_pdf(project_id: str, files: list[dict], options: dict) -> Path:
    root = Path(__import__("kdp_factory.projects", fromlist=["project_dir"]).project_dir(project_id))
    out_dir = root / "exports" / "print_ready"
    out_dir.mkdir(parents=True, exist_ok=True)
    size = str(options.get("paper_size", "A4")).upper()
    orientation = str(options.get("orientation", "portrait")).lower()
    mode = str(options.get("fit", "contain")).lower()
    grayscale = bool(options.get("grayscale", False))
    try:
        margin = max(0.0, float(options.get("margin_mm", 0)))
    except Exception:
        margin = 0.0
    if size == "CUSTOM":
        try:
            w_mm = float(options.get("custom_width_mm", 210))
            h_mm = float(options.get("custom_height_mm", 297))
        except Exception:
            w_mm, h_mm = 210.0, 297.0
        if orientation == "landscape":
            w_mm, h_mm = h_mm, w_mm
    else:
        w_mm, h_mm = _paper_mm(size, orientation)
    page_w, page_h = _mm_to_pt(w_mm), _mm_to_pt(h_mm)
    margin_pt = _mm_to_pt(margin)
    target = fitz.Rect(margin_pt, margin_pt, max(margin_pt, page_w-margin_pt), max(margin_pt, page_h-margin_pt))
    out = fitz.open()
    try:
        for item in files:
            rel = str(item.get("path", "")).replace("\\", "/")
            path = root / rel
            if not path.exists():
                continue
            ext = path.suffix.lower()
            if ext == ".pdf":
                src = fitz.open(path)
                try:
                    for n in range(src.page_count):
                        _append_pdf(src, out, n, target, mode)
                finally:
                    src.close()
            elif ext in {".jpg", ".jpeg", ".png", ".webp"}:
                data, iw, ih = _image_bytes(path, grayscale)
                page = out.new_page(width=page_w, height=page_h)
                rect = _rect_fit(iw, ih, target, mode)
                page.insert_image(rect, stream=data, keep_proportion=True, overlay=True)
            else:
                continue
        if out.page_count == 0:
            raise ValueError("Nenhuma página válida foi encontrada nos arquivos.")
        slug = _safe_name(str(options.get("name") or "arquivo_para_impressao"))
        dest = out_dir / f"{slug}.pdf"
        out.save(dest, garbage=4, deflate=True)
    finally:
        out.close()
    return dest

def manifest(project_id: str) -> dict:
    root = Path(__import__("kdp_factory.projects", fromlist=["project_dir"]).project_dir(project_id))
    d = root / "imports" / "print"
    d.mkdir(parents=True, exist_ok=True)
    mf = d / "manifest.json"
    if not mf.exists():
        return {"files": []}
    try:
        return json.loads(mf.read_text(encoding="utf-8"))
    except Exception:
        return {"files": []}

def save_manifest(project_id: str, data: dict) -> None:
    root = Path(__import__("kdp_factory.projects", fromlist=["project_dir"]).project_dir(project_id))
    d = root / "imports" / "print"
    d.mkdir(parents=True, exist_ok=True)
    (d / "manifest.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def add_files(project_id: str, uploads: Iterable, filenames: list[str]) -> dict:
    data = manifest(project_id)
    items = data.get("files", [])
    if len(items) + len(filenames) > MAX_FILES:
        raise ValueError(f"O limite é de {MAX_FILES} arquivos por projeto.")
    root = Path(__import__("kdp_factory.projects", fromlist=["project_dir"]).project_dir(project_id))
    dest_dir = root / "imports" / "print"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for upload, original in zip(uploads, filenames):
        ext = Path(original).suffix.lower()
        if ext not in ALLOWED:
            raise ValueError(f"Formato não suportado: {original}. Use PDF, JPG, PNG ou WEBP.")
        content = upload if isinstance(upload, bytes) else upload.read()
        if len(content) > MAX_FILE_MB * 1024 * 1024:
            raise ValueError(f"{original} excede o limite de {MAX_FILE_MB} MB.")
        safe = _safe_name(original)
        target = dest_dir / f"{len(items)+1:03d}_{safe}{ext}"
        target.write_bytes(content)
        items.append({"id": target.stem, "name": original, "path": str(target.relative_to(root)), "order": len(items)})
    data["files"] = items
    save_manifest(project_id, data)
    return data

def remove_file(project_id: str, file_id: str) -> dict:
    data = manifest(project_id)
    items = data.get("files", [])
    item = next((x for x in items if x.get("id") == file_id), None)
    if not item:
        raise ValueError("Arquivo não encontrado.")
    root = Path(__import__("kdp_factory.projects", fromlist=["project_dir"]).project_dir(project_id))
    path = root / str(item.get("path", ""))
    if path.exists(): path.unlink()
    data["files"] = [x for x in items if x.get("id") != file_id]
    for n, x in enumerate(data["files"]): x["order"] = n
    save_manifest(project_id, data)
    return data

def reorder(project_id: str, ids: list[str]) -> dict:
    data = manifest(project_id)
    by_id = {x["id"]: x for x in data.get("files", [])}
    ordered = [by_id[i] for i in ids if i in by_id]
    ordered += [x for x in data.get("files", []) if x["id"] not in ids]
    for n, item in enumerate(ordered):
        item["order"] = n
    data["files"] = ordered
    save_manifest(project_id, data)
    return data
