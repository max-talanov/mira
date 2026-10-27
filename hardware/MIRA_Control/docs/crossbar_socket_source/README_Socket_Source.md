# ICS-CQFP64-1830-1830-100-1 socket footprint

The KiCad footprint was converted from the socket footprint in the original
MemArdBoard authors' public hardware project, rather than inferred from the
18.3 mm chip dimensions in the socket catalogue.

Source repository: https://github.com/ai-systems-lab/MemArdBoard

Pinned source revision: `540ae65eee1c722b8465fbbb46600562a5c2705d`

Author project archive:
https://github.com/ai-systems-lab/MemArdBoard/blob/540ae65eee1c722b8465fbbb46600562a5c2705d/commutatuin-board/schematic/ProPrj_UNO2FL32x8_COMM_pro_2026-06-11.epro

Gerber archive used for verification:
https://github.com/ai-systems-lab/MemArdBoard/blob/540ae65eee1c722b8465fbbb46600562a5c2705d/commutatuin-board/gerbers/Gerber_ISC_UNO_COMM_FLOOR.zip

The EasyEDA Pro `.epro` archive contains
`FOOTPRINT/c50c5847ddbc46caaf921c32459d483b.efoo` under the name
`ICS-CQFP64-1830-1830-100-1`. The board BOM identifies this socket as U10.
The unmodified footprint and original crossbar symbol are included here.
The repository's MIT license and copyright notice are preserved separately.

## Geometry and contact technology

- 64 circular copper contact lands, diameter 0.5 mm, 1.0 mm pitch.
- 16 contacts per side; opposing row centerlines are 21.0 mm apart.
- These lands are surface copper, not 0.5 mm plated holes. The original top
  copper Gerber has 64 flashes with a 0.5 mm circular aperture. None of these
  64 contacts occurs in the drill file.
- The original solder-mask openings are circles of diameter 0.602 mm. The
  KiCad footprint uses a 0.051 mm radial mask expansion to preserve them.
- Four NPTH mounting holes, diameter 2.1 mm, at X = +/-17 mm,
  Y = +/-19 mm.
- One NPTH locating hole, diameter 2.0 mm, at (-17, +12) mm.
- One NPTH locating hole, diameter 1.5 mm, at (+17, -12) mm.
- All coordinates in this note use KiCad's footprint view: X right,
  Y down. EasyEDA up-Y coordinates were inverted.
- Pad 1 is at (-10.5, -7.5) mm, pad 16 at (-10.5, +7.5) mm,
  pad 17 at (-7.5, +10.5) mm, pad 32 at (+7.5, +10.5) mm,
  pad 33 at (+10.5, +7.5) mm, pad 48 at (+10.5, -7.5) mm,
  pad 49 at (+7.5, -10.5) mm, pad 64 at (-7.5, -10.5) mm.

The original top silkscreen shows a 40 x 50 mm rounded rectangle with 2 mm
corner radii. This exact outline is preserved and repeated on F.Fab. The
source label OPEN is preserved at (-5.6, -16.8) mm. A pad-1 marker and a
41.5 x 51.5 mm courtyard have been added. The courtyard leaves at least
0.5 mm outside the source silkscreen stroke.

## Deliberate conversion choices and limits

The original Gerbers also contain solder-paste openings over the pressure
contact lands. The KiCad footprint intentionally has F.Cu and F.Mask only:
the 64 socket contacts are contact lands and do not receive solder paste.
The screw/locating holes are NPTH with zero additional mask expansion.

The footprint is an exact transfer of the published author PCB geometry
(rounded to 0.0001 mm), not an independently verified manufacturer drawing.
No manufacturer drawing defining socket body height, tolerance, lid travel,
open-lid swept area, or 3D model was found. The source outline is therefore
an author outline; it must not be treated as a certified manufacturer
mechanical envelope. No guessed lid keepout or 3D model is included.

The physical socket's pin-1 marker is not the same thing as the chip's
installation key. The author instruction photo explicitly warns that one
visible socket mark is not the chip key for this device. Use the instruction
photo and the intended chip documentation to orient the chip.

## Chip mapping in the author project

The socket footprint itself is generic contact 1..64. The original author
symbol supplies the following crossbar mapping:

| Signals | Physical contacts |
| --- | --- |
| BL0..BL15 | 64..49, descending |
| BL16..BL31 | 17..32, ascending |
| WL0..WL7 | 46, 45, 44, 43, 42, 41, 39, 38 |
| Net0..Net7 | 3..10, ascending |
| VCOM | 47 |

In the author PCB pad 47 is tied to GND. Contacts 40 and 48 are unconnected;
no CASE connection is established by this source. Do not infer other chip
pin functions from the socket alone.

## Manufacturer cross-check

https://icsocket.ru/ku/cqfp/489

https://icsocket.ru/ku/rus/987

The manufacturer lists 64 chip contacts, 1 mm chip pitch and 18.3 x 18.3 mm
chip body dimensions. Those are not socket PCB dimensions.
The manufacturer's catalogue lists compatibility with chip packages
5134.64-6, H18.64-2B and H18.64-1B, but no recommended PCB pattern.

## Conversion checks

`conversion_checks.json` records successful checks of all 64 unique contact
numbers, contact copper size and pitch, mask openings, six NPTH sizes, and
the transformed pad positions against the source board Gerbers. The largest
coordinate difference caused by removing the original mil rounding is less
than 0.00004 mm. KiCad loading and final project checks are performed with
the assembled MIRA project.

## Later MIRA visual model addition

The MIRA project now includes an explicitly approximate visual STEP model.
Its Z dimensions and latch are estimated; see `../CROSSBAR_SOCKET_3D.md`.
The physical contact and hole pattern is unchanged. The current courtyard
has extra front space for the approximate closed latch and therefore differs
from the initial 41.5 x 51.5 mm conversion described above.
