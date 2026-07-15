"""Einstiegspunkt: startet die Notenheft-Tkinter-App."""

import sys
from pathlib import Path

# Ermöglicht den Start via `python src/main.py` ohne Installation als Paket.
sys.path.insert(0, str(Path(__file__).parent))

from notenheft.gui.app import run  # noqa: E402

if __name__ == "__main__":
    run()
