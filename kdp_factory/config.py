from pathlib import Path
import os
import sys

if getattr(sys, "frozen", False) and os.name == "nt":
    _base = Path(os.getenv("LOCALAPPDATA", Path.home())) / "KDP AI Factory"
else:
    _base = Path(__file__).resolve().parent.parent

def _path_env(name, default):
    return Path(os.getenv(name, str(default))).expanduser().resolve()

DATA_DIR = _path_env("KDP_FACTORY_DATA_DIR", _base / "data")
PROJECTS_DIR = DATA_DIR / "projects"
DB_PATH = DATA_DIR / "factory.sqlite3"
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
COMFYUI_URL = os.getenv("COMFYUI_BASE_URL", "http://127.0.0.1:8188").rstrip("/")
LICENSE_SERVER_URL = os.getenv("KDP_LICENSE_SERVER_URL", "https://kdp-ai-factory-license-server.onrender.com").rstrip("/")
LICENSE_STATE_PATH = DATA_DIR / "license_state.json"
LICENSE_PUBLIC_KEY_B64 = os.getenv("KDP_LICENSE_PUBLIC_KEY_B64", "YePeDo6HujQPXrIK+ffeYHzxaeV8QzdF41kFFCF/4Yo=")
PAYMENT_NETWORK = os.getenv("KDP_PAYMENT_NETWORK", "BSC")
PAYMENT_ADDRESS = os.getenv("KDP_PAYMENT_ADDRESS", "0x09fa433f8df884356bbb8a1afe1fb11bea3e12e5")
PAYMENT_PRICE_USD = float(os.getenv("KDP_PAYMENT_PRICE_USD", "50"))

def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
