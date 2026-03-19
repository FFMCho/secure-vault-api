#!/usr/bin/env python3
"""Docker-Entrypoint: Migrationen, dann App starten."""

import os
import subprocess
import sys


def main() -> int:
    """Führt Alembic-Migrationen aus und startet Uvicorn."""
    print("Running migrations...")
    result = subprocess.run(["alembic", "upgrade", "head"], env=os.environ)
    if result.returncode != 0:
        return result.returncode

    print("Starting API...")
    os.execvp("uvicorn", ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])


if __name__ == "__main__":
    sys.exit(main() or 0)
