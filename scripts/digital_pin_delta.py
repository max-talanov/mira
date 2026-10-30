"""Explicit MIRA.04 migration for checks against immutable pre-MIRA.04 baselines.
The current hardware contract is independently enforced by verify_digital_interfaces.py.
"""
DELTA = {
    ('U500', 'AB12'): ('MCU_FPGA_SCK_F', 'unconnected-(U500C-IO_L7N_T1_13-PadAB12)'),
    ('U500', 'Y11'): ('unconnected-(U500C-IO_L11P_T1_SRCC_13-PadY11)', 'MCU_FPGA_SCK_F'),
}
def normalize_digital_rows(rows, board='Control'):
    if board != 'Control':
        return list(rows)
    return [(r,p,DELTA[r,p][0] if (r,p) in DELTA and n == DELTA[r,p][1] else n)
            for r,p,n in rows]
