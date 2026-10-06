# MIRA Control — empty KiCad project

Open **MIRA_Control.kicad_pro**. The project contains one blank A4 schematic and an empty PCB. It is intended for building MIRA Control Rev.A from scratch.

## Local library

Keep the complete folder together. Both library tables use the nickname `MIRA_RevA` and project-relative paths. No global library installation is required.

- 151 unique symbols: the original ICs, connectors and passive variants, plus 16 ready-to-place 0201 capacitor/resistor variants with Value, MPN, Manufacturer, Footprint, Datasheet and Description filled in. One identical 10k resistor entry was removed.
- 48 local footprints and 48 local STEP models, including C/R 0201.
- 0201 body size is 0.6 x 0.3 mm; local copper-pad gap is 0.22 mm.
- The generic Capacitor and Resistor symbols remain generic; select the appropriate filled variant when an ordering part is known. Larger and precision variants are retained for suitable circuits.

`docs/PASSIVES_0201.csv` lists the 16 new 0201 choices. The 100n 16V part is X7S; retain the original X7R/other suitable variant when capacitance tolerance is important, including USB coupling. `docs/models/` contains model source and license records.

## Project settings

Minimum copper clearance and Default netclass clearance are 0.2 mm. Existing generic board defaults are retained; no finished layer stack, outline, net assignments or circuit is defined.

## Repository placement

Place the complete **MIRA_Control/** folder under **hardware/** in the existing MIRA repository. Commit the .kicad_pro, .kicad_sch, .kicad_pcb, both library tables, libraries/ and docs/ together. The included .gitignore excludes local preferences, locks, autosave and backup files.
