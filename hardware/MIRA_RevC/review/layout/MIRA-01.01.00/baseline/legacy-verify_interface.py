"""Verify actual saved PCB + fresh KiCad XML exports. Run with KiCad pcbnew Python."""
from pathlib import Path as _GuardPath
import subprocess as _trial_subprocess, sys as _trial_sys
_trial_here=_GuardPath(__file__).resolve().parent
if '"MIRA_Module:ICS-CQFP64-1830-1830-100-1"' in (_trial_here.parents[1]/'MIRA_Crossbar/MIRA_Crossbar.kicad_pcb').read_text():
 _trial_subprocess.run([_trial_sys.executable,str(_trial_here/'socket-trial/verify_trial.py')],check=True)
 raise SystemExit(0)

import pcbnew as p,csv,json,xml.etree.ElementTree as ET,hashlib,math
from collections import Counter
from interface_spec import BASE,OUT,PAIRS,pinout,POWER_PINS,MOUNTS,KEY
from sexpr_tools import children,reference

def xy(q):return [round(p.ToMM(q.x),6),round(p.ToMM(q.y),6)]
def foot(b,r):return next(f for f in b.GetFootprints() if f.GetReference()==r)
def netlist(n):
 tree=ET.parse(OUT/'netlists'/f'{n}.xml');nodes={};types={};components={c.get('ref'):c for c in tree.findall('./components/comp')}
 for net in tree.findall('./nets/net'):
  for node in net:nodes[node.get('ref'),node.get('pin')]=net.get('name');types[node.get('ref'),node.get('pin')]=node.get('pintype','')
 return nodes,types,components

def original(n):
 path=OUT/'day1'/f'{n}.xml';tree=ET.parse(path);return {(node.get('ref'),node.get('pin')):net.get('name') for net in tree.findall('./nets/net') for node in net}
boards={n:p.LoadBoard(str(BASE/f'MIRA_{n}/MIRA_{n}.kicad_pcb')) for n in ['Control','Power','Crossbar']}
c,w,m=[boards[n] for n in ['Control','Power','Crossbar']]
cn,ct,cc=netlist('control');mn,mt,mc=netlist('module')
# Full unchanged electrical assignments on all other Control components, independent of PCB source comparison.
old=original('Control');assert {k:v for k,v in cn.items() if k[0] not in ['J1800','J1801']}=={k:v for k,v in old.items() if k[0]!='J1800'}
# Preserve untouched footprints byte-for-byte relative to the user's local day1, not git HEAD.
for n,excluded in [('Control',{'J1800','J1801','H1800','H1801','H1802'}),('Crossbar',{'J1','J2','H1','H2','H3'})]:
 def bodies(s):return {reference(t):t for _,_,t in children(s) if t.startswith('(footprint ') and reference(t) not in excluded}
 assert bodies((BASE/f'MIRA_{n}/MIRA_{n}.kicad_pcb').read_text())==bodies((OUT/'day1'/f'MIRA_{n}.kicad_pcb').read_text())
assert (BASE/'MIRA_Power/MIRA_Power.kicad_pcb').read_bytes()==(OUT/'day1/MIRA_Power.kicad_pcb').read_bytes()
# Every electrically numbered PCB pad must match its schematic net. Board-only holes are unnumbered.
for b,nodes,label in [(c,cn,'Control'),(m,mn,'Crossbar')]:
 for f in b.GetFootprints():
  if f.GetAttributes()&p.FP_BOARD_ONLY:continue
  for a in f.Pads():
   k=(f.GetReference(),a.GetNumber())
   if a.GetNumber():assert a.GetNetname()==nodes.get(k,''),(label,k,a.GetNetname(),nodes.get(k))
rows=[];detail=[];seen=[]
def half(b,r):
 f=foot(b,r);pos=xy(f.GetPosition());a={a.GetNumber():a for a in f.Pads() if a.GetNumber()};points={k:xy(a[k].GetPosition()) for k in ['1','2','3']};one=points['1'];two=points['2'];three=points['3']
 return {'ref':r,'pcb_x':pos[0],'pcb_y':pos[1],'pcb_angle':f.GetOrientationDegrees(),'pcb_side':f.GetLayerName(),'common_x':pos[0],'common_y':pos[1],'common_angle':f.GetOrientationDegrees(),'common_side':'down (-Z)' if f.GetLayer()==p.B_Cu else 'up (+Z)','pin1_x':one[0],'pin1_y':one[1],'pin1_orientation':f'datum->1 ({one[0]-pos[0]:.3f},{one[1]-pos[1]:.3f}); 1->2 ({two[0]-one[0]:.3f},{two[1]-one[1]:.3f}); 1->3 ({three[0]-one[0]:.3f},{three[1]-one[1]:.3f})','points':points}
