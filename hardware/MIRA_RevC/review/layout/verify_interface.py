"""Check the current RevC assembly and its restored Final-Control overlay."""
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

LAYOUT = Path(__file__).resolve().parent
ROOT = LAYOUT.parents[1]
VERIFY = LAYOUT / "revision-audit/verify.py"


def main():
    if sys.argv[1:]:
        subprocess.run([sys.executable, VERIFY, *sys.argv[1:]], check=True)
        return

    with TemporaryDirectory(prefix="mira-final-control-") as directory:
        trial = Path(directory) / "Final-Control"
        subprocess.run(
            [sys.executable, LAYOUT / "MIRA-01.03.00/open-trial.py",
             LAYOUT / "final-control.sexpr.gz", trial],
            check=True,
            stdout=sys.stderr,
        )
        boards = [ROOT / f"MIRA_{name}/MIRA_{name}.kicad_pcb"
                  for name in ("Control", "Power", "Crossbar")]
        boards.append(trial / "MIRA_Control/MIRA_Control.kicad_pcb")
        subprocess.run([sys.executable, VERIFY, *boards], check=True)


if __name__ == "__main__":
    main()
