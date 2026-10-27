# Crossbar socket: J2801

The local symbol `MIRA_RevA:ICS_CQFP64_1830_1830_100_1_MIRA`
replaces the generic 2x32 header on sheet
`2800_MATRIX_CROSSBAR_SOCKET_AND_BIAS.kicad_sch`.
J2801A and J2801B are two schematic units of one physical socket.
Both use `MIRA_RevA:ICS-CQFP64-1830-1830-100-1`.
All 64 physical contact numbers are present. Existing schematic placement,
reference, instance UUIDs, and BL/WL/NL connections are preserved.

## Electrical reference

Pin functions follow the user's supplied crossbar pin-map image from July 2026.
The complete correspondence is in `CROSSBAR_SOCKET_PIN_MAP.csv`.

- 3-10: NL0-NL7.
- 17-32: BL16-BL31.
- 49-64: BL15-BL0.
- WL0-WL7: 46, 45, 44, 43, 42, 41, 39, 38.
- 40: CASE_COM; connected to the existing MAT_ADAPTER_CASE bias selector.
- 48: GND in the user reference; connected to the existing configurable
  MAT_ADAPTER_VSUB network. The symbol calls this contact GND_REF.
- 1, 2, 11-16, 33-37, 47: no connect in the user reference.

The previous generic adapter had CASE and VSUB assigned to 48 and 40.
These two net associations have been corrected to follow the user reference.
Existing independent bias selectors and their resistors are retained.
Select GND on both selectors for the reference connection. The supplied source
does not independently establish that pin 48 is the semiconductor substrate,
or that applying a nonzero bias to pin 48 or CASE is allowed.

The MemArdBoard repository is used as a mechanical source only. Its later
electrical schematic uses a different common-contact assignment (47 VCOM/GND;
40 and 48 unused). That mapping has NOT been substituted for the user's
crossbar pin map. Confirm the sample revision before fitting the actual array.

## Mechanical source

Source: https://github.com/ai-systems-lab/MemArdBoard

Pinned revision: `540ae65eee1c722b8465fbbb46600562a5c2705d`.

The footprint was converted from:

`commutatuin-board/schematic/ProPrj_UNO2FL32x8_COMM_pro_2026-06-11/FOOTPRINT/c50c5847ddbc46caaf921c32459d483b.efoo`

Coordinates were checked against the published board's copper, solder mask,
silkscreen and nonplated drill outputs. EasyEDA's Y coordinate was inverted
for KiCad. Pin numbering was preserved.

| Feature | KiCad geometry |
| --- | --- |
| Contacts | 64 circular surface contact lands, diameter 0.50 mm |
| Contact pitch | 1.00 mm |
| Opposite contact row centers | 21.00 mm |
| Solder mask | 0.051 mm radial expansion, 0.602 mm opening |
| Main mounting holes | Four NPTH, diameter 2.10 mm, at X = +/-17 mm, Y = +/-19 mm |
| Auxiliary hole | NPTH, diameter 2.00 mm, at X = -17 mm, Y = +12 mm |
| Auxiliary hole | NPTH, diameter 1.50 mm, at X = +17 mm, Y = -12 mm |
| Reference outline | 40 x 50 mm, corner radius 2 mm |
| Courtyard | X = -20.75 to +20.75 mm; Y = -31.5 to +25.75 mm; front margin estimated from the 3D latch |

These are pressure-contact lands, not 64 signal-drill holes. Paste apertures
are omitted: solder paste is not required on a pressure-contact landing.
The source's published paste layer did include the same contact circles;
this is the one intentional manufacturing-layer deviation in the conversion.
The outline and OPEN indication follow the author layout. An approximate visual STEP model has now been added; see
`CROSSBAR_SOCKET_3D.md`. The courtyard front was enlarged to cover its
estimated closed latch. Contact and hole geometry are unchanged. No certified
open-lid swept clearance is defined.

This is an author-board-derived footprint, not a manufacturer-certified
mechanical drawing. Check the purchased socket's revision, pins, mounting
holes and lid access against the footprint before ordering the PCB.

Manufacturer reference: https://icsocket.ru/ku/cqfp/489
The manufacturer's public page states 64 contacts, 1 mm IC contact pitch and
18.3 x 18.3 mm IC body. Those IC dimensions were not used as the socket's
PCB outline or mounting-hole dimensions.

The original footprint, contact-coordinate table, and upstream MIT license
are retained under `crossbar_socket_source/`.

The pad-1 marker denotes PCB contact numbering. It is not a verified chip
installation key. The author warns that the visible mark on the socket
housing is not the chip installation key; check the chip pin-map orientation
and continuity before insertion.
