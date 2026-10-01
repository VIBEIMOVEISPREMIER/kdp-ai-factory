from __future__ import annotations

import logging
import os
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

import uvicorn
from kdp_factory.cli import app
from kdp_factory.db import init_db

HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}/"


def _log_path() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    if base:
        folder = Path(base) / "KDP-AI-Factory"
    else:
        folder = Path.home() / ".kdp-ai-factory"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "launcher.log"


LOG_PATH = _log_path()

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def _show_error(message: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "KDP AI Factory",
            f"O aplicativo não conseguiu iniciar.\n\n{message}\n\n"
            f"Log: {LOG_PATH}",
        )
        root.destroy()
    except Exception:
        logging.exception("Could not show error dialog")


def _open_browser_when_ready() -> None:
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(URL, timeout=2) as response:
                if 200 <= response.status < 500:
                    webbrowser.open(URL)
                    return
        except Exception:
            time.sleep(0.5)

    logging.error("Local dashboard did not become available within 30 seconds")
    _show_error(
        f"O Dashboard local não respondeu em 30 segundos.\n"
        f"Abra {URL} manualmente ou consulte o log."
    )


def _run_desktop() -> None:
    try:
        logging.info("Starting KDP AI Factory desktop")
        init_db()
        threading.Thread(target=_open_browser_when_ready, daemon=True).start()
        uvicorn.run(
            "kdp_factory.api:app",
            host=HOST,
            port=PORT,
            reload=False,
            log_config=None,
        )
    except Exception as exc:
        logging.exception("KDP AI Factory failed to start")
        _show_error(f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _run_desktop()
    else:
        app()
