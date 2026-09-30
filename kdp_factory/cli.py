import json, typer, uvicorn
from pathlib import Path
from .db import init_db
from .projects import create_project, list_projects
from .doctor import run_doctor
from .config import ensure_dirs
from .ai.registry import registry
from .models.manager import ModelManager
from .kdp.validator import KDPValidator
app=typer.Typer(help="KDP AI Factory — fábrica editorial local-first.")
@app.command()
def doctor(): typer.echo(json.dumps(run_doctor(),indent=2,ensure_ascii=False))
@app.command()
def ai(): typer.echo(json.dumps(registry.status(),indent=2,ensure_ascii=False))
@app.command()
def models(): typer.echo(json.dumps({"hardware":ModelManager().hardware(),"installed":ModelManager().ollama_models(),"recommended":ModelManager().recommendations()},indent=2,ensure_ascii=False))
@app.command()
def init(): ensure_dirs(); init_db(); typer.echo("KDP AI Factory inicializado.")
@app.command("new")
def new(name:str,book_type:str="custom",language:str="pt-BR"): init_db(); typer.echo(json.dumps(create_project(name,book_type,language),indent=2,ensure_ascii=False))
@app.command("list")
def projects(): init_db(); typer.echo(json.dumps(list_projects(),indent=2,ensure_ascii=False))
@app.command("validate")
def validate(spec_file:Path,pdf:Path|None=None):
    spec=json.loads(spec_file.read_text(encoding="utf-8")); issues=KDPValidator().validate_pdf(pdf,spec) if pdf else KDPValidator().validate_spec(spec)
    typer.echo(json.dumps([i.__dict__ for i in issues],indent=2,ensure_ascii=False)); raise typer.Exit(code=1 if any(i.level=="error" for i in issues) else 0)
@app.command()
def start(host:str="127.0.0.1",port:int=8000): init_db(); typer.echo(f"API: http://{host}:{port}"); uvicorn.run("kdp_factory.api:app",host=host,port=port,reload=False)
if __name__=="__main__": app()
