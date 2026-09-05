#!/usr/bin/env python3
"""
Football Scanner AI — Launcher
Starts the FastAPI server and opens the browser.
Works as-is on any Python 3.10+ environment.
Used as the entry point for the .exe build.
"""
import sys
import os
import time
import threading
import webbrowser
import subprocess

# Ensure the project root is on the path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from config.settings import settings


def open_browser(url: str, delay: float = 2.5):
    """Open browser after short delay to let server start."""
    def _open():
        time.sleep(delay)
        webbrowser.open(url)
    t = threading.Thread(target=_open, daemon=True)
    t.start()


def print_banner():
    print("=" * 60)
    print("  ⚽  Football Scanner AI  v1.0.0")
    print("=" * 60)
    print(f"  Modo DB   : {settings.db_mode.upper()}")
    print(f"  Provider  : {settings.sports_api_provider}")
    print(f"  Endereço  : http://{settings.app_host}:{settings.app_port}")
    print("=" * 60)
    print("  Pressione Ctrl+C para encerrar")
    print()


def main():
    print_banner()
    url = f"http://{settings.app_host}:{settings.app_port}"
    open_browser(url)

    # Run uvicorn programmatically
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.app_host,
        port=settings.app_port,
        log_level=settings.log_level.lower(),
        reload=False,
    )


if __name__ == "__main__":
    main()
