
from pathlib import Path as _P
import json as _J, hashlib as _H
_o=_P(__file__).resolve().parents[1];_r=_P(__file__).resolve().parents[4]
for _pr,_c in _J.loads((_o/'validation.json').read_text())['checks'].items():
 assert _H.sha256((_r/_pr/(_pr+'.kicad_pcb')).read_bytes()).hexdigest()==_c['pcb_sha256'], 'Saved PCB changed: re-export geometry before using snapshot tools'

import json,csv,math,collections,hashlib
from pathlib import Path
import gzip
R=Path(__file__).resolve().parents[4];O=R/'review/layout/MIRA-01.01.00';a=json.loads(gzip.decompress((O/'checks/boards.json.gz').read_bytes()));b=json.loads(gzip.decompress((O/'baseline/boards.json.gz').read_bytes()));rows=[];detail=[]
def fp(pr,ref):return next(f for f in a[pr]['footprints'] if f['ref']==ref)
def half(pr,ref,prefix):
 f=fp(pr,ref);pads={p['number']:p for p in f['pads'] if p['number']};pt=pads['1']['xy'];two=pads['2']['xy'];return {prefix+k:v for k,v in dict(board=pr,ref=ref,MPN=f['value'],x=f['xy'][0],y=f['xy'][1],angle=f['angle'],side=f['side'],pin1_x=pt[0],pin1_y=pt[1],pin1_orientation=f"datum->1 ({pt[0]-f['xy'][0]:.3f},{pt[1]-f['xy'][1]:.3f}); 1->2 ({two[0]-pt[0]:.3f},{two[1]-pt[1]:.3f})").items()}
pairs=[('PC'+str(i+1),c,'MIRA_Power',p) for i,(c,p) in enumerate([('J70001','J220001'),('J80001','J230001'),('J80002','J230002'),('J80003','J230003'),('J80004','J230004'),('J160001','J230005'),('J90001','J240001'),('J90002','J240002')])]+[('A','J580001','MIRA_Crossbar','J10001'),('B','J580002','MIRA_Crossbar','J10002')]
for name,cr,pr,mr in pairs:
 c,m=fp('MIRA_Control',cr),fp(pr,mr);cp={p['number']:p for p in c['pads'] if p['number']};mp={p['number']:p for p in m['pads'] if p['number']};assert cp.keys()==mp.keys();assert c['xy']==m['xy'];isfx=pr=='MIRA_Crossbar';assert c['side']==('F.Cu' if isfx else 'B.Cu') and m['side']==('B.Cu' if isfx else 'F.Cu')
 errs=[]
 for n in cp:
  dx,dy=[mp[n]['xy'][k]-cp[n]['xy'][k] for k in range(2)]
  if isfx:
   assert abs(dy)<1e-6
   if n.isdigit():assert abs(abs(dx)-1.6)<1e-6
   elif n.startswith('P'):assert abs(abs(dx)-2.3)<1e-6
  else:assert abs(dx)+abs(dy)<1e-6
  errs.append(dict(pin=n,control_net=cp[n]['net'],mate_net=mp[n]['net'],pad_delta_mm=[dx,dy]))
 row=dict(pair=name,**half('MIRA_Control',cr,'control_'),**half(pr,mr,'mate_'),axis_error_mm=math.dist(c['xy'],m['xy']),gap_mm=8 if isfx else 12,status='AXES_AND_CHIRALITY_PASS; H8 per SV8 drawing, exact STEP/fit pending' if isfx else 'PAD_XY_PASS; H12 intent, nominal insertion4.89mm; contact depth/tolerance pending',next_action='#2 exact Hirose STEP/physical fit, clearance with socket screws' if isfx else '#4 confirm Samtec engagement at 12mm and choose fixed standoffs')
 rows.append(row);detail.append(dict(pair=name,pins=errs))
with (R/'review/layout/connector-map.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator="\n");w.writeheader();w.writerows(rows)
(O/'pair-pin-checks.json').write_text(json.dumps(detail,indent=2));assert len(rows)==10
# Unmodified physical pins/net assignments/UUIDs/3D across all pre-existing components.
pres={}
for pr,old in b.items():
 before={f['uuid']:f for f in old['footprints']};after={f['uuid']:f for f in a[pr]['footprints']};assert before.keys()<=after.keys()
 moved=[]
 for uid,f in before.items():
  g=after[uid]
  for key in ['ref','value','footprint','path','side','dnp','models']:assert f[key]==g[key],(pr,f['ref'],key)
  # Native pcbnew rotates absolute pad angles together with footprint.
  for x,y in zip(sorted(f['pads'],key=lambda p:(p['number'],p['local'])),sorted(g['pads'],key=lambda p:(p['number'],p['local']))):
   for key in ['number','local','size','drill','type','shape','layers','net','mask_margin','paste_margin']:assert x[key]==y[key],(pr,f['ref'],key,x[key],y[key])
  if f['xy']!=g['xy'] or f['angle']!=g['angle']:moved.append(f['ref'])
 pres[pr]=dict(original_footprints_preserved=len(before),added_mechanical_holes=len(after)-len(before),moved=moved,all_pad_net_assignments_and_model_bindings='unchanged',tracks_before=old['tracks'],tracks_after=a[pr]['tracks'],outline_closed=a[pr]['outline_valid'])
(O/'preservation.json').write_text(json.dumps(pres,indent=2));print('10 pairs / all original footprint identities, nets and models: PASS')
