# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

MIRA is a hardware research platform for memristor arrays and neuromorphic computing. The "code" here is mostly **KiCad 10 projects** plus **Python verification and generation scripts** that check and edit those projects. There is no RTL, no firmware, and no app source. There is no build system, test framework, or linter. Verification means running scripts that use `kicad-cli` and `pcbnew` and comparing their output against recorded baselines.

Project documentation, reports, and commit-adjacent notes are written mostly in **Russian**. The root `README.md` and `CHANGELOG.md` are in English but describe the older RevA/RevB-era work. Write new review documents in Russian to match `hardware/MIRA_RevC/`.

## Revisions: which tree is current

- `hardware/MIRA_RevC/` is the **active design**, with three KiCad projects:
  - `MIRA_Control`: Zynq-7020 (PL+PS), PS DDR3L, FX20 USB-C bridge, 48 analog channels (3× DAC81416, 6× AD4696), masks and faults, forming circuits.
  - `MIRA_Power`: power rails and an STM32G0 supervisor.
  - `MIRA_Crossbar`: the replaceable adapter with the ICS-CQFP64 socket (J3).
  
  Start with `hardware/MIRA_RevC/START_RU.md` and `ARCHITECTURE_RU.md`.
- `hardware/MIRA_Control/`, `hardware/MIRA_Power/`, `docs/pcb-preparation/`, `scripts/`, and `fpga/digital-interfaces/` belong to the earlier RevA "MIRA.0x" schematic stages, which are history. `scripts/verify_*.py` hard-code paths into `hardware/MIRA_Control` and `docs/pcb-preparation/...` and do not apply to RevC.
- Within RevC, `review/prelayout`, `review/schematic-layout`, `review/layout/day1`, and older snapshots are also historical (see `START_RU.md`).

## Schematic sheet and reference conventions (RevC)

- Sheet files are numbered by hundreds (`1000_Zynq_DDR3L.kicad_sch`, `2200_CH00_03_Drive_and_Sense.kicad_sch`, …). Reference designators are short and sheet-based: the leading digits are the sheet number, with up to 99 parts per group (for example U701 and U1001; older docs use the longer form U70001). The mapping between old and new references, with UUIDs, is in `review/layout/reference-renumbering.csv`. The sheet index is `review/layout/reconciled/sheets.csv`.
- On committed `main`, the Crossbar socket is **U101** (ICS-CQFP64, footprint from the MemArdBoard project, not a manufacturer drawing). 50 of its 64 pins are wired: CH0–47, CASE and GND_REF, following the MemArdBoard 32×8 author map. The real die bondout, orientation key and 24×6 geometry are still unconfirmed. The untracked `review/layout/socket-trial/` (J3 all TBD, U1 as a "96-line logical boundary") is an older, never-committed state.
- Each project carries its own `sym-lib-table`/`fp-lib-table` with project-relative `libraries/`. Keep project folders intact. Shared 3D models live in `hardware/MIRA_RevC/libraries/3d`.

## Layout tooling architecture (`hardware/MIRA_RevC/review/layout/`)

These are milestone-scoped folders (`MIRA-01.01.00` … `MIRA-01.04.00`, `acceptance-01.03-01.04`, `acceptance-01.05-01.06`, `ddr-ch48-followup`, `revision-audit`, `socket-trial`). Each folder holds its own README, its tools, its CSV/JSON evidence, and its SVG/PNG renders. Key shared pieces:

- `sexpr_tools.py`: splices top-level KiCad S-expressions while keeping all untouched text **byte-for-byte**. Generator scripts rewrite only their own objects, and they use deterministic `uuid5` UUIDs (fixed namespace) so reruns are stable.
- `interface_spec.py` / `socket-trial/trial_spec.py`: the single source of truth for interface geometry, which other scripts import.
- **Final-Control** is an overlay, not a committed board. To build it, run `MIRA-01.03.00/open-trial.py final-control.sexpr.gz <new-dir>`, which writes a separate KiCad project from the working Control PCB plus the overlay. The routing trial lives there, and the working `MIRA_Control.kicad_pcb` holds only placement.
- **Guard rails**: `build_draft.py`, `update_interface_pcb.py`, `update_interface_schematics.py`, and `u1_constraints.py` deliberately `SystemExit` while the ICS socket footprint is present in the Crossbar PCB. Those are historical day-1 builders and would undo later work. Do not remove the guards. Use the `socket-trial/` tools instead.
- Checks run on **isolated copies in `/tmp`**, with `libraries/` symlinked, so they never touch the working `.kicad_pro` user settings. Preserve that pattern in any new check script.

