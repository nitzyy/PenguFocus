from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "sessions.log"

def ensure_dirs():
    LOG_DIR.mkdir(exist_ok=True)
    Path("images").mkdir(exist_ok=True)

def write_log(message):
    ensure_dirs()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] {message}\n")

def read_logs():
    if not LOG_FILE.exists():
        return []
    with LOG_FILE.open("r", encoding="utf-8") as f:
        return f.readlines()