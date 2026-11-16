"""Current draft maintenance entry point; preserves existing non-interface placement.
The original day-1 rebuild is archived under day1/build_draft.py; it would undo v0.2.
Usage: python3 build_draft.py /path/to/kicad-cli /path/to/python-with-pcbnew
"""
import subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
cli,pcbpython=sys.argv[1:3]
for cmd in [[sys.executable,str(P/'update_interface_schematics.py')],
            [sys.executable,str(P/'check_schematics.py'),cli],
            [sys.executable,str(P/'update_interface_pcb.py')],
            [sys.executable,str(P/'verify_fx23_drawings.py')],
            [pcbpython,str(P/'verify_interface.py')],
            [sys.executable,str(P/'u1_constraints.py')],
            [sys.executable,str(P/'render_review.py')]]:
 subprocess.run(cmd,check=True)
