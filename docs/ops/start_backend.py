#!/usr/bin/env python3
"""Startet Uvicorn mit .env-Variablen geladen."""
import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def main() -> None:
    load_env_file(ENV_FILE)
    os.environ.setdefault("PYTHONPATH", str(BACKEND_DIR))
    cmd = [
        str(BACKEND_DIR / ".venv" / "bin" / "uvicorn"),
        "app.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--workers", "1",
        "--log-level", "warning",
    ]
    subprocess.run(cmd, cwd=BACKEND_DIR, check=False)


if __name__ == "__main__":
    sys.exit(main() or 0)
