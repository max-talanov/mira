"""Apply model links only; preserve all pad/placement/route data verbatim."""
from pathlib import Path
import json,sys,re,hashlib,shutil
ROOT=Path(__file__).resolve().parents[3];REPO=ROOT.parents[1];STATE=Path('/tmp/mira-layout-audit')
sys.path.insert(0,str(ROOT/'review/schematic-layout'));from kicad_sexpr import child,children,leaves,kind,quoted,uuid
assign=json.loads((STATE/'model-assignments.json').read_text());catalog=json.loads((ROOT/'review/layout-audit/model-catalog.json').read_text());mapping={(x['project'],x['footprint']):x for x in assign};native=json.loads((STATE/'native-before.json').read_text());changes=[]
def block(model,transform=None):
 if not model.get('file'):return ''
 t=transform or dict(offset=[0,0,0],scale=[1,1,1],rotation=[0,0,0])
 def v(k):return ' '.join(str(x) for x in t[k])
 return f'(model "${{KIPRJMOD}}/../libraries/3d/{model["file"]}" (offset (xyz {v("offset")})) (scale (xyz {v("scale")})) (rotate (xyz {v("rotation")})))'
def set_models(s,new):
 for x in leaves(s,'model'):s=s.replace(x,'',1)
 return s.rstrip()[:-1]+'\n'+new+'\n)'
# Every active library package, including schematic-only components.
for entry in assign:
 p=REPO/entry['library'];s=p.read_text();new=set_models(s,block(entry['model'],entry['transform']))+'\n'
 if s!=new:p.write_text(new);changes.append(dict(file=str(p.relative_to(REPO)),kind='library_model',footprint=entry['footprint']))
# Board models are explicitly updated as saved footprint instances.
for pr,data in native.items():
 p=ROOT/pr/(pr+'.kicad_pcb');s=p.read_text();byid={f['uuid']:f for f in data['footprints']};parts=[];cursor=0
 for f in leaves(s,'footprint'):
  source=byid[uuid(f)];key=(pr,source['footprint']);model=None;transform=None
  if key in mapping:
   model=mapping[key]['model'];transform=mapping[key]['transform']
  elif pr=='MIRA_Control' and source['ref'] in ['H1800','H1801']:model=catalog['hardware']['M2_SPACER_8mm_PROVISIONAL']
  elif pr=='MIRA_Control' and source['ref']=='H1802':model=catalog['hardware']['KEY_D2_14mm_PROVISIONAL']
  elif pr=='MIRA_Crossbar' and source['ref'] in ['H1','H2']:model=catalog['hardware']['M2_SCREW_HEAD_PROVISIONAL']
  else:model=dict(file=None,kind='mechanical_hole_no_housing')
  new=set_models(f,block(model,transform))
  if pr=='MIRA_Crossbar' and source['ref']=='J3':
   # Exact UUID matches schematic J10003. The trial geometry remains unchanged.
   new=re.sub(r'(\(fp_text\s+reference\s+)"J3"',r'\1"J10003"',new)
   changes.append(dict(file=str(p.relative_to(REPO)),kind='reference_correction',old='J3',new='J10003',uuid=source['uuid'],reason='Matches the existing schematic symbol UUID after page annotation; no second socket added.'))
  start=s.find(f,cursor);assert start>=0;parts.extend([s[cursor:start],new]);cursor=start+len(f)
  changes.append(dict(file=str(p.relative_to(REPO)),kind='board_model',reference='J10003' if source['ref']=='J3' else source['ref'],uuid=source['uuid'],model=model.get('file'),quality=model.get('kind')))
 parts.append(s[cursor:]);p.write_text(''.join(parts))
source=ROOT/'MIRA_Power/libraries/KiCad_3D_LICENSE.md';shutil.copy2(source,ROOT/'libraries/3d/KiCad_3D_LICENSE.md')
(STATE/'applied-changes.json').write_text(json.dumps(changes,indent=2)+'\n');print('Updated library packages',len(assign),'and footprint instances',sum(len(d['footprints']) for d in native.values()))
