"""Materialize a review overlay in a new KiCad project directory."""
import argparse
import gzip
import hashlib
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from sexpr_tools import children

SOURCE = HERE.parent.parent.parent / "MIRA_Control"
PROJECT = "MIRA_Control"


def geometry_hash(pcb):
    geometry = (node for _, _, node in children(pcb)
                if node.split(None, 1)[0] in ("(footprint", "(gr_line", "(gr_arc", "(gr_rect"))
    return hashlib.sha256("\n".join(geometry).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("overlay", type=Path)
    parser.add_argument("output", type=Path, help="new directory for the review project")
    args = parser.parse_args()
    base = (SOURCE / f"{PROJECT}.kicad_pcb").read_text()
    expected_hash, overlay = gzip.decompress(args.overlay.read_bytes()).decode().split("\n", 1)
    if geometry_hash(base) != expected_hash:
        parser.error("Control footprint or outline geometry differs from this trial's revision")
    args.output.mkdir(parents=True, exist_ok=False)
    target = args.output / PROJECT
    target.mkdir()
    for name in (f"{PROJECT}.kicad_pro", f"{PROJECT}.kicad_dru", "fp-lib-table", "sym-lib-table"):
        shutil.copy2(SOURCE / name, target / name)
    for sheet in sorted(SOURCE.glob("*.kicad_sch")):
        (target / sheet.name).symlink_to(sheet)
    (target / "libraries").symlink_to(SOURCE / "libraries", target_is_directory=True)
    (args.output / "libraries").symlink_to(SOURCE.parent / "libraries", target_is_directory=True)
    pcb = target / f"{PROJECT}.kicad_pcb"
    pcb.write_text(base.rstrip()[:-1] + overlay + ")\n")
    print(pcb.resolve())


if __name__ == "__main__":
    main()
