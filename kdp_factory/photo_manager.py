from __future__ import annotations
from pathlib import Path
import json
import uuid
from PIL import Image, ImageOps
from .projects import project_dir, checkpoint

MAX_PHOTOS = 100
ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024


def _manifest_path(project_id: str) -> Path:
    return project_dir(project_id) / "photos.json"


def get_photo_manifest(project_id: str):
    p = _manifest_path(project_id)
    if not p.exists():
        return {"photos": [], "cover": None, "back_cover": None, "interior": [], "ai_reference": []}
    return json.loads(p.read_text(encoding="utf-8"))


def _save(project_id: str, data: dict):
    p = _manifest_path(project_id)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    checkpoint(project_id, "photos", {"count": len(data["photos"]), "cover": data.get("cover"), "back_cover": data.get("back_cover")})


async def upload_photos(project_id: str, files):
    data = get_photo_manifest(project_id)
    if len(data["photos"]) + len(files) > MAX_PHOTOS:
        raise ValueError(f"O limite é de {MAX_PHOTOS} fotos por projeto.")
    out_dir = project_dir(project_id) / "images" / "personal"
    out_dir.mkdir(parents=True, exist_ok=True)
    added = []
    for upload in files:
        content_type = (upload.content_type or "").lower()
        if content_type not in ALLOWED:
            raise ValueError("Formato não suportado. Use JPG, PNG ou WEBP.")
        raw = await upload.read()
        if len(raw) > MAX_UPLOAD_BYTES:
            raise ValueError("Cada foto pode ter no máximo 25 MB.")
        try:
            from io import BytesIO
            src = Image.open(BytesIO(raw))
            src = ImageOps.exif_transpose(src).convert("RGB")
        except Exception:
            raise ValueError(f"Arquivo de imagem inválido: {upload.filename or 'sem nome'}")
        photo_id = uuid.uuid4().hex
        original = out_dir / f"{photo_id}_original.jpg"
        prepared = out_dir / f"{photo_id}_prepared.jpg"
        src.save(original, format="JPEG", quality=95, dpi=(300, 300))
        # Preserve aspect ratio; no stretching. The prepared copy is a clean 300-DPI RGB master.
        src.save(prepared, format="JPEG", quality=95, dpi=(300, 300))
        item = {"id": photo_id, "name": upload.filename or f"foto_{len(data['photos'])+1}", "original": str(original.relative_to(project_dir(project_id))), "prepared": str(prepared.relative_to(project_dir(project_id))), "width": src.width, "height": src.height, "source": "gallery_or_device", "edited": False}
        data["photos"].append(item)
        added.append(item)
    _save(project_id, data)
    return {"ok": True, "added": added, "count": len(data["photos"]), "limit": MAX_PHOTOS}


def update_photo_roles(project_id: str, payload: dict):
    data = get_photo_manifest(project_id)
    valid = {p["id"] for p in data["photos"]}
    cover = payload.get("cover") or None
    back = payload.get("back_cover") or None
    interior = payload.get("interior") or []
    if cover and cover not in valid: raise ValueError("Foto de capa não encontrada.")
    if back and back not in valid: raise ValueError("Foto de contracapa não encontrada.")
    if not isinstance(interior, list) or len(interior) > MAX_PHOTOS: raise ValueError(f"O limite é de {MAX_PHOTOS} fotos internas.")
    if any(x not in valid for x in interior): raise ValueError("Uma ou mais fotos internas não foram encontradas.")
    data["cover"] = cover
    data["back_cover"] = back
    data["interior"] = interior
    ai_reference = payload.get("ai_reference") or []
    if not isinstance(ai_reference, list) or len(ai_reference) > MAX_PHOTOS: raise ValueError(f"O limite é de {MAX_PHOTOS} referências para a IA.")
    if any(x not in valid for x in ai_reference): raise ValueError("Uma ou mais referências da IA não foram encontradas.")
    data["ai_reference"] = ai_reference
    _save(project_id, data)
    return data
