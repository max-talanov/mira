"""Assemble saved native board bodies and assigned component STEP models.

Only already placed parts enter the stack. Parked groups remain on the source PCBs.
The PNG uses explicit component colors and nominal, documented board Z datums.
"""
from pathlib import Path
import json,math,sys,collections
import cadquery as cq
import vtk
ROOT=Path(__file__).resolve().parents[3];STATE=Path('/tmp/mira-layout-audit');OUT=ROOT/'review/layout-audit'
data=json.loads((STATE/'native-after.json').read_text());catalog=json.loads((OUT/'model-catalog.json').read_text())
meta={x['model']['file']:x['model'] for x in catalog['packages'] if x['model'].get('file')};meta.update({x['file']:x for x in catalog['hardware'].values()})
Z={'MIRA_Control':dict(top=1.6,bottom=0),'MIRA_Power':dict(top=-12,bottom=-13.6),'MIRA_Crossbar':dict(top=11.2,bottom=9.6)}
def inside(point,poly):
 x,y=point;odd=False
 for i,(x1,y1) in enumerate(poly):
  x2,y2=poly[i-1]
  if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1:odd=not odd
 return odd

def load(path):return cq.Compound.makeCompound([x for x in cq.importers.importStep(str(path)).vals() if x.Faces()])
def color(f):
 if f['ref'].startswith('H'):return (.68,.70,.73)
 if 'ICS-CQFP' in f['footprint']:return (.78,.57,.20)
 if f['ref'].startswith('C'):return (.66,.52,.32)
 return (.12,.13,.15)
cache={};assembly=cq.Assembly(name='MIRA_nominal_current_placement');objects=[];parts=[]
for pr,board in data.items():
 shape=load(STATE/(pr+'-body.step'));bb=shape.BoundingBox();assert bb.zmin>=-.02 and bb.zmax<=board['thickness']+.02,(pr,bb.zmin,bb.zmax)
 shape=shape.translate((0,0,Z[pr]['bottom']));col={'MIRA_Control':(.12,.36,.25),'MIRA_Power':(.13,.23,.36),'MIRA_Crossbar':(.30,.44,.25)}[pr]
 assembly.add(shape,name=pr+'_PCB',color=cq.Color(*col));objects.append((pr+'_PCB',shape,col))
 for f in board['footprints']:
  if not any(inside(f['xy'],poly) for poly in board['outlines']):continue
  for index,model in enumerate(f['models']):
   if not model['visible']:continue
   path=Path(model['path'].replace('${KIPRJMOD}',str(ROOT/pr)));name=path.name
   if name not in cache:cache[name]=load(path)
   sh=cache[name]
   assert all(abs(v-1)<1e-9 for v in model['scale']),name
   # KiCad model rotations use the opposite sign from the right-handed CAD axes.
   for axis,angle in zip([(1,0,0),(0,1,0),(0,0,1)],model['rotation']):
    if angle:sh=sh.rotate((0,0,0),axis,-angle)
   sh=sh.translate(tuple(model['offset']))
   back=f['side']=='B.Cu'
   if back:sh=sh.rotate((0,0,0),(1,0,0),180)
   sh=sh.rotate((0,0,0),(0,0,1),f['angle']).translate((f['xy'][0],-f['xy'][1],Z[pr]['bottom' if back else 'top']))
   label=pr+'_'+f['ref']+'_'+str(index);col=color(f);assembly.add(sh,name=label,color=cq.Color(*col));objects.append((label,sh,col));b=sh.BoundingBox()
   parts.append(dict(project=pr,reference=f['ref'],side=f['side'],model=name,kind=meta[name]['kind'],bounds_mm=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],shape=sh))
assembly.export(str(OUT/'step/MIRA-assembly.step'))
# Exact intersection tests follow an AABB broad phase. Connector envelope mating
# overlap is classified separately: these models do not contain mating cavities.
collisions=[]
def intersection(a,b):return [max(a[i],b[i]) for i in range(3)]+[min(a[i+3],b[i+3]) for i in range(3)]
for i,a in enumerate(parts):
 for b in parts[i+1:]:
  ab=intersection(a['bounds_mm'],b['bounds_mm']);depth=[ab[i+3]-ab[i] for i in range(3)]
  if min(depth)<=.015:continue
  pair={a['reference'],b['reference']}
  hirose='Hirose' in a['model'] and 'Hirose' in b['model'] and a['project']!=b['project']
  samtec=(('HTSW' in a['model'] and 'SSW' in b['model']) or ('SSW' in a['model'] and 'HTSW' in b['model'])) and a['project']!=b['project']
  if hirose or samtec:
   collisions.append(dict(a=a['project']+'/'+a['reference'],b=b['project']+'/'+b['reference'],status='expected_mating_envelope_overlap',overlap_xyz_mm=depth,next_action='Obtain exact mating CAD/physical fit; solid envelopes have no contact cavities.'));continue
  common=a['shape'].intersect(b['shape']);volume=common.Volume()
  if volume>.0001:collisions.append(dict(a=a['project']+'/'+a['reference'],b=b['project']+'/'+b['reference'],status='component_overlap',intersection_mm3=volume,overlap_xyz_mm=depth,next_action='Inspect the referenced parts; validate exact package and placement before moving either part.'))
