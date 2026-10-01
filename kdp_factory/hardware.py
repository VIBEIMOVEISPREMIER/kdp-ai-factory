"""Hardware profile and capability tiers for the desktop edition."""
from __future__ import annotations
import os, platform, shutil, subprocess
from dataclasses import asdict, dataclass
import psutil

@dataclass
class HardwareProfile:
    os: str
    arch: str
    ram_gb: float
    vram_gb: float | None
    free_disk_gb: float
    tier: str
    local_images: bool
    notes: list[str]

def _gpu_vram_gb() -> float | None:
    if os.name != "nt":
        return None
    try:
        cmd = ["powershell", "-NoProfile", "-Command",
               "(Get-CimInstance Win32_VideoController | Measure-Object -Property AdapterRAM -Maximum).Maximum / 1GB"]
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL, timeout=5).strip()
        value = float(out)
        return value if value > 0 else None
    except Exception:
        return None

def detect() -> HardwareProfile:
    ram = round(psutil.virtual_memory().total / (1024**3), 1)
    drive = os.environ.get("SystemDrive", "C:\") if os.name == "nt" else "/"
    free = round(shutil.disk_usage(drive).free / (1024**3), 1)
    vram = _gpu_vram_gb()
    if ram < 8:
        tier, images, notes = "unsupported", False, ["A instalação não é recomendada abaixo de 8 GB de RAM."]
    elif ram < 12 or (vram is not None and vram < 4):
        tier, images, notes = "compatibility", False, ["Modo Compatibilidade: recursos editoriais e KDP disponíveis; geração local de imagens desativada."]
    elif ram < 16 or (vram is not None and vram < 6):
        tier, images, notes = "standard", bool(vram and vram >= 4), ["Modo Padrão: use modelos e workflows leves."]
    elif ram < 32 or (vram is not None and vram < 8):
        tier, images, notes = "full", bool(vram and vram >= 6), ["Modo Completo: modelos locais de porte moderado."]
    else:
        tier, images, notes = "pro", True, ["Modo Pro: hardware adequado para modelos locais maiores."]
    if vram is None:
        notes.append("VRAM não detectada; geração local só será habilitada após teste do mecanismo.")
    return HardwareProfile(platform.system(), platform.machine(), ram, vram, free, tier, images, notes)

def as_dict() -> dict:
    return asdict(detect())
