"""Quant Strategy Lab home."""
import os
import runpy
import sys

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "quant-lab"))
TARGET = os.path.join(APP_DIR, 'home.py')
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
runpy.run_path(TARGET, run_name="__main__")
