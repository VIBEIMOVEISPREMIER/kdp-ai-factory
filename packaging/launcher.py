from __future__ import annotations
import sys
import threading
import time
import webbrowser
import uvicorn
from kdp_factory.cli import app
from kdp_factory.db import init_db

def _open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8000/")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        init_db()
        threading.Thread(target=_open_browser, daemon=True).start()
        uvicorn.run("kdp_factory.api:app", host="127.0.0.1", port=8000, reload=False)
    else:
        app()
