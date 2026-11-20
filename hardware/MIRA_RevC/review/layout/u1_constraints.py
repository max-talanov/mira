"""Measure U1 top-side constraints from the SAVED adapter PCB and re-read pad geometry.
No physical socket envelope is assumed. Nominal geometric bounds are not design clearances.
"""
from pathlib import Path as _GuardPath
if '"MIRA_Module:ICS-CQFP64-1830-1830-100-1"' in (_GuardPath(__file__).resolve().parents[2]/'MIRA_Crossbar/MIRA_Crossbar.kicad_pcb').read_text():
 raise SystemExit('Socket J3 is installed: the old empty U1-area estimate is historical. See socket-trial/README.md and geometry.json.')

import json,re,hashlib,math
from interface_spec import BASE,OUT
from sexpr_tools import children,reference

def coords(s,tag):
 m=re.search(r'\('+tag+r'\s+([-+.\d]+)\s+([-+.\d]+)',s);assert m,(tag,s[:80]);return [float(m[1]),float(m[2])]
def box(s):return coords(s,'start')+coords(s,'end')
def middle(b):return [(b[0]+b[2])/2,(b[1]+b[3])/2]
def dims(b):return [round(b[2]-b[0],6),round(b[3]-b[1],6)]
def inset(b,m):return [round(b[0]+m,6),round(b[1]+m,6),round(b[2]-m,6),round(b[3]-m,6)]
def main():
 path=BASE/'MIRA_Crossbar/MIRA_Crossbar.kicad_pcb';raw=path.read_text();nodes=[n for _,_,n in children(raw)]
 footprints={reference(n):n for n in nodes if n.startswith('(footprint ')}
 g=json.loads((OUT/'geometry.json').read_text())['Crossbar'];fps={f['ref']:f for f in g}
 outline=box(next(n for n in nodes if n.startswith('(gr_rect ') and '(layer "Edge.Cuts")' in n))
 rects=[box(n) for n in nodes if n.startswith('(gr_rect ') and '(layer "Dwgs.User")' in n]
 grips=[];reserve=None
 for n in nodes:
  if n.startswith('(gr_text ') and ('"GRIP short edge"' in n or '"U1 / socket placement area ONLY"' in n):
   center=coords(n,'at');b=next(b for b in rects if math.dist(middle(b),center)<1e-6)
   if '"GRIP short edge"' in n:grips.append(b)
   else:reserve=b
 assert len(grips)==2 and reserve is not None
 grips.sort()
 power=[];bodies=[];mounts=[]
 for ref in ['J1','J2','H1','H2','H3']:
  f=fps[ref];node=footprints[ref];angle=f['angle'];assert angle==0
  # Body/Fab and courtyard rectangles are read from this footprint instance, not a catalogue size.
  graphics=[n for _,_,n in children(node) if n.startswith('(fp_rect ')]
  for n in graphics:
   if '(layer "B.Fab")' in n and ref.startswith('J'):
    b=box(n);b=[round(v+f['pos'][i%2],6) for i,v in enumerate(b)];bodies.append({'ref':ref,'bbox':b,'side':'B.Cu'})
  if ref.startswith('J'):
   for a in f['pads']:
    if a['through_hole']:
     assert a['pin'] in ['P1','P2','P3','P4'] and a['size']==[1.6,1.6] and a['drill']==[1.2,1.2]
     power.append({'ref':ref,**a})
  else:
   a=next(a for a in f['pads'] if a['through_hole']);assert a['drill']==[2.2,2.2]
   court=next(n for n in graphics if '(layer "F.CrtYd")' in n);b=box(court);b=[round(v+f['pos'][i%2],6) for i,v in enumerate(b)]
   mounts.append({'ref':ref,'pos':a['pos'],'drill':a['drill'],'reservation_bbox':b,'kind':'key' if ref=='H3' else 'M2'})
 assert len(power)==8 and len(bodies)==2
 upper=[a for a in power if a['ref']=='J1'];lower=[a for a in power if a['ref']=='J2']
 band=[grips[0][2],max(a['pos'][1]+a['size'][1]/2 for a in upper),grips[1][0],min(a['pos'][1]-a['size'][1]/2 for a in lower)]
 band=[round(v,6) for v in band];margin=.5;planning=inset(band,margin)
 midx=middle(outline)[0]
 left=max(a['pos'][0]+a['size'][0]/2 for a in power if a['pos'][0]<midx)
 right=min(a['pos'][0]-a['size'][0]/2 for a in power if a['pos'][0]>midx)
 vertical=[round(left,6),outline[1],round(right,6),outline[3]]
 # Independent rectangle/circle clearance check, including mounting reservations and grips.
 for b in [band,planning,vertical]:
  for a in power:
   x,y=a['pos'];distance=math.hypot(x-max(b[0],min(x,b[2])),y-max(b[1],min(y,b[3])))
   assert distance+1e-6>=a['size'][0]/2,(b,a)
  for o in grips+[m['reservation_bbox'] for m in mounts]:
   assert b[2]<=o[0] or b[0]>=o[2] or b[3]<=o[1] or b[1]>=o[3],(b,o)
 result={'source_PCB':str(path.relative_to(BASE)),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'common_view':'Control top / adapter F.Cu up; dimensions mm','outline':outline,'board_size':dims(outline),'power_PTH':power,'mounting_and_key':mounts,'grip_zones':grips,'underside_bodies_dashed':bodies,'current_reservation':reserve,'current_size':dims(reserve),'nominal_horizontal_band':band,'nominal_horizontal_size':dims(band),'proposed_margin_mm':margin,'planning_horizontal_band':planning,'planning_horizontal_size':dims(planning),'nominal_vertical_corridor':vertical,'nominal_vertical_size':dims(vertical),'socket_envelope':'TBD','notes':['Nominal bands are tangent to copper or board edges: not manufacturing clearances.','0.5mm inset is a planning proposal, not a validated socket/fillet/edge clearance.','Top-only socket housing may project over underside connector bodies; through pins/holes/vias and support legs must clear bottom copper and bodies.','The usable outline can be nonrectangular. Preserve PTH access, M2/key reservations and grip windows. Key/spacer tolerances and removal force are open follow-up questions.']}
 (OUT/'u1-constraints.json').write_text(json.dumps(result,indent=2));print('Saved-PCB U1 space: nominal',dims(band),'planning',dims(planning),'vertical',dims(vertical),'socket TBD')
 return result
if __name__=='__main__':main()
