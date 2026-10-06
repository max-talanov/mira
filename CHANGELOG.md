# MIRA changelog

Repository milestones are separate from hardware revisions. Both projects currently use **RevA**.

## v0.2.0 — 2026-10-06

- Separate `hardware/MIRA_Power` and `hardware/MIRA_Control` projects.
- Replace the Control hierarchy scaffold with one empty A4 schematic and an empty PCB, retaining its local symbol, footprint, and STEP libraries.
- Update the root README with both projects, their current status, and opening instructions.
- Document milestone tags and retain `v0.1.0` on the original import.
- Add Git attributes for consistent KiCad text files and concise 3D model diffs.

This milestone describes repository organisation. Control circuitry, PCB routing, and hardware validation remain development work.

## v0.1.0 — 2026-10-06

- Import the MIRA RevA KiCad project and local libraries at commit `4b14a7e`.
- Mark the initial import with an annotated tag.
