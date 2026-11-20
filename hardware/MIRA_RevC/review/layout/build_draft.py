"""Current draft maintenance entry point; preserves existing non-interface placement.
The original day-1 rebuild is archived under day1/build_draft.py; it would undo v0.2.
Usage: python3 build_draft.py /path/to/kicad-cli /path/to/python-with-pcbnew
"""
# The active socket trial must not be overwritten by the historical first-day builder.
from pathlib import Path as _GuardPath
_guard_base=_GuardPath(__file__).resolve().parents[2]
if '"MIRA_Module:ICS-CQFP64-1830-1830-100-1"' in (_guard_base/'MIRA_Crossbar/MIRA_Crossbar.kicad_pcb').read_text():
 raise SystemExit('Active ICS socket trial: use review/layout/socket-trial tools; old draft rebuild is intentionally disabled.')

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