for i in range(10):
 pair=None if i<8 else PAIRS[i-8];ar=f'J{400+i}' if i<8 else pair['control'];br=f'J{4901+i}' if i<8 else pair['module'];other=w if i<8 else m
 A=half(c,ar);B=half(other,br);fa,fb=foot(c,ar),foot(other,br);pa={a.GetNumber():a for a in fa.Pads() if a.GetNumber()};pb={a.GetNumber():a for a in fb.Pads() if a.GetNumber()}
 if i<8:
  assert set(pa)==set(pb)
  for pin in pa:
   assert xy(pa[pin].GetPosition())==xy(pb[pin].GetPosition())
   expected='CORE_SENSE_P' if (ar,pin)==('J401','17') else pa[pin].GetNetname();assert pb[pin].GetNetname()==expected
 else:
  assert xy(fa.GetPosition())==xy(fb.GetPosition())==[pair['x'],pair['y']]
  assert fa.GetLayer()==p.F_Cu and fb.GetLayer()==p.B_Cu
  mapping=pinout(pair['pair']);assert set(mapping)==set(pa)==set(pb)
  assert sum(mapping[str(n)]=='GND' for n in range(1,81))==22
  assert sum(mapping[str(n)]=='NC' for n in range(1,81))==10
  for pin,net in mapping.items():
   # Numbering/geometric chirality: independent check against catalogue dimensions.
   ax,ay=xy(pa[pin].GetPosition());bx,by=xy(pb[pin].GetPosition())
   if pin.isdigit():
    k=int(pin);x=-9.75+((k-1)%40)*.5;sign=-1 if k<=40 else 1
    assert [ax,ay]==[pair['x']+x,pair['y']+sign*4.75]
    assert [bx,by]==[pair['x']+x,pair['y']+sign*3.15]
    assert xy(pa[pin].GetSize())==[.3,1.8] and xy(pb[pin].GetSize())==[.3,1.9]
   else:
    assert ax==bx and abs(abs(ay-by)-2.3)<1e-6
    assert xy(pa[pin].GetSize())==xy(pb[pin].GetSize())==[1.6,1.6]
    assert xy(pa[pin].GetDrillSize())==xy(pb[pin].GetDrillSize())==[1.2,1.2]
   if net=='NC':
    assert 'no_connect' in ct[ar,pin] and 'no_connect' in mt[br,pin]
    assert cn[ar,pin].startswith('unconnected-') and mn[br,pin].startswith('unconnected-')
   else:
    assert cn[ar,pin]==mn[br,pin]==net
    if net!='GND':assert mn['U1',net]==net;seen.append(net)
 for pin in ['1','2','3']:detail.append({'pair':i+1,'pin':pin,'control':A['points'][pin],'mate':B['points'][pin]})
 record={'pair':i+1,'status':'all contacts coincide' if i<8 else 'FX23L '+pair['pair']+' axes coincide; H=8mm; tail offset 1.6mm / power2.3mm'}
 for prefix,h in [('control',A),('mate',B)]:
  for k,val in h.items():
   if k!='points':record[prefix+'_'+k]=val
 rows.append(record)
assert Counter(seen)==Counter(f'{fam}{i}' for fam in ['BL','NL','WL'] for i in range(32))
for cr,mr,x,y,d in MOUNTS+[KEY]:
 assert xy(foot(c,cr).GetPosition())==xy(foot(m,mr).GetPosition())==[x,y]
 assert xy(next(iter(foot(m,mr).Pads())).GetDrillSize())==[d,d]
# Physical interface fit: mating S land/courtyard vs Control and P courtyard vs module.
# The body+land bounds are wider than the plastic, so this is conservative for board fit.
for pair in PAIRS:
 f=foot(m,pair['module']);bb=f.GetBoundingBox(False,False)
 assert p.ToMM(bb.GetX())>=147 and p.ToMM(bb.GetRight())<=207
 assert p.ToMM(bb.GetY())>=62 and p.ToMM(bb.GetBottom())<=92
# Contour-aligned 180-degree error is 2mm. A 2mm lateral shift can realign two identical pairs, so the separate key post is mandatory.
rotated_A=[354-PAIRS[0]['x'],154-PAIRS[0]['y']]
rotation_error=math.dist(rotated_A,[PAIRS[1]['x'],PAIRS[1]['y']]);assert rotation_error>1.2
with (OUT/'connector-map.csv').open('w') as f:wr=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');wr.writeheader();wr.writerows(rows)
geometry={}
for n,b in boards.items():
 fs=[]
 refs=([f'J{i}' for i in range(400,408)]+['U500','U800','U700','U100','U200','J700','J1800','J1801'] if n=='Control' else [f'J{i}' for i in range(4901,4909)]+['J101','U1102'] if n=='Power' else ['J1','J2','H1','H2','H3'])
 for r in refs:
  f=foot(b,r);bb=f.GetBoundingBox(False,False);fs.append({'ref':r,'pos':xy(f.GetPosition()),'angle':f.GetOrientationDegrees(),'side':f.GetLayerName(),'bbox':[p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())],'pads':[{'pin':a.GetNumber(),'pos':xy(a.GetPosition()),'size':xy(a.GetSize()),'drill':xy(a.GetDrillSize()),'through_hole':a.GetAttribute() in (p.PAD_ATTRIB_PTH,p.PAD_ATTRIB_NPTH),'net':a.GetNetname()} for a in f.Pads()]})
 geometry[n]=fs
(OUT/'geometry.json').write_text(json.dumps(geometry,indent=2))
report={'KiCad':p.Version(),'boards_readable':True,'connector_pairs':len(rows),'lines_verified':len(seen),'signal_GND_per_pair':22,'reserve_per_pair':10,'power_GND_per_pair':4,'rotation_180_axis_mismatch_mm_when_contour_aligned':rotation_error,'key_post_required':True,'key_post_nominal_projection_mm':14.0,'Control_noninterface_schematic_nets_unchanged':True,'noninterface_placements_preserved':True,'Power_PCB_byte_identical_to_day1':True,'schematic_to_PCB_net_assignments_match':True,'counts':{n:{'footprints':len(b.GetFootprints()),'pads':sum(len(list(f.Pads())) for f in b.GetFootprints()),'tracks':len(b.GetTracks())} for n,b in boards.items()},'pin_1_2_3_common_coordinates':detail}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='pin_1_2_3_common_coordinates'},indent=2))
