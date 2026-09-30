from fastapi import FastAPI
from pydantic import BaseModel
from .db import init_db
from .projects import create_project, list_projects
from .doctor import run_doctor

app = FastAPI(title="KDP AI Factory", version="0.1.0")

class ProjectCreate(BaseModel):
    name: str
    book_type: str = "custom"
    language: str = "pt-BR"

@app.on_event("startup")
def startup():
    init_db()

@app.get("/api/health")
def health():
    return {"ok": True, "service": "kdp-ai-factory"}

@app.get("/api/doctor")
def doctor():
    return run_doctor()

@app.get("/api/projects")
def projects():
    return list_projects()

@app.post("/api/projects")
def new_project(payload: ProjectCreate):
    return create_project(payload.name, payload.book_type, payload.language)
