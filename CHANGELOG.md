# MIRA changelog

Repository milestones are separate from hardware revisions. Both projects currently use **RevA**.

## Unreleased

### 2026-10-28 — Connector selection and VSS ERC correction

- Assign SSW-132-01-S-D / HTSW-132-07-S-D and SSW-109-01-S-D / HTSW-109-07-S-D to the existing 64- and 18-contact inter-board interfaces. Add local footprints, nominal 3D envelope models, mating pinout, BOM and a proposed 12 mm board stack.
- Rename negative analog supply pins VSS_NEG in six local symbol definitions and active schematic copies, preserving pin numbers, power-input types and all electrical connectivity. Remove all 32 previous VSS exclusions and resolve the two remaining active messages.
- Verify zero ERC errors, warnings and exclusions in both projects. Re-enable footprint-filter and simulation-model checks; retain and disclose the two existing ignored style checks.
- Verify all 82 mating contacts, 34 negative-supply pins and 6850 connected pin entries against the high-load baseline. PCB placement, routing, mechanical and thermal qualification remain pending.

### 2026-10-28 — High-load schematic candidate

- Include the earlier ERC/interface corrections: U1903 feedback, Power 4900 inter-board interface, reset and host status paths.
- Add supplemental CORE contacts and positive remote sense with a local fallback path; retain the existing 64-pin map.
- Replace the N15 inverting converter with TEN 30-2413WIN and a default-OFF remote driver; coordinate its current-trip divider for the provisional load target.
- Change the input OVP divider and specify the candidate continuous input range as 18–30 V at nominal 24 V.
- Add local library assets, reproducible connectivity/DC checks, ERC reports and a report of remaining hardware validation. No PCB routing, GitHub publication or hardware qualification is claimed.

### 2026-10-27 — Initial ERC report review

- Preserve user-generated Control and Power ERC reports byte-for-byte: 4 errors / 118 warnings and 11 errors / 13 warnings respectively.
- Group all 146 messages into six cause groups and add a seventh question for report provenance and check coverage, each with priority, next action, and closure criterion.
- Identify the two U1903 feedback joins as the first Control correction to verify; document Power source-model checks, the unresolved GND flag, off-grid objects, VSS warnings, and hidden power-pin aliases.
- Record report hashes and all messages. Close the report-documentation checklist item while keeping schematic corrections and the report-to-source revision match open.
- Update the shared issue list and project status. No schematics, PCB files, or libraries are changed.

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
