"""Independent dimensional audit of libraries AND four installed footprints.
Expected coordinates transcribed from the individual Hirose PDFs in sources/.
Installation view = looking at the component from its mounting side.
"""
import re,json,hashlib
from pathlib import Path
from sexpr_tools import children,reference
from interface_spec import BASE,OUT,PAIRS

def values(node,tag):
 m=re.search(r'\('+tag+r'\s+([-+.\d]+)(?:\s+([-+.\d]+))?',node);assert m,(tag,node[:90])
 return [float(x) for x in m.groups() if x is not None]
def near(a,b):assert len(a)==len(b) and all(abs(x-y)<1e-6 for x,y in zip(a,b)),(a,b)
def check(s,plug,installed=False):
 pads={};tabs=[]
 for _,_,n in children(s):
  if not n.startswith('(pad '):continue
  key=re.match(r'\(pad "([^"]*)"',n)[1]
  if key:assert key not in pads; pads[key]=n
  else:tabs.append(n)
 assert set(pads)=={str(i) for i in range(1,81)}|{'P1','P2','P3','P4'}
 # Individual drawings, top/installation view: S pin1 upper-left, P pin1 lower-left.
 row=3.15 if plug else 4.75;sign=-1 if plug and not installed else 1
 corners={'1':[-9.75,-row*sign],'40':[9.75,-row*sign],'41':[-9.75,row*sign],'80':[9.75,row*sign]}
 for pin,pos in corners.items():near(values(pads[pin],'at'),pos)
 for i in range(1,81):
  n=pads[str(i)];near(values(n,'at'),[-9.75+((i-1)%40)*.5,(-row if i<=40 else row)*sign]);near(values(n,'size'),[.3,1.9 if plug else 1.8]);assert ' smd rect' in n
 # Factory Power Contact No.1..4: S top-view LL/LR/UL/UR; P top-view UL/UR/LL/LR.
 h=2.375 if plug else 4.675
 power={'P1':[-12.25,h*sign],'P2':[12.25,h*sign],'P3':[-12.25,-h*sign],'P4':[12.25,-h*sign]}
 for pin,pos in power.items():
  n=pads[pin];near(values(n,'at'),pos);near(values(n,'size'),[1.6,1.6]);near(values(n,'drill'),[1.2]);assert ' thru_hole circle' in n
 assert len(tabs)==2
 centre=16.175 if plug else 17.325
 for n,want in zip(sorted(tabs,key=lambda n:values(n,'at')[0]),[-centre,centre]):
  near(values(n,'at'),[want,0]);near(values(n,'size'),[2.45,3.2]);assert ' smd rect' in n
 zones=[n for _,_,n in children(s) if n.startswith('(zone ')]
 if plug:assert not zones
 else:
  assert len(zones)==2
  origin=values(s,'at') if installed else [0,0]
  for z,(left,right) in zip(zones,[(-16.1,-9.9),(9.9,16.1)]):
   assert '(layer "F.Cu")' in z
   for kind in ['tracks','vias','pads','copperpour']:assert f'({kind} not_allowed)' in z
   points=[[float(a),float(b)] for a,b in re.findall(r'\(xy\s+([-+.\d]+)\s+([-+.\d]+)\)',z)]
   expected=[[origin[0]+left,origin[1]-3.85],[origin[0]+right,origin[1]-3.85],[origin[0]+right,origin[1]+3.85],[origin[0]+left,origin[1]+3.85]]
   assert len(points)==4
   for a,b in zip(points,expected):near(a,b)
 return {'signal_corners_local_mm':corners,'power_contacts_local_mm':power,'power_PTH_drill_mm':1.2,'power_PTH_land_mm':1.6,'retention_tabs':2,'copper_prohibition_regions':len(zones),'passed':True}
def main():
 report={'sources':{},'correction':'P1/P2 changed from upper to lower row in assembled view; P3/P4 from lower to upper, to match Hirose Power Contact No.1..4. All remain GND.','checks':{}}
 for file in sorted((OUT/'sources').glob('*_2d.pdf')):report['sources'][file.name]={'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'pages':1}
 assert len(report['sources'])==2
 for plug in [False,True]:
  project='MIRA_Crossbar' if plug else 'MIRA_Control';lib='MIRA_Module' if plug else 'MIRA_C';part='FX23L-80P-0.5SV8' if plug else 'FX23L-80S-0.5SV'
  path=BASE/project/'libraries'/(lib+'.pretty')/('Hirose_'+part+'.kicad_mod');report['checks'][part+'_library_installation_view']=check(path.read_text(),plug)
  board=(BASE/project/(project+'.kicad_pcb')).read_text()
  for pair in PAIRS:
   ref=pair['module' if plug else 'control'];s=next(n for _,_,n in children(board) if n.startswith('(footprint ') and reference(n)==ref)
   assert '(layer "B.Cu")' in s if plug else '(layer "F.Cu")' in s
   report['checks'][project+'/'+ref+'_common_top_view']=check(s,plug,True)
 report['passed']=True
 report['key']={'datum':'Control F.Cu outer mounting surface','projection_tip_mm':14.,'PCB_thickness_mm':1.6,'installed_mounting_gap_mm':8.,'protrusion_above_adapter_FCu_mm':4.4,'key_tip_enters_at_gap_mm':14.,'housing_first_touch_nominal_gap_bound_mm':12.65,'housing_first_touch_max_height_gap_bound_mm':13.25,'nominal_key_entry_lead_mm':1.35,'key_entry_lead_before_max_height_bound_mm':.75,'signal_first_touch_reference_gap_mm':9.5,'power_first_touch_reference_gap_mm':10.,'key_entry_lead_before_signal_reference_mm':4.5,'key_entry_lead_before_power_reference_mm':4.,'conditions':'Straight aligned insertion. 1.5mm signal and 2mm power effective mating lengths are reference dimensions, not guaranteed first-touch limits. Key projection tolerance, tip chamfer and tilt budget TBD; require H_min - chamfer_max - tilt_budget > 13.25mm.'}
 (OUT/'footprint-drawing-audit.json').write_text(json.dumps(report,indent=2));print('Individual Hirose drawing audit: 2 libraries + 4 PCB instances PASS; corners 1/40/41/80, 4 power PTH, retention tabs, S copper prohibition.')
if __name__=='__main__':main()
