"""Explicit MIRA.05 change only; old baselines remain immutable.
verify_analog_requirements.py independently validates every current connection.
"""
DELTA = {('U2109', '1'): ('MAT_DRV_CMD', 'GND'), ('U2109', '2'): ('unconnected-(U2109-RG-Pad2)', 'CC_CMD_SENSE'), ('U2109', '3'): ('unconnected-(U2109-RG-Pad3)', 'MAT_PI_RAW'), ('U2109', '4'): ('MAT_PI_RAW', 'N15'), ('U2109', '5'): ('N15', 'GND'), ('U2109', '6'): ('GND', 'CC_AW'), ('U2109', '7'): ('CC_AW', 'P15'), ('U2109', '8'): ('P15', 'unconnected-(U2109-NC-Pad8)')}
VALUE_OVERRIDES = {'R2302': '31.6k'}
def normalize_analog_rows(rows, board='Control'):
    if board != 'Control': return list(rows)
    return [(r,p,DELTA[r,p][0] if (r,p) in DELTA and n == DELTA[r,p][1] else n) for r,p,n in rows]
