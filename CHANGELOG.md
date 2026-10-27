# MIRA changelog

Repository milestones are separate from hardware revisions. Both projects currently use **RevA**.

## Unreleased

### 2026-10-27 — Power–Control inter-board review

- Record the 26 required inter-board nets and the observed pins of J400 and the relevant Power connectors.
- Document 3 P0 and 5 P1 open questions, each with evidence, a next action, and a closure criterion.
- Close the checklist item for documenting inter-board connections and discrepancies. Electrical corrections and fresh ERC runs remain open.
- Verify all 78 active schematic files against baseline commit `b457c20e4a20e0389fd8b2b06486e559891e3b48` and record their SHA-256 hashes.
- Update the root README to describe the populated 30-page Control project and link the review. No schematics, PCB files, or libraries are changed by this documentation update.

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
