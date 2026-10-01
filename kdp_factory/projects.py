from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json
import os
import shutil

from .config import PROJECTS_DIR, ensure_dirs
from .db import connect
from .books.templates import template_for
from .licensing.client import assert_can_create_book, register_book_created


def now():
    return datetime.now(timezone.utc).isoformat()


def _safe_json_write(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    backup = path.with_suffix(path.suffix + ".bak")
    text = json.dumps(data, indent=2, ensure_ascii=False)
    tmp.write_text(text, encoding="utf-8")
    if path.exists():
        shutil.copy2(path, backup)
    os.replace(tmp, path)


def project_dir(project_id: str):
    return PROJECTS_DIR / project_id


def create_project(name: str, book_type: str, language: str, **overrides):
    ensure_dirs()
    pid = str(uuid4())

    # In official mode the remote licensing service is authoritative for trial use.
    assert_can_create_book(pid)

    stamp = now()
    folder = project_dir(pid)
    for d in ("manuscript", "images", "exports", "logs", "imports", "cover", "validation"):
        (folder / d).mkdir(exist_ok=True)

    tpl = template_for(book_type)
    spec = {"title": name, "book_type": book_type, "language": language, **tpl, **overrides}
    manifest = {
        "id": pid,
        "name": name,
        "book_type": book_type,
        "language": language,
        "status": "created",
        "progress": 0,
        "version": 1,
        "created_at": stamp,
        "updated_at": stamp,
        "spec": spec,
    }

    _safe_json_write(folder / "project.json", manifest)
    _safe_json_write(folder / "book_spec.json", spec)
    _safe_json_write(folder / "checkpoints.json", [])

    with connect() as db:
        db.execute(
            "INSERT INTO projects VALUES (?, ?, ?, ?, 'created', 0, ?, ?)",
            (pid, name, book_type, language, stamp, stamp),
        )

    register_book_created()
    return manifest


def get_project(project_id: str):
    p = project_dir(project_id) / "project.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        backup = p.with_suffix(p.suffix + ".bak")
        if backup.exists():
            data=json.loads(backup.read_text(encoding="utf-8"))
            _safe_json_write(p,data)
            return data
        return None


def update_project(project_id: str, **changes):
    data = get_project(project_id)
    if not data:
        return None

    data.update(changes)
    data["updated_at"] = now()
    data["version"] = int(data.get("version", 1)) + 1

    p = project_dir(project_id) / "project.json"
    _safe_json_write(p, data)

    with connect() as db:
        fields = []
        values = []
        for k in ("name", "book_type", "language", "status", "progress"):
            if k in changes:
                fields.append(f"{k}=?")
                values.append(changes[k])
        if fields:
            values += [data["updated_at"], project_id]
            db.execute(
                f"UPDATE projects SET {','.join(fields)},updated_at=? WHERE id=?",
                values,
            )

    return data


def checkpoint(project_id: str, stage: str, state: dict):
    p = project_dir(project_id) / "checkpoints.json"
    items = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    items.append({"stage": stage, "timestamp": now(), "state": state})
    _safe_json_write(p, items)
    return items[-1]


def list_projects():
    with connect() as db:
        return [
            dict(row)
            for row in db.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC"
            ).fetchall()
        ]
