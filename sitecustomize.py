"""Runtime defaults for local project execution.

Python imports this module automatically when the project root is on
``sys.path``. Keep it tiny: it only makes console output robust on Windows
terminals that still default to legacy encodings.
"""
import os
import sys

os.environ.setdefault("PYTHONUTF8", "1")

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass
