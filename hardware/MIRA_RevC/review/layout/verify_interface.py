"""MIRA-01.01.00 entry point. Earlier local tool preserved under baseline/."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parent/"MIRA-01.01.00/tools/verify_saved.py"),run_name="__main__")
