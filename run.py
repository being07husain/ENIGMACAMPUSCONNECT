import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

# Locate project directories
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR / "EnigmaCampusConnect-main 2" if (SCRIPT_DIR / "EnigmaCampusConnect-main 2").exists() else SCRIPT_DIR
BACKEND_DIR = PROJECT_DIR / "backend"
VENV_PYTHON = SCRIPT_DIR / "venv" / "Scripts" / "python.exe"

# If user runs with global python and dependencies aren't in it, switch to venv automatically
if VENV_PYTHON.exists() and sys.executable.lower() != str(VENV_PYTHON).lower():
    try:
        import uvicorn
        import fastapi
        import pymongo
    except ImportError:
        print(f"[*] Switching to project virtual environment: {VENV_PYTHON}")
        cmd = [str(VENV_PYTHON), str(Path(__file__).resolve())] + sys.argv[1:]
        sys.exit(subprocess.call(cmd))

# Add directories to sys.path so modules resolve correctly
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import uvicorn


def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000/Views/login.html")


def main():
    print("=" * 65)
    print("   CampusConnect Backend Server Starting...")
    print("=" * 65)
    print("   Login URL:     http://127.0.0.1:8000/Views/login.html")
    print("   Register URL:  http://127.0.0.1:8000/Views/register.html")
    print("   API Docs:      http://127.0.0.1:8000/docs")
    print("   Health Check:  http://127.0.0.1:8000/api/health")
    print("=" * 65)
    print("   Demo Accounts:")
    print("   - Club:    codingclub@campusconnect.com / Club@12345")
    print("   - Faculty: faculty@campusconnect.com    / Faculty@12345")
    print("=" * 65)
    print("   Opening browser in 1.5 seconds...\n")

    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        app_dir=str(PROJECT_DIR)
    )


if __name__ == "__main__":
    main()