### Running checks

KiCad 10.0.8 is installed system-wide from the PPA: `/usr/bin/kicad-cli`, and `pcbnew` imports in the system `/usr/bin/python3`. Scripts that need the CLI take its path as the first argument:

```bash
cd hardware/MIRA_RevC/review/layout
python3 socket-trial/check_trial.py /usr/bin/kicad-cli   # ERC/DRC before/after in /tmp copies → socket-trial/*.json, checks-summary.json
python3 check_schematics.py /usr/bin/kicad-cli           # ERC + XML netlist export → netlists/*.xml, *-after-erc.json
python3 socket-trial/verify_trial.py                     # pcbnew: socket trial invariants → geometry.json, connector-map.csv, verification.json
python3 verify_interface.py                              # pcbnew: materializes Final-Control in a temp dir, runs revision-audit/verify.py
python3 revision-audit/verify.py CONTROL POWER CROSSBAR FINAL [--before ×4]
python3 verify_fx23_drawings.py                          # Hirose FX23L footprint dimensions vs sources/ → footprint-drawing-audit.json
```

Known failures (as of 2026-11-20):
- `verify_fx23_drawings.py` passes. It finds the FX23L footprints by library ID and `PAIRS` position (pair A J5301↔J101, B J5302↔J102), not by reference.
- Text parsers must accept both S-expression layouts. Library files and script-written boards are single-line `(zone (layer …`. GUI-saved boards are multi-line `(zone\n\t(layer …`, and a save can reorder zones and outline vertices. Match heads with `re.match(r'\(zone\s', …)`, not `startswith('(zone ')`, and compare geometry order-independently. Cross-check against `pcbnew` before reporting a missing object.
- `socket-trial/verify_trial.py` compares `.kicad_pro` files with `socket-trial/before/` (the a1d7038 snapshot) as parsed JSON, so a KiCad re-save alone does not fail it. Control still fails on the 8 intentional HDI DRC rules from 8dbc304. Later asserts (Power PCB and Control footprint blocks byte-equal to `before/`, refs J1800/J1801) are also stale. `socket-trial/` is untracked. `kicad-cli pcb drc` text and JSON output caps unconnected items at 499; take full counts from the pcbnew `ratsnest` field of `verify_interface.py`.

Most of these **overwrite committed evidence files** in the repo. For a read-only check, copy `hardware/MIRA_RevC` elsewhere (keeping the `hardware/MIRA_RevC` path depth) and run the copies.

Direct CLI equivalents: `kicad-cli sch erc --format json -o out.json X.kicad_sch`, `kicad-cli pcb drc --format json -o out.json X.kicad_pcb`, and `kicad-cli sch export netlist --format kicadxml ...`.

Acceptance criteria used throughout: **ERC and DRC 0 errors**, schematic↔PCB parity, unchanged ratsnest totals (Control 6757, Power 2124 after the 2aa6b58 fuse-input fix — `review/layout/README.md` still says 2125, Crossbar 103, Final-Control 6594), and connector contact maps (`connector-map.csv`, 10 inter-board pairs). Check results are committed as JSON next to the tool that produced them.

## Repository conventions

- `.kicad_prl`, backups, `fp-info-cache`, and `__pycache__` are gitignored. KiCad and Markdown files use LF line endings. STEP, WRL, and PDF files are binary.
- Commit subjects often carry the task ID (`MIRA-01.0x.00 …`), followed by an imperative summary.
- Reports must keep a strict line between what was verified (ERC/DRC/static geometry) and what remains open (impedance with the fab stack-up, MIG/Vivado, firmware, bench validation). Do not claim hardware validation that has not happened.
- MIG/Vivado validation of FPGA↔DDR3L was explicitly **deferred by the user** and must be done before DDR3L routing is finalized.
