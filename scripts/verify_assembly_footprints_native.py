#!/usr/bin/env python3
"""Read corrected footprints with KiCad pcbnew; no PCB or source modifications."""
from pathlib import Path
import json
import pcbnew as pcb
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/pcb-preparation/components-assembly/validation';LIB=ROOT/'hardware/MIRA_Control/libraries/MIRA_RevA.pretty'
parts={}
for name,count in [('Samtec_FTSH-105-01-L-DV-K_2x05_P1.27mm_SMD',10),('Wuerth_61300611121_1x06_P2.54mm_Vertical',6),('ICS-CQFP64-1830-1830-100-1',70)]:
 fp=pcb.FootprintLoad(str(LIB),name);assert fp is not None
 pads=[]
 for p in fp.Pads():
  pads.append(dict(number=p.GetNumber(),x_mm=pcb.ToMM(p.GetPosition().x),y_mm=pcb.ToMM(p.GetPosition().y),width_mm=pcb.ToMM(p.GetSize().x),height_mm=pcb.ToMM(p.GetSize().y),drill_mm=pcb.ToMM(p.GetDrillSize().x),attribute=int(p.GetAttribute()),paste=p.IsOnLayer(pcb.F_Paste)))
 assert len(pads)==count
 if name.startswith('Samtec_'):
  assert all(p['attribute']==pcb.PAD_ATTRIB_SMD and p['drill_mm']==0 and p['paste'] for p in pads)
 elif name.startswith('Wuerth_'):
  assert all(p['attribute']==pcb.PAD_ATTRIB_PTH and abs(p['drill_mm']-1.1)<1e-7 for p in pads)
 else:
  assert all(not p['paste'] for p in pads)
 parts[name]=pads
r=dict(engine=pcb.GetBuildVersion(),native_loading_passed=True,parts=parts,scope='Nominal geometry; does not certify socket drawing, mechanical tolerances, solder process or PCB placement.')
(OUT/'native-footprints.json').write_text(json.dumps(r,indent=2)+'\n');print('Native footprint validation: 3 footprints / 86 pads passed')
