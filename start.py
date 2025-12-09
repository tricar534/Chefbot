# start.py
import subprocess
import sys
import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    # ----- BACKEND CONFIG -----
    # Example: backend/app.py is your Flask/FastAPI file
    backend_cwd = ROOT / "backend"        # folder where backend lives
    backend_cmd = [sys.executable, "app.py"]  # or "main.py", etc.

    # ----- FRONTEND CONFIG -----
    # Example: React/Vite frontend in frontend/ folder
    frontend_cwd = ROOT / "frontend"
    frontend_cmd = ["npm", "run", "dev"]  # or "npm", "start"

    # Decide if we need shell=True (npm on Windows)
    use_shell = (platform.system() == "Windows")

    print("Starting backend...")
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=backend_cwd,
        shell=False  # Python is already sys.executable; no need for shell
    )

    print("Starting frontend...")
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_cwd,
        shell=use_shell
    )

    print("\nBackend and frontend started.")
    print("Press Ctrl+C to stop both.")

    try:
        # Wait for either to exit
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping processes...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()
