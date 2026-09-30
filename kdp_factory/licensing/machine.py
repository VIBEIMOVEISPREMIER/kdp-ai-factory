from __future__ import annotations

import hashlib
import platform
import subprocess
import uuid


def _windows_machine_guid() -> str:
    if platform.system() != "Windows":
        return ""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
            value, _ = winreg.QueryValueEx(key, "MachineGuid")
            return str(value)
    except Exception:
        return ""


def _powershell_value(script: str) -> str:
    if platform.system() != "Windows":
        return ""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True, text=True, timeout=3, check=False,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def machine_id() -> str:
    """Return a privacy-preserving stable installation fingerprint."""
    mac = f"{uuid.getnode():012x}"
    guid = _windows_machine_guid()
    cpu = _powershell_value(
        "(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty ProcessorId)"
    )
    raw = "|".join(["kdp-ai-factory-v1", mac, guid, cpu, platform.node()])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
