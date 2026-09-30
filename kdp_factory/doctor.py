import os
import platform
import shutil
import psutil
import httpx

from .config import OLLAMA_URL, COMFYUI_URL, ensure_dirs

def command_exists(name):
    return shutil.which(name) is not None

def service(url):
    try:
        r = httpx.get(url, timeout=2)
        return {"online": True, "status": r.status_code}
    except Exception as exc:
        return {"online": False, "error": str(exc)}

def run_doctor():
    ensure_dirs()
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    docker_mode = os.path.exists("/.dockerenv")
    return {
        "runtime": "docker" if docker_mode else "native",
        "os": platform.platform(),
        "python": platform.python_version(),
        "git": command_exists("git"),
        "node": command_exists("node"),
        "npm": command_exists("npm"),
        "ollama_cli": command_exists("ollama"),
        "comfyui": service(COMFYUI_URL),
        "ollama_service": service(OLLAMA_URL),
        "ram_gb": round(vm.total / 1024**3, 1),
        "ram_available_gb": round(vm.available / 1024**3, 1),
        "disk_free_gb": round(disk.free / 1024**3, 1),
    }