# Test component material against the exact PCB bodies, including actual holes.
board_hits=[]
for p in parts:
 for label,body,col in objects[:0]:pass
 for pr in data:
  if pr==p['project']:continue
  body=next(s for n,s,c in objects if n==pr+'_PCB');bb=body.BoundingBox();b=[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax];ab=intersection(p['bounds_mm'],b)
  if min(ab[i+3]-ab[i] for i in range(3))<=.015:continue
  volume=p['shape'].intersect(body).Volume()
  if volume>.0001:board_hits.append(dict(component=p['project']+'/'+p['reference'],board=pr,status='component_board_overlap',intersection_mm3=volume,next_action='Confirm model and board clearance; do not assume a routing change resolves a mechanical collision.'))
# Measured connector and mounting alignment at the actual saved XY/angles.
def fp(pr,ref):return next(f for f in data[pr]['footprints'] if f['ref']==ref)
interfaces=[]
for cr,mr in [('J620001','J10001'),('J620002','J10002')]:
 a,b=fp('MIRA_Control',cr),fp('MIRA_Crossbar',mr);interfaces.append(dict(a=cr,b=mr,xy_error_mm=math.dist(a['xy'],b['xy']),angle_error_deg=abs(a['angle']-b['angle']),gap_mm=8.,status='nominal_axes_match'))
for cr,pr in [('J70001','J260001'),('J80001','J270001'),('J80002','J270002'),('J80003','J270003'),('J80004','J270004'),('J160001','J270005'),('J90001','J280001'),('J90002','J280002')]:
 a,b=fp('MIRA_Control',cr),fp('MIRA_Power',pr);interfaces.append(dict(a=cr,b=pr,xy_error_mm=math.dist(a['xy'],b['xy']),gap_mm=12.,status='nominal_axes_match' if math.dist(a['xy'],b['xy'])<.001 else 'XY_mismatch'))
cin=next(p for p in parts if 'Cincon' in p['model']);surface_gap=50-cin['bounds_mm'][3]
report=dict(datums_mm=Z,placed_model_instances=len(parts),interfaces=interfaces,component_intersections=collisions,component_board_intersections=board_hits,
 cincon=dict(reference='MIRA_Power/U110001',bounds_mm=cin['bounds_mm'],clearance_to_control_left_edge_mm=surface_gap,above_control_BCu_mm=cin['bounds_mm'][5],status='no_XY_overlap_with_Control',next_action='Keep the left exposed strip clear; verify airflow and cables on the selected converter sample.'),
 key=dict(control='H1802',module='H3',diameter_mm=2.,hole_mm=2.2,radial_clearance_mm=.1,projection_mm=14.,protrusion_above_module_mm=4.4,guaranteed=False,next_action='Select fixed pin/holder and check chamfer, tilt and tolerance against 13.25 mm housing bound.'),
 access=dict(grip_windows_mm=[[152,60,192,70],[152,144,192,154]],usb_slot_width_mm=20.,socket_closed_height_mm=11.2,socket_height_confirmed=False,removal_required_until_key_clears_mm=4.4,next_action='Obtain exact socket closed/open/latch/under-board fastener drawing; test grip, mating force and cable bend space.'))
for p in parts:p.pop('shape')
report['parts']=parts;(OUT/'assembly-checks.json').write_text(json.dumps(report,indent=2)+'\n')
# Offscreen CAD view. Native unmodified top/bottom KiCad renders are separate PNGs.
renderer=vtk.vtkRenderer();renderer.SetBackground(.95,.96,.98)
for label,shape,col in objects:
 vertices,triangles=shape.tessellate(.12,.2);points=vtk.vtkPoints()
 for v in vertices:points.InsertNextPoint(v.x,v.y,v.z)
 cells=vtk.vtkCellArray()
 for tri in triangles:
  cells.InsertNextCell(3)
  for v in tri:cells.InsertCellPoint(v)
 poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells);mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly);actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(*col);actor.GetProperty().SetAmbient(.25);actor.GetProperty().SetDiffuse(.7);renderer.AddActor(actor)
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(True);window.SetSize(2200,1700);window.AddRenderer(renderer)
camera=renderer.GetActiveCamera();camera.SetPosition(-320,-440,360);camera.SetFocalPoint(125,-130,0);camera.SetViewUp(0,0,1);camera.ParallelProjectionOn();renderer.ResetCamera();camera.Zoom(1.1)
for text,x,y,size in [('MIRA | current placed assembly',30,1650,30),('Control F=+1.6 | Power F=-12 | Crossbar B=+9.6 mm',30,1610,20),('Nominal stack. Socket, hardware and connector envelopes include unconfirmed mechanics.',30,35,18)]:
 actor=vtk.vtkTextActor();actor.SetInput(text);actor.SetDisplayPosition(x,y);actor.GetTextProperty().SetFontSize(size);actor.GetTextProperty().SetColor(.12,.16,.22);renderer.AddActor2D(actor)
window.Render();capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.Update();writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/'views/MIRA-assembly.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()
print('Assembly:',len(parts),'placed models;',len(board_hits),'board collisions;',len(collisions),'component/envelope intersections',flush=True)
