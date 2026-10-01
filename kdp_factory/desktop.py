from __future__ import annotations
import argparse
import threading
import time
import webbrowser
import uvicorn
from .hardware import detect
from .api import app

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--compatibility-check",action="store_true")
    parser.add_argument("--host",default="127.0.0.1")
    parser.add_argument("--port",type=int,default=8765)
    args=parser.parse_args()
    profile=detect()
    if args.compatibility_check:
        print({"tier":profile.tier,"ram_gb":profile.ram_gb,"vram_gb":profile.vram_gb,"local_images":profile.local_images})
        return 0
    def open_browser():
        time.sleep(1.2)
        webbrowser.open(f"http://{args.host}:{args.port}")
    threading.Thread(target=open_browser,daemon=True).start()
    uvicorn.run(app,host=args.host,port=args.port,log_level="info")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
