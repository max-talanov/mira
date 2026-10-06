# Local MIRA Rev.A 3D model library

This empty KiCad starter includes 46 footprint-matched local STEP models. References use `${KIPRJMOD}/libraries/MIRA_RevA.3dshapes/`, without system-wide model dependencies. Model units are millimetres; the KiCad scale is 1:1.

`model_manifest.json` records original sources, filenames, SHA-256 checksums, transforms and mechanical scope. Symbols, footprints and STEP files are copied byte-for-byte from the separate MIRA Rev.A control project. Only common navigation and supply-boundary sheets are retained. No detailed circuit or board placement from that project is included.

## Model sources and scope

Most files are footprint-matched official KiCad packages3D models or the same local STEP files already present in the supplied MIRA project. KiCad model licensing notices remain inside the STEP headers; the upstream library license is included as `KICAD_3D_LICENSE.md`. Use the current manufacturer drawing as the authority for production dimensions, tolerances, contact plating and soldering conditions.

Four files ending in `_Drawing_Model.step` are generated nominal body/contact models, because their exact footprint model was absent from the official KiCad repository:

| Footprint | Drawing geometry represented | Scope |
| --- | --- | --- |
| HD3SS3220 RNH30 | 2.5 × 4.5 mm body; 0.8 mm maximum height; 30 nominal terminals; 1.2 × 3.2 mm exposed pad | TI RNH0030A / 4221819/B. Body draft and lead fillets omitted. |
| Winbond WSON8 | 8 × 6 × 0.75 mm nominal package; 0.02 mm body standoff; eight 0.50 × 0.40 mm terminals; 3.4 × 4.3 mm exposed metal | W25Q512JV package E. Nominal dimensions only. |
| Micron TW FBGA96 | 8 × 14 mm package; 1.1 mm nominal total height; exact sparse 96-ball arrangement; 0.47 mm post-reflow balls; 0.34 mm standoff | Micron 4Gb DDR3L Rev.R, figure 13. Ball deformation and substrate/overmold details simplified. |
| SiTime SiT9121 | 3.2 × 2.5 × 0.75 mm package with six nominal terminals, oriented to the footprint | SiT9121 Rev.1.09 dimension drawing. Lid seam and marking simplified. |

These four models support placement and package-envelope review. They are not manufacturer-certified mechanical models and do not establish worst-case assembly tolerances.

## Pulse H5007NL

The manufacturer STEP from `H5007NL_3D.zip` is retained unchanged. The footprint applies a Z offset of −3.03302244 mm to put its lowest lead seating point on the PCB top plane. Pin 1 marking and the 24-lead X pitch align with the footprint.

The manufacturer CAD dated 2018-03-14 and the HC500.T drawing dated 2020-06 disagree on the moulded body length. The STEP overall bounding box is 18.288 × 15.875 × 5.625481 mm, and its body side faces reach X = ±9.144 mm. The newer drawing gives nominal body 17.526 × 12.192 mm, overall lead span 16.002 mm and height 5.715 mm. The footprint courtyard conservatively covers the longer CAD. Use the current drawing, not the legacy CAD, for production body limits.

The new local footprint uses the manufacturer's suggested lands: 0.762 × 1.905 mm pads, 1.27 mm pitch and 14.605 mm row-centre spacing. Adjacent-pad copper clearance is 0.508 mm. This library retains those corrected lands.

Source: https://productfinder.pulseeng.com/product/H5007NLT

## Amphenol RJE71-188-1412

The RJE71-188-1412 library component is a plain CAT6 shielded 8P8C jack with LEDs. It requires external magnetics when used for Ethernet.

The manufacturer's RJE71-188-1XXX family STEP is rigidly rotated and translated into the new footprint's coordinate system. Its body frame is 16.90 × 20.70 mm and its top is aligned to the drawing's 8.55 mm height above the PCB. The family CAD does not establish suffix-specific tail dimensions or individual contact tolerances. Suffix 1412 has nominal 2.27 mm tails and 1.57 mm recommended board thickness in the drawing.

**This is a sink-PCB connector.** Part of the body extends below the PCB top plane. Merge the footprint's open U contour on `Dwgs.User` into the actual PCB outline during layout. A rectangular board without that opening is unsuitable for this connector. Confirm the board edge and enclosure cutout using the current connector drawing before manufacture.

Sources:
- https://www.amphenol-cs.com/product/rje711881411.html (same family; suffix 1412 is specified in the linked drawing)
- https://cdn.amphenol-cs.com/media/wysiwyg/files/drawing/rje711881xxx.pdf
- https://cdn.amphenol-cs.com/media/wysiwyg/files/3d/srje711881xxx.zip
