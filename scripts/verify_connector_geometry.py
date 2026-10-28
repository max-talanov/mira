#!/usr/bin/env python3
"""Check native KiCad mating geometry; optionally render nominal model fixtures.

Run with a Python interpreter containing KiCad's pcbnew module, for example:
  /usr/bin/python3 scripts/verify_connector_geometry.py --render-fixture
No project PCB is modified. The rendered board is only a model-loading fixture.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile
import pcbnew as pcb

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/pcb-preparation/distributed-power'


def library(project):
    return ROOT/'hardware'/f'MIRA_{project}'/'libraries'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render-fixture',action='store_true')
    args=parser.parse_args()
    spec=json.loads((OUT/'interface.json').read_text())
    assets=json.loads((OUT/'connector-assets.json').read_text())
    check_board=pcb.BOARD()
    count=0
    for a in spec['connectors']:
        pad_maps=[]
        for project in ['Power','Control']:
            part=a[project+'_part']
            name=f'Samtec_{part}_2x{a["rows"]:02d}_P2.54mm_Vertical'
            fp=pcb.FootprintLoad(str(library(project)/'MIRA_RevA.pretty'),name)
            assert fp is not None
            # Flip accesses the parent board's settings; never flip an unowned footprint.
            check_board.Add(fp)
            fp.SetPosition(pcb.VECTOR2I(0,0))
            if project=='Control':
                fp.Flip(pcb.VECTOR2I(0,0),pcb.FLIP_DIRECTION_LEFT_RIGHT)
                assert fp.GetLayer()==pcb.B_Cu
            pad_maps.append({p.GetNumber():(p.GetPosition().x,p.GetPosition().y) for p in fp.Pads()})
        assert pad_maps[0]==pad_maps[1],a['zone']
        count+=len(pad_maps[0])
    result={'engine':'KiCad pcbnew '+pcb.GetBuildVersion(),
            'control_flip':'FLIP_DIRECTION_LEFT_RIGHT around pad 1',
            'all_mated_pad_coordinates_match':True,'mated_contacts_checked':count,
            'scope':'Nominal footprint geometry only, not mechanical tolerance or final PCB placement'}
    (OUT/'validation/native-mating-geometry.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
    if not args.render_fixture:
        return

    board=pcb.BOARD()
    rows=sorted({a['rows'] for a in spec['connectors']})
    for a in assets:
        n=len(a['pads'])//2
        fp=pcb.FootprintLoad(str(library(a['project'])/'MIRA_RevA.pretty'),a['footprint'])
        assert fp is not None
        x=12+rows.index(n)*14;y=12 if a['project']=='Power' else 58
        fp.SetReference(a['part'].split('-')[0]+'-'+str(n));fp.SetValue(a['part'])
        fp.SetPosition(pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y)))
        board.Add(fp)
    outline=pcb.PCB_SHAPE(board);outline.SetShape(pcb.SHAPE_T_RECT)
    outline.SetStart(pcb.VECTOR2I(pcb.FromMM(3),pcb.FromMM(3)))
    outline.SetEnd(pcb.VECTOR2I(pcb.FromMM(106),pcb.FromMM(98)))
    outline.SetLayer(pcb.Edge_Cuts);outline.SetWidth(pcb.FromMM(.05));board.Add(outline)
    with tempfile.TemporaryDirectory(prefix='mira-model-fixture-') as td:
        path=Path(td)/'fixture.kicad_pcb';pcb.SaveBoard(str(path),board)
        def absolute_model(match):
            filename=match[1];project='Control' if filename.startswith('HTSW') else 'Power'
            return '(model "'+str(library(project)/'MIRA_RevA.3dshapes'/filename)+'"'
        source=re.sub(r'\(model "\$\{KIPRJMOD\}/libraries/MIRA_RevA.3dshapes/([^"]+)"',absolute_model,path.read_text())
        path.write_text(source)
        subprocess.run(['kicad-cli','pcb','render','--width','1400','--height','1200','--rotate','325,0,25',
                        '--zoom','.85','--background','opaque','--quality','basic','-o',
                        str(OUT/'validation/connector-envelopes-fixture.png'),str(path)],check=True,capture_output=True,text=True)
    print('Rendered all 14 nominal models on a temporary test fixture.')


if __name__=='__main__':
    main()
