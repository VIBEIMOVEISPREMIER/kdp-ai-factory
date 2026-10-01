import sqlite3
import os
from .config import DB_PATH, ensure_dirs

_USE_POSTGRES = bool(os.getenv("DATABASE_URL", "").strip())

if _USE_POSTGRES:
    import psycopg
    from psycopg.rows import dict_row


def connect():
    if _USE_POSTGRES:
        return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _sql(sql: str) -> str:
    return sql.replace("?", "%s") if _USE_POSTGRES else sql


def execute(db, sql: str, params=()):
    return db.execute(_sql(sql), params)


def init_db():
    with connect() as db:
        execute(db, """
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            book_type TEXT NOT NULL,
            language TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'created',
            progress INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        execute(db, """
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            progress INTEGER NOT NULL DEFAULT 0,
            error TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        if _USE_POSTGRES:
            execute(db, """
            CREATE TABLE IF NOT EXISTS kdp_factory_projects (
                project_id TEXT PRIMARY KEY,
                archive BYTEA NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """)
