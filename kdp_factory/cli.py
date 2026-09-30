import json
import typer
import uvicorn
from .db import init_db
from .projects import create_project, list_projects
from .doctor import run_doctor
from .config import ensure_dirs

app = typer.Typer(help="KDP AI Factory command line interface.")

@app.command()
def doctor():
    """Diagnose the local machine and optional AI services."""
    typer.echo(json.dumps(run_doctor(), indent=2, ensure_ascii=False))

@app.command()
def init():
    """Initialize local data folders and database."""
    ensure_dirs()
    init_db()
    typer.echo("KDP AI Factory inicializado com sucesso.")

@app.command("new")
def new(name: str, book_type: str = "custom", language: str = "pt-BR"):
    """Create a new book project."""
    init_db()
    project = create_project(name, book_type, language)
    typer.echo(json.dumps(project, indent=2, ensure_ascii=False))

@app.command("list")
def projects():
    """List local projects."""
    init_db()
    typer.echo(json.dumps(list_projects(), indent=2, ensure_ascii=False))

@app.command()
def start(host: str = "127.0.0.1", port: int = 8000):
    """Start the local API/dashboard server."""
    init_db()
    typer.echo(f"Servidor: http://{host}:{port}")
    uvicorn.run("kdp_factory.api:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    app()
