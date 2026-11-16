"""MIRA replaceable adapter interface v0.2, dimensions in mm, common Control top view."""
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
PAIRS=[dict(pair='A',control='J1800',module='J1',x=176.,y=68.5),dict(pair='B',control='J1801',module='J2',x=180.,y=85.5)]
OUTLINE=(147.,62.,207.,92.)
MOUNTS=[('H1800','H1',152.,77.,2.2),('H1801','H2',202.,77.,2.2)]
KEY=('H1802','H3',153.,86.,2.2)
# P1..P4 correspond to Hirose Power Contact No.1..4, separate from 80 signal positions.
# Common assembled top view: P1 LL, P2 LR, P3 UL, P4 UR.
POWER_PINS=['P1','P2','P3','P4']
def pinout(pair):
 signals=[f'{"BL" if pair=="A" else "NL"}{i}' for i in range(32)]+[f'WL{i}' for i in range(0 if pair=='A' else 16,16 if pair=='A' else 32)]
 it=iter(signals); result={}
 for n in range(1,81):result[str(n)]=('NC' if n>70 else 'GND' if n<=66 and n%3==0 else next(it))
 result.update({p:'GND' for p in POWER_PINS})
 return result
