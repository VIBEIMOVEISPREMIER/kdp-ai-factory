from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
def _path_env(name, default): return Path(os.getenv(name, str(default))).expanduser().resolve()
DATA_DIR = _path_env("KDP_FACTORY_DATA_DIR", ROOT/"data")
PROJECTS_DIR = DATA_DIR/"projects"
DB_PATH = DATA_DIR/"factory.sqlite3"
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL","http://127.0.0.1:11434").rstrip("/")
COMFYUI_URL = os.getenv("COMFYUI_BASE_URL","http://127.0.0.1:8188").rstrip("/")
def ensure_dirs():
    DATA_DIR.mkdir(parents=True,exist_ok=True); PROJECTS_DIR.mkdir(parents=True,exist_ok=True)
