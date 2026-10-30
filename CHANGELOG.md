# MIRA changelog

## 2026-10-30 — Architecture Atlas 4.3 distribution

- Add the original, unchanged `MIRA_Architecture_Atlas_4.3.zip` under `docs/architecture-atlas/`, with a direct download link and Russian opening instructions in the repository README.
- Document offline startup through `index.html`, presentation mode, and the speaker guide. Keep the atlas's earlier schematic snapshot separate from the current `hardware/` projects.
- Verify ZIP integrity, all 273 script/style dependencies, functional data, and navigation using the bundled validators. The archive is preserved byte for byte; no hardware files are changed.

## 2026-10-30 — MIRA.05 analog requirements

- Define separate READ, SET, RESET and FORMING source-voltage/current profiles, concurrency, provisional load limits and command windows. Distinguish these engineering limits from unknown DUT ratings.
- Replace U2109 INA821 with INA149AIDR and its actual SOIC-8 pin map; sense buffered command for anti-windup. Preserve all other pin connectivity.
- Change R2111 to 10 kOhm; nominal command ceiling 10.05 V. Set the local P15 qualifier to 1 MOhm / 31.6 kOhm, 0.1%, 0603; nominal falling threshold 13.22 V.
- Preserve intervening R2115/R2116 100k/101k CV compensation, R2104 0603 MPN and five Panasonic ERJ metadata fixes (12 component records total).
- Correct switch-family, ADC blanking, discharge and over-current notes. Preserve the earlier MIRA.04 and v6 repairs and all Power circuitry.
- Pass 43 analog checks, 1650 digital and 1404 v6 checks, seven other historical regression scripts, and native ERC on Control (43 sheets) / Power (61 sheets), zero errors and warnings.
- Add a Russian report, changed-sheet PDF, numeric tables, disabled matrix-profile template and explicit bench/model acceptance criteria. No firmware, PCB, peak-current or pulse-timing qualification is claimed. MIG/Vivado remains deferred until before DDR3L routing.

## 2026-10-30 — MIRA.04 digital interface review

- User decision: defer MIG/Vivado validation until before routing FPGA-to-DDR3L on Control and before freezing the FPGA pinout. The user is closing the current MIRA.04 card as a schematic milestone; MIG validation remains an open pre-routing requirement.

- Move MCU-to-FPGA SPI SCK from U500.AB12 to Y11 (SRCC, bank 13); release AB12.
- Verify exact FPGA/MCU/DDR3L/SDRAM pin functions, 39 FMC paths and 56 STM32 alternate functions.
- Add pin maps, candidate XDC, exact MIG input settings and Vivado project preparation scripts.
- Pass 1650 static checks and historical regressions; KiCad ERC remains 0 errors / 0 warnings on both projects.
- MIG/Vivado was not available: DDR validation, generated MIG project and implementation/timing reports remain open. No PCB, firmware or hardware-test claim.

## 2026-10-30 — Unpowered-input review / partial hardware repair

- Add AON-powered Ioff Schmitt receivers for host reset and host UART RX on Power 5500 (7 parts; 3 legacy pin changes).
- Keep Control pin connectivity unchanged and preserve startup / sequencing / fault behavior.
- Record open analog back-power paths and an exact 190-row input/clamp inventory. This checklist item is not closed.
- KiCad 10.0.8, Power 55 sheets / Control 32; no ERC errors or warnings. No firmware, PCB or board-test claim.


Repository milestones are separate from hardware revisions. Both projects currently use **RevA**.

## Unreleased

### 2026-10-29 — Fault hardware repair

- Add Power sheet 5400: application heartbeat timeout, first-edge readiness latch and open-drain host-watchdog reset. Add LINK_READY_H to matrix clear and PM PC15.
- Preserve the 118-contact pinout and all Control electrical connections; update heartbeat semantics on Control sheets 300/900. Add 14 Power components.
- Verify 112 fault-hardware checks, 173 fault-path checks across 30 scenarios, 134 startup checks, 179 sequencing checks and 21 power-path checks. ERC: zero messages, Power 54 sheets / Control 32.
- Firmware integration, PCB placement, supply ramps, fault timing, discharge and unpowered-input tests remain pending.

### 2026-10-29 — Startup and PM sequencing

- Qualify AON startup, block all 15 rail commands and MATRIX_PERMIT until ready, require fresh ARM after a detected fault, and replace the VTT source follower with a full-swing buffered drive.
- Add GLOBAL_CLEAR_N feedback to PC14 / U2401.4 on Power sheet 2400; keep low-voltage READY fanout unchanged. Document every EN/PG pin, parent dependency, sequencing and fault response for PM firmware.
- Preserve the 118-contact inter-board interface and Control sources. Verify 134 startup checks, 178 native connectivity/Boolean sequencing checks, zero ERC messages on 53 Power and 32 Control sheets, and the earlier 21 power-path checks.
- No PM/FPGA firmware implementation, PCB routing, GitHub publication or hardware timing qualification is claimed.


### 2026-10-28 — Task 1/2 documentation refresh

- Synchronize the task review, ERC resolution table, inter-board pinout, current XLSX/JSON budget and ready-to-post task comments with hardware commit `52f4386`; preserve the previous documents and workbook as history.
- Apply a 30% margin to provisional peak loads, model TEN 30-2413WIN losses separately, refresh capacitances from native netlists and replace the obsolete central-connector calculation with 27 zone/rail branches and the CORE sense model.
- Record unresolved N15 startup/OCP and IO3V3 current-distribution cases explicitly. Do not claim final load capacity, completed PCB layout or GitHub publication.
- Add an independent budget verification script and GitHub publication instructions. This documentation refresh does not alter hardware sources.

### 2026-10-28 — Distributed local power entries

- Replace the central 64-contact interface with seven local power entries for FPGA, DDR, MCU, USB, Ethernet, DAC/matrix and ADC/AFE, plus a separate 20-contact supervision interface. Update both boards together; this pinout supersedes the previous connector candidate.
- Assign all eight Samtec SSW/HTSW pairs and add four hierarchy leaves, zone-specific symbols, 14 unique local footprints/models, BOM, mating pinout and placement requirements. Retain the proposed 12 mm facing-surface gap; PCB coordinates and routing remain pending.
- Preserve all 6686 connected pin entries outside the replaced connectors, including power converters, protection, analog negative supplies and CORE positive sense. Verify all 118 mating contacts, zero ERC violations/exclusions under the documented check set, and 21 power-path/value assertions.
- Account for provisional FPGA AUX/IO return current in the conditional CORE DC calculation. Do not claim hardware load capacity, thermal qualification or a completed mechanical stack.

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
