from __future__ import annotations

import logging
import os
import sys
import threading
import time
import urllib.request
from pathlib import Path

import uvicorn
from kdp_factory.cli import app
from kdp_factory.db import init_db

HOST = "127.0.0.1"
PORT = int(os.environ.get("KDP_FACTORY_PORT", "8000"))
URL = f"http://{HOST}:{PORT}/"


def _log_path() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    folder = Path(base) / "KDP-AI-Factory" if base else Path.home() / ".kdp-ai-factory"
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
            f"O aplicativo não conseguiu iniciar.\n\n{message}\n\nLog: {LOG_PATH}",
        )
        root.destroy()
    except Exception:
        logging.exception("Could not show error dialog")


def _wait_for_server(timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(URL, timeout=2) as response:
                if 200 <= response.status < 500:
                    return True
        except Exception:
            time.sleep(0.25)
    return False


def _serve() -> None:
    try:
        uvicorn.run(
            "kdp_factory.api:app",
            host=HOST,
            port=PORT,
            reload=False,
            log_config=None,
        )
    except Exception:
        logging.exception("Local API server stopped unexpectedly")


def _run_server_only() -> None:
    """Headless mode used by Linux CI and server environments.

    Linux builds must not initialize pywebview because GitHub Actions runners
    have no GTK/Qt desktop session. The API is still fully testable here.
    """
    logging.info("Starting KDP AI Factory in headless/server mode")
    init_db()
    _serve()


def _run_desktop() -> None:
    try:
        logging.info("Starting KDP AI Factory desktop")
        init_db()

        server_thread = threading.Thread(target=_serve, daemon=True, name="kdp-local-api")
        server_thread.start()

        if not _wait_for_server():
            raise RuntimeError(
                f"O servidor local não respondeu em {URL} dentro de 30 segundos."
            )

        logging.info("Local API/dashboard ready at %s", URL)

        # Windows is a native desktop app. It never opens the SaaS URL and
        # never downloads the web application. The bundled dashboard is served
        # only by the local FastAPI process.
        import webview

        webview.create_window(
            "KDP AI Factory",
            URL,
            width=1440,
            height=900,
            min_size=(1100, 700),
            resizable=True,
            text_select=True,
        )
        webview.start()
        logging.info("Desktop window closed")
    except Exception as exc:
        logging.exception("KDP AI Factory failed to start")
        _show_error(f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    # The desktop GUI is intentionally Windows-only. On Linux/macOS, run the
    # local API in headless mode so CI and server environments never try to
    # load GTK/Qt through pywebview.
    if sys.platform == "win32" and len(sys.argv) == 1:
        _run_desktop()
    elif len(sys.argv) == 1:
        _run_server_only()
    else:
        app()
