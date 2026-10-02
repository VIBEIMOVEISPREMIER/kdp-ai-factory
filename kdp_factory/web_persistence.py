from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

from .config import PROJECTS_DIR
from .db import connect, execute


def enabled() -> bool:
    # Desktop builds are strictly local-first: project archives, images, PDFs
    # and exports must never be copied to Neon. The web deployment can still
    # enable DATABASE_URL normally.
    local_mode = os.getenv("KDP_FACTORY_LOCAL_MODE", "").strip().lower() in {"1", "true", "yes", "on"}
    return bool(os.getenv("DATABASE_URL", "").strip()) and not local_mode


def persistence_status() -> dict:
    if not enabled():
        return {"enabled": False, "backend": "local"}
    with connect() as db:
        row = execute(db, "SELECT COUNT(*) AS count FROM kdp_factory_projects").fetchone()
    return {"enabled": True, "backend": "neon-postgres", "project_archives": int(row["count"])}


def persist_project(project_id: str) -> None:
    if not enabled():
        return
    root = PROJECTS_DIR / project_id
    if not root.exists():
        return

    buffer = io.BytesIO()
    # Neon is the metadata persistence layer, not a large-file store.
    # Keep the project state recoverable but never copy uploaded/generated
    # binaries (PDFs, images, exports) into the database archive.
    excluded_roots={"imports","images","exports","cover"}
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in root.rglob("*"):
            if not path.is_file() or path.name.endswith(".tmp"):
                continue
            rel=path.relative_to(root)
            if rel.parts and rel.parts[0] in excluded_roots:
                continue
            zf.write(path, rel.as_posix())

    with connect() as db:
        execute(
            db,
            """
            INSERT INTO kdp_factory_projects(project_id, archive, updated_at)
            VALUES (?, ?, NOW())
            ON CONFLICT(project_id)
            DO UPDATE SET archive=EXCLUDED.archive, updated_at=NOW()
            """,
            (project_id, buffer.getvalue()),
        )


def restore_projects() -> int:
    if not enabled():
        return 0

    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    restored = 0
    with connect() as db:
        rows = execute(
            db,
            "SELECT project_id, archive FROM kdp_factory_projects ORDER BY updated_at ASC",
        ).fetchall()

    for row in rows:
        project_id = row["project_id"]
        target = PROJECTS_DIR / project_id
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(bytes(row["archive"]))) as zf:
            zf.extractall(target)
        restored += 1

    return restored
