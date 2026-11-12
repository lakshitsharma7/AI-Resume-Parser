import os
import sys
import time
import webbrowser
import threading
import multiprocessing
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Ensure storage directories exist
STORAGE_DIR = BASE_DIR / "storage"
(STORAGE_DIR / "uploads").mkdir(parents=True, exist_ok=True)

def open_browser():
    """Wait for server to start and open browser."""
    time.sleep(1.8)
    url = "http://127.0.0.1:8000"
    print(f"\n[+] Opening AI Resume Parser Dashboard in your default browser: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[!] Could not open browser automatically: {e}")

def main():
    # Required for Windows PyInstaller multiprocessing
    multiprocessing.freeze_support()

    print("=" * 65)
    print("      AI RESUME PARSER - STANDALONE DESKTOP APPLICATION")
    print("=" * 65)
    print("  Status:       Starting local server...")
    print("  Web Dashboard: http://127.0.0.1:8000/")
    print("  REST API:      http://127.0.0.1:8000/api/v1/resumes/parse")
    print("  Swagger Docs:  http://127.0.0.1:8000/docs")
    print("=" * 65)
    print("  Press Ctrl+C in this terminal window to stop the server.\n")

    # Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Import uvicorn and app after freeze_support
    import uvicorn
    from app.main import app

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    main()

