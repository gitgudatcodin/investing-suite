"""Market Pulse — real-time regime dashboard."""
import os
import runpy
import sys

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "market-pulse"))
TARGET = os.path.join(APP_DIR, 'app.py')
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
runpy.run_path(TARGET, run_name="__main__")
