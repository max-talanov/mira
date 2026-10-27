# Socket 3D model: approximate visual representation

The footprint now links the closed model:

`${KIPRJMOD}/libraries/MIRA_RevA.3dshapes/ICS-CQFP64-1830-1830-100-1_APPROX.step`

An optional illustrative open model is also included:

`ICS-CQFP64-1830-1830-100-1_APPROX_OPEN.step`

To view the open model, temporarily select that file in the footprint's 3D
Models tab. Both models use scale 1, rotation 0 and offset 0. Only the closed
model is enabled by default. The project's empty PCB is not populated.

## What is confirmed

The original authors' EasyEDA project and Gerber outputs define 64 surface
copper lands of diameter 0.50 mm on a 1.00 mm pitch, with 21.00 mm opposing
row spacing. They do not contain 64 corresponding signal drills. A pressure
contact interface is consistent with this geometry and the photographed
mechanically fixed socket; the internal spring design is not documented.

Four NPTH mounting holes of diameter 2.10 mm and two asymmetric NPTH holes
of diameter 2.00 and 1.50 mm are transferred exactly. The latter probably
serve for location, but that function is inferred. The 40 x 50 mm R2 outline
is the author PCB outline; it is not a certified manufacturer envelope.

The model's 64 lower contact centers and all six hole centers/diameters
match this footprint. PCB contact plane is Z=0; STEP Y is minus footprint Y.

## What is approximate

No manufacturer STEP model or dimensioned assembly drawing was found.
The author project's own 3D fields are empty. The visual design follows
the gold-colored metal socket with a circular cover opening in the user's
`Доклад_Щаников_1.pdf`, page 15. Another author photo shows a black exterior;
that may be a different construction or revision of the socket family.

All vertical dimensions, cover size, circular opening, latch, hinge,
pressure insert, screw heads and internal contact shapes are estimates.
They make the model recognizable but must not be used to manufacture the
socket or determine final enclosure/stacking clearances.

The estimated closed model occupies X=-20..+20 mm, CAD Y=-25..+30.95 mm,
Z=0..11.2 mm. This 11.2 mm height is a modeling choice, not a datasheet value.
The open model uses an illustrative 105-degree opening angle and reaches
about 45.8 mm in height. Neither the angle nor this envelope is confirmed.

The latch is on the footprint's OPEN / -Y side and the hinge is opposite.
Because the photographed latch protrudes beyond the frame, the provisional
closed courtyard front was enlarged to footprint Y=-31.5 mm. Its remaining
limits are X=+/-20.75 mm and Y=+25.75 mm. This is a layout margin based on the
approximate model, not a manufacturer's recommended keepout. The original
copper, solder-mask openings, 64 pin numbers and six holes remain unchanged.

Pad 1 marks PCB contact numbering. It is not a certified chip insertion key;
the author's instruction photo warns against using one visible housing mark
as the key. Check the chip pin map and sample revision before insertion.

## Files and validation

`crossbar_socket_source/3D_MODEL_CHECKS.json` records STEP geometry validity,
solid count, bounding boxes and the exact/estimated dimension categories.
Both STEP files were imported again with Open CASCADE after export.

The rebuild source is `models/build_crossbar_socket_3d.py` (CadQuery 2.7).
It regenerates the STEP models, not the footprint electrical geometry.

Mechanical source: https://github.com/ai-systems-lab/MemArdBoard

Manufacturer reference: https://icsocket.ru/ku/cqfp/489

Before ordering the PCB or an enclosure, compare the actual purchased socket
against its PCB contact pattern, fasteners, closed height and lid clearance.
