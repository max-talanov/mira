#!/usr/bin/env python3
"""Generate MIRA Samtec connector footprints and nominal 3D envelope models.

Sources and dimensions are recorded in docs/pcb-preparation/connectors-erc/README.md.
The models are project-created envelopes, not manufacturer detailed CAD models.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def num(v):
    return f'{v:.5f}'.rstrip('0').rstrip('.') or '0'


def box(x, y, z, sx, sy, sz, color):
    # KiCad VRML uses 0.1 inch units; model Y is opposite the footprint Y axis.
    position = ' '.join(num(v / 2.54) for v in [x, -y, z])
    size = ' '.join(num(v / 2.54) for v in [sx, sy, sz])
    return (f'Transform {{ translation {position} children [ Shape {{ '
            f'appearance Appearance {{ material Material {{ diffuseColor {color} }} }} '
            f'geometry Box {{ size {size} }} }} ] }}')


def build(project, series, rows):
    socket = series == 'SSW'
    part = f'{series}-1{rows:02d}-{"01" if socket else "07"}-S-D'
    name = f'Samtec_{part}_2x{rows:02d}_P2.54mm_Vertical'
    sign = -1 if socket else 1
    span = (rows - 1) * 2.54
    cx = sign * 1.27
    width = 4.95 if socket else 5.08
    length = rows * 2.54 + (.51 if socket else 0)
    height = 8.51 if socket else 2.54
    drill = 1.04 if socket else 1.02
    x1, x2 = cx - width / 2, cx + width / 2
    y1, y2 = span / 2 - length / 2, span / 2 + length / 2
    lib = ROOT / 'hardware' / f'MIRA_{project}' / 'libraries'
    fpdir = lib / 'MIRA_RevA.pretty'
    models = lib / 'MIRA_RevA.3dshapes'
    models.mkdir(exist_ok=True)
    model_name = part + '_Envelope.wrl'
    model = ['#VRML V2.0 utf8', '# MIRA nominal envelope; not manufacturer CAD.',
             box(cx, span / 2, height / 2, width, length, height,
                 '.07 .07 .07' if socket else '.82 .78 .62')]
    lines = [f'(footprint "{name}" (version 20241229) (generator "pcbnew")',
             '(layer "F.Cu") (attr through_hole)',
             f'(descr "Samtec {part}; 30uin gold contact/tin tail; mating orientation in connectors-erc report")',
             '(tags "Samtec MIRA board-to-board 2.54mm")',
             f'(fp_text reference "REF**" (at {num(cx)} {num(y1-2)}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))',
             f'(fp_text value "{part}" (at {num(cx)} {num(y2+2)}) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))']
    for layer, extra, stroke in [('F.Fab', 0, .1), ('F.SilkS', .15, .12), ('F.CrtYd', .75, .05)]:
        lines.append(f'(fp_rect (start {num(x1-extra)} {num(y1-extra)}) (end {num(x2+extra)} {num(y2+extra)}) '
                     f'(stroke (width {stroke}) (type default)) (fill none) (layer "{layer}"))')
    # Pin 1 indication is an assembly mark, not a claim of mechanical keying.
    marker_x = x2 + .55 if socket else x1 - .55
    tip_x = x2 + .2 if socket else x1 - .2
    lines.append(f'(fp_poly (pts (xy {num(tip_x)} 0) (xy {num(marker_x)} -.4) (xy {num(marker_x)} .4)) '
                 '(stroke (width .1) (type default)) (fill solid) (layer "F.SilkS"))')
    pads = []
    for row in range(rows):
        for col in range(2):
            pin = 2 * row + col + 1
            x, y = sign * col * 2.54, row * 2.54
            pads.append({'number':pin,'x_mm':round(x,4),'y_mm':round(y,4)})
            shape = 'rect' if pin == 1 else 'circle'
            lines.append(f'(pad "{pin}" thru_hole {shape} (at {num(x)} {num(y)}) '
                         f'(size 2 2) (drill {drill}) (layers "*.Cu" "*.Mask"))')
            if socket:
                model.append(box(x,y,-2.64/2,.79,.41,2.64,'.68 .68 .70'))
                model.append(box(x,y,8.515,.8,.8,.01,'.015 .015 .015'))
            else:
                model.append(box(x,y,-2.54/2,.635,.635,2.54,'.68 .68 .70'))
                model.append(box(x,y,2.54+5.84/2,.635,.635,5.84,'.78 .60 .20'))
    lines.append(f'(model "${{KIPRJMOD}}/libraries/MIRA_RevA.3dshapes/{model_name}" '
                 '(offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n)')
    (fpdir / (name + '.kicad_mod')).write_text('\n'.join(lines)+'\n')
    (models / model_name).write_text('\n'.join(model)+'\n')
    return {'project':project,'part':part,'footprint':name,'model':model_name,
            'body_mm':[round(width,4),round(length,4),height], 'drill_mm':drill,'pad_diameter_mm':2,
            'pads':pads,'planned_mount_side':'F.Cu' if socket else 'B.Cu'}


if __name__ == '__main__':
    assets = [build(project,series,n) for project,series in [('Power','SSW'),('Control','HTSW')] for n in [32,9]]
    out=ROOT/'docs/pcb-preparation/connectors-erc'
    out.mkdir(parents=True,exist_ok=True)
    (out/'connector-assets.json').write_text(json.dumps(assets,indent=2)+'\n')
    print('Generated four footprints and four nominal 3D envelope models.')
