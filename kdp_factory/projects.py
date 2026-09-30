from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json
from .config import PROJECTS_DIR, ensure_dirs
from .db import connect

def now():
    return datetime.now(timezone.utc).isoformat()

def create_project(name: str, book_type: str, language: str):
    ensure_dirs()
    pid = str(uuid4())
    stamp = now()
    folder = PROJECTS_DIR / pid
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "manuscript").mkdir(exist_ok=True)
    (folder / "images").mkdir(exist_ok=True)
    (folder / "exports").mkdir(exist_ok=True)
    (folder / "logs").mkdir(exist_ok=True)
    manifest = {
        "id": pid, "name": name, "book_type": book_type,
        "language": language, "status": "created", "progress": 0
    }
    (folder / "project.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with connect() as db:
        db.execute(
            "INSERT INTO projects VALUES (?, ?, ?, ?, 'created', 0, ?, ?)",
            (pid, name, book_type, language, stamp, stamp)
        )
    return manifest

def list_projects():
    with connect() as db:
        return [dict(row) for row in db.execute(
            "SELECT * FROM projects ORDER BY updated_at DESC"
        ).fetchall()]
