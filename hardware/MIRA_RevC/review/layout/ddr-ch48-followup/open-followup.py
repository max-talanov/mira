"""Materialize a follow-up PCB with its trial-only fabrication rules."""
import argparse
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from sexpr_tools import children


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trial", choices=("analog", "pth", "pth-015", "pth-limit", "pth-reflow", "hdi"))
    parser.add_argument("output", type=Path, help="new directory")
    args = parser.parse_args()

    name = "MIRA_Control"
    trial = HERE / ("pth" if args.trial in ("pth-reflow", "pth-015") else args.trial)
    subprocess.run(
        [sys.executable, str(HERE.parent / "MIRA-01.03.00/open-trial.py"),
         str((HERE / "pth-015.sexpr.gz") if args.trial == "pth-015" else trial.with_suffix(".sexpr.gz")), str(args.output)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    project = args.output / name
    pcb = project / (name + ".kicad_pcb")
    if args.trial == "pth-reflow":
        pcb.write_bytes(gzip.decompress((HERE / "pth-reflow.kicad_pcb.gz").read_bytes()))
    stack = trial.with_suffix(".stackup")
    if stack.exists():
        text = pcb.read_text()
        start, end, setup = next(item for item in children(text) if item[2].startswith("(setup"))
        low, high, _ = next(item for item in children(setup) if item[2].startswith("(stackup"))
        new_setup = setup[:low] + stack.read_text().rstrip() + setup[high:]
        pcb.write_text(text[:start] + new_setup + text[end:])

    rules = trial.with_suffix(".rules.json")
    original = project / (name + ".kicad_pro")
    data = json.loads(original.read_text())
    data["board"]["design_settings"]["rules"].update(json.loads(rules.read_text()))
    original.write_text(json.dumps(data, indent=2) + "\n")
    shutil.copyfile(trial.with_suffix(".kicad_dru"), project / (name + ".kicad_dru"))
    print(pcb.resolve())


if __name__ == "__main__":
    main()
