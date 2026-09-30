from datetime import datetime, timezone
from uuid import uuid4
from .db import connect

def now():
    return datetime.now(timezone.utc).isoformat()

def create_task(project_id: str, name: str):
    tid = str(uuid4()); stamp = now()
    with connect() as db:
        db.execute("INSERT INTO tasks VALUES (?, ?, ?, 'pending', 0, NULL, ?, ?)",
                   (tid, project_id, name, stamp, stamp))
    return tid

def update_task(task_id: str, status: str, progress: int = 0, error: str | None = None):
    with connect() as db:
        db.execute("UPDATE tasks SET status=?,progress=?,error=?,updated_at=? WHERE id=?",
                   (status, progress, error, now(), task_id))

def list_tasks(project_id: str):
    with connect() as db:
        return [dict(r) for r in db.execute(
            "SELECT * FROM tasks WHERE project_id=? ORDER BY created_at", (project_id,)
        ).fetchall()]
