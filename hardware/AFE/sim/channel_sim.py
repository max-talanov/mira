"""MIRA AFE channel v3 (±5 mA, no Kelvin mux, ±15 V amplifier rails), TI OPA197 model, ngspice.

VSET -> OPA197 +IN. -IN = S (line sense). OUT -> [TMUX6112 SPST + R_k] (k=1..3) and R4 (+Cf4) -> F (force node).
F -> connect switch -> LINE. LINE -> sense switch -> S. RFS (10M) F-S keeps the loop closed when both are open.
Fb = OPA197 follower of F. Current = (V(OUT) - V(Fb)) / R_eff, R_eff = (R_k + Ron) || R4 (or R4 alone).
Switches are static resistors (Ron 120 ohm on, 1e12 off) with datasheet capacitances and off-leakage sources.
Usage: python3 chan2.py dc|pulse RANGE [Cf]
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
R = {1: 1000.0, 2: 20e3, 3: 2e6, 4: 200e6}
RON = 120.0
LEAK = 0.02e-9          # TMUX6112 off-leakage, 25 °C max (datasheet)


def netlist(rng, step, T, rcell, vset_src, cline=30e-12, cf=None, cf4=0.5e-12, meas=""):
    on = {k: k == rng for k in (1, 2, 3)}
    cf = cf or {}
    L = ["* MIRA channel v2", ".include models/opa197/OPAx197.LIB",
         "VCC vp 0 PWL(0 0 5u 15)", "VEE vn 0 PWL(0 0 5u -15)", vset_src,
         "RMUX vs vsp 60", "CIN vsp 0 5p", "XA vsp s vp vn out OPAx197"]
    for k in (1, 2, 3):
        L += [f"RS{k} out d{k} {RON if on[k] else 1e12}", f"R{k} d{k} f {R[k]}", f"CD{k} d{k} 0 {4e-12 if on[k] else 3e-12}"]
        if not on[k]:
            L += [f"IL{k} 0 d{k} {LEAK}"]     # range switch off-leakage
        if cf.get(k):
            L.append(f"CF{k} d{k} f {cf[k]}")
    L += [f"R4 out f {R[4]}", f"CF4 out f {cf4}", "CF 0 f 6p",
          f"RSC f line {RON}", "CLS line 0 7p", f"CLINE line 0 {cline}", f"RCELL line 0 {rcell}",
          f"RSS line s {RON}", "CSS s 0 4p", "RFS f s 10e6",
          "IB1 0 line 0.02e-9",                                    # bleed switch off-leakage
          "XB f fb vp vn fb OPAx197",
          f".tran {step} {T}", ".control", "run", meas, ".endc", ".end"]
    return "\n".join(L)


def tap(rng):
    return "out"


def reff(rng):
    return R[4] if rng == 4 else 1 / (1 / (R[rng] + RON) + 1 / R[4])


def run(name, text, timeout=3000):
    p = HERE / f"{name}.cir"
    p.write_text(text)
    o = subprocess.run(["ngspice", "-b", str(p)], cwd=HERE, capture_output=True, text=True, timeout=timeout).stdout
    return {m[1]: float(m[2]) for m in re.finditer(r"^(\w+)(?:\[n\])?\s*=\s*([-+0-9.eE]+)", o, re.M)}, o


def dc(rng):
    cases = {1: [(2.5, 1e3, "2.5 mA"), (0.5, 100.0, "5 mA")], 2: [(0.5, 20e3, "25 µA")], 3: [(0.2, 1e6, "200 nA")],
             4: [(0.2, 100e6, "2 nA"), (0.1, 1e9, "100 pA"), (2.5, 1e9, "2.5 nA")]}[rng]
    T, step = {1: ("40u", "50n"), 2: ("200u", "200n"), 3: ("5m", "5u"), 4: ("600m", "100u")}[rng]
    for vset, rcell, label in cases:
        meas = (f"let il = v(line)/{rcell}\nlet im = (v({tap(rng)})-v(fb))/{reff(rng)!r}\n"
                "let n = length(il)-1\nprint il[n] im[n] v(line)[n]")
        v, o = run(f"v2dc_{rng}_{rcell:.0e}", netlist(rng, step, T, rcell, f"VSET vs 0 PWL(0 0 3u 0 8u {vset})", meas=meas))
        if "il" not in v:
            print(f"range {rng} {label}: FAILED"); continue
        il, im, vl = v["il"], v["im"], v["v"] if "v" in v else float(re.search(r"^v\(line\)\[n\] = (\S+)", o, re.M)[1])
        print(f"range {rng} ({label:7s}): V(line) {vl:.5f} V (set {vset}), I_line {il:.4e}, I_meas {im:.4e}, "
              f"error {im - il:+.2e} A ({(im - il) / il * 100:+.3f} %)", flush=True)


def pulse(rng, cfk=0.0):
    rcell = {1: 1e3, 2: 100e3, 3: 10e6}[rng]
    cf = {rng: cfk} if cfk else {}
    src = "VSET vs 0 PULSE(0 2.5 20u 20n 20n 10u 40u)"
    meas = (f"let im = (v({tap(rng)})-v(fb))/{reff(rng)!r}\n"
            "meas tran vmax MAX v(line) from=20u to=29u\n"
            "meas tran t1 WHEN v(line)=2.4975 RISE=LAST\n"
            "meas tran t2 WHEN v(line)=2.475 RISE=1\n"
            "meas tran imax MAX im from=20u to=29u\n"
            "meas tran ifin FIND im AT=29u\n"
            "meas tran i1us FIND im AT=21u\n")
    v, o = run(f"v2p_{rng}_{cfk:.0e}", netlist(rng, "2n", "30u", rcell, src, cf=cf, meas=meas))
    if "vmax" not in v:
        print(f"range {rng} Cf {cfk}: FAILED"); return
    print(f"range {rng}, Rcell {rcell:.0e}, Cf {cfk * 1e12:.1f} pF: overshoot {v['vmax'] - 2.5:+.3f} V, "
          f"1 % at {(v.get('t2', 0) - 20e-6) * 1e9:.0f} ns, 0.1 % at {(v.get('t1', 0) - 20e-6) * 1e9:.0f} ns, "
          f"I peak {v['imax']:.3e}, I at 1 µs {v['i1us']:.3e}, I end {v['ifin']:.3e} (expected {2.5 / rcell:.3e})", flush=True)


if __name__ == "__main__":
    mode, rng = sys.argv[1], int(sys.argv[2])
    cfk = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    dc(rng) if mode == "dc" else pulse(rng, cfk)
