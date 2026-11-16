"""Run with KiCad 10 pcbnew Python. Rebuilds draft from recorded source SHA."""
import pcbnew as p, json, csv, math, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'hardware/MIRA_RevC'; OUT=Path(__file__).resolve().parent
SHA='439da953af8e23b70ae902847f65b4afd8eb2a95'
def v(x,y): return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def xy(q): return [round(p.ToMM(q.x),6),round(p.ToMM(q.y),6)]
def fp(b,r): return next(f for f in b.GetFootprints() if f.GetReference()==r)
def text(b,s,x,y,size=1):
 t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(v(x,y));t.SetTextSize(v(size,size));t.SetTextThickness(p.FromMM(.15));t.SetLayer(p.Dwgs_User);b.Add(t)
def line(b,a,z,layer=p.Dwgs_User):
 d=p.PCB_SHAPE();d.SetShape(p.SHAPE_T_SEGMENT);d.SetStart(v(*a));d.SetEnd(v(*z));d.SetLayer(layer);d.SetWidth(p.FromMM(.1 if layer==p.Edge_Cuts else .2));b.Add(d)
def rect(b,box,label=None,layer=p.Dwgs_User):
 x,y,X,Y=box
 for a,z in [((x,y),(X,y)),((X,y),(X,Y)),((X,Y),(x,Y)),((x,Y),(x,y))]:line(b,a,z,layer)
 if label:text(b,label,(x+X)/2,(y+Y)/2)
def circle(b,x,y):
 d=p.PCB_SHAPE();d.SetShape(p.SHAPE_T_CIRCLE);d.SetCenter(v(x,y));d.SetEnd(v(x+3,y));d.SetLayer(p.Dwgs_User);d.SetWidth(p.FromMM(.2));b.Add(d)
def move(b,r,x,y):fp(b,r).SetPosition(v(x,y))
def electrical(b):
 return {'footprints':len(b.GetFootprints()),'pads':sorted((f.GetReference(),a.GetNumber(),a.GetNetname()) for f in b.GetFootprints() for a in f.Pads()),'tracks':len(b.GetTracks()),'zones':len(b.Zones())}
boards={};before={};paths={}
for n in ['Control','Power','Crossbar']:
 path=BASE/f'MIRA_{n}/MIRA_{n}.kicad_pcb';paths[n]=path
 raw=subprocess.check_output(['git','show',f'{SHA}:{path.relative_to(ROOT)}'],cwd=ROOT)
 tmp=Path(tempfile.gettempdir())/f'mira-{n}-source.kicad_pcb';tmp.write_bytes(raw)
 boards[n]=p.LoadBoard(str(tmp));before[n]=electrical(boards[n])
c,w,m=[boards[n] for n in ['Control','Power','Crossbar']]
# Common XY is KiCad XY, all mm. Power is unreflected, module reflected y -> 164-y.
rect(c,(50,20,230,158.2),layer=p.Edge_Cuts)
rect(w,(10,20,230,158.2),layer=p.Edge_Cuts)
rect(m,(147,72,207,102),layer=p.Edge_Cuts) # assembly bounds y62..92
for b in [c,w]:
 for x,y in [(55,25),(225,25),(55,150),(225,150)]:
  circle(b,x,y);text(b,'STANDOFF / drill TBD',x+10,y+4,.7)
# Two optional three-board support axes; module coordinates reflect Y.
for x,y in [(154,67),(200,67)]:
 for b in [c,w]:circle(b,x,y)
 circle(m,x,164-y)
text(m,'Support height / fasteners TBD',177,70,.7)
for b in boards.values():
 b.GetDesignSettings().SetAuxOrigin(v(0,0));b.GetDesignSettings().SetGridOrigin(v(0,0))
 line(b,(0,0),(15,0));line(b,(0,0),(0,15));text(b,'O (0,0) / +X right / +Y down',24,5)
 text(b,'MIRA-01.02.00 DRAFT / HEIGHTS TBD',135,12)
# Preserve all 16 floorplan positions including USB-C and J1800.
move(c,'U100',77,47);move(c,'U200',107,51)
positions=[(65,65),(65,103),(79,108),(93,65),(122,104),(122,126),(215,103),(215,132)]
for i,(x,y) in enumerate(positions):
 f=fp(c,f'J{400+i}');f.SetPosition(v(x,y));f.Flip(f.GetPosition(),False) # B.Cu 180; pin2 left; pin3 down
 move(w,f'J{4901+i}',x,y)
# Preserve relative Power staging by parking the unplaced set as one group.
selected={'U1102','J101'}|{f'J{4901+i}' for i in range(8)}
for f in w.GetFootprints():
 if f.GetReference() not in selected:f.Move(v(300,0))
# Cincon original Fab body is [-5.08,-2.54]..[20.32,48.26] relative to pin1.
move(w,'U1102',20.08,57.54) # actual body [15,55]..[40.4,105.8]
move(w,'J101',17,154) # bottom edge accessible screw terminal
move(m,'J1',177,82) # native F.Cu, flipped only in assembly about longitudinal X
for b in [c,w]:
 rect(b,(145,60,209,94),'Crossbar removal +Z / clear access / height TBD')
rect(w,(15,55,40.4,105.8),'U1102 25.4 x 50.8 / H12.7')
text(w,'10 mm overhang clearance to Control x=50',28,113,.8)
for box,label in [((125,25,165,58),'BL0-15'),((175,25,220,58),'BL16-31'),((130,100,167,145),'NL0-15'),((174,100,207,145),'NL16-31'),((130,148,207,155),'WL'),((132,94,207,98),'J1800 routing corridor'),((168,98,173,155),'WL path')]:rect(c,box,label)
text(m,'U1 die / bonding / outline TBD',177,95)
text(m,'Assembly: X=x; Y=164-y; F.Cu faces Control',177,106,.8)
text(c,'USB-C access at bottom edge',100,160)
text(w,'J101 cable / screwdriver access - bottom',65,160)
# Save and reload: all subsequent geometry is taken from files, not placement intentions.
for n,b in boards.items():
 project=paths[n].with_suffix('.kicad_pro');project_bytes=project.read_bytes()
 try:p.SaveBoard(str(paths[n]),b)
 finally:project.write_bytes(project_bytes)
boards={n:p.LoadBoard(str(path)) for n,path in paths.items()};c,w,m=[boards[n] for n in ['Control','Power','Crossbar']]
checks={}
for n,b in boards.items():
 after=electrical(b);assert after==before[n],n
 checks[n]={'readable':True,'footprints':after['footprints'],'pads':len(after['pads']),'tracks':after['tracks'],'zones':after['zones'],'electrical_unchanged':True}
for row in csv.DictReader((BASE/'review/prelayout/Control-floorplan.csv').open()):
 assert xy(fp(c,row['ref']).GetPosition())==[float(row['x_mm']),float(row['y_mm'])]
rows=[];pad_checks=[]
def half(b,r,module=False):
 f=fp(b,r);x,y=xy(f.GetPosition());a={a.GetNumber():a for a in f.Pads() if a.GetNumber()}
 points={k:xy(a[k].GetPosition()) for k in ['1','2','3']}
 if module:y=164-y;points={k:[q[0],round(164-q[1],6)] for k,q in points.items()}
 # pin1 vector relative footprint datum, and vector 1->3 (increasing odd contacts)
 return {'ref':r,'pcb_x':xy(f.GetPosition())[0],'pcb_y':xy(f.GetPosition())[1],'pcb_angle':f.GetOrientationDegrees(),'pcb_side':f.GetLayerName(),'common_x':x,'common_y':y,'common_angle':-f.GetOrientationDegrees() if module else f.GetOrientationDegrees(),'common_side':'down (-Z)' if module or f.GetLayer()==p.B_Cu else 'up (+Z)','pin1_x':points['1'][0],'pin1_y':points['1'][1],'pin1_orientation':f"datum->1 ({points['1'][0]-x:.3f},{points['1'][1]-y:.3f}); 1->3 ({points['3'][0]-points['1'][0]:.3f},{points['3'][1]-points['1'][1]:.3f})",'points':points}
for i in range(9):
 A=half(c,f'J{400+i}' if i<8 else 'J1800');B=half(w,f'J{4901+i}') if i<8 else half(m,'J1',True)
 if i<8:
  fa,fb=fp(c,A['ref']),fp(w,B['ref']);pa={a.GetNumber():a for a in fa.Pads()};pb={a.GetNumber():a for a in fb.Pads()}
  for k in pa:
   assert xy(pa[k].GetPosition())==xy(pb[k].GetPosition()),(i,k)
   expected='CORE_SENSE_P' if i==1 and k=='17' else pa[k].GetNetname()
   assert pb[k].GetNetname()==expected
 else:
  # Receptacle and plug solder tails are 0.15mm apart in projection; centers mate.
  for k in ['1','2','3']:
   assert A['points'][k][0]==B['points'][k][0]
   assert abs(abs(A['points'][k][1]-B['points'][k][1])-.15)<1e-5
  for k in range(1,141):
   pa=next(a for a in fp(c,'J1800').Pads() if a.GetNumber()==str(k));pb=next(a for a in fp(m,'J1').Pads() if a.GetNumber()==str(k))
   assert pa.GetNetname()==pb.GetNetname()
 record={'pair':i+1,'status':'all pads coincide' if i<8 else 'FX8 mating axes coincide; solder tails offset 0.15mm'}
 for prefix,h in [('control',A),('mate',B)]:
  for k,val in h.items():
   if k!='points':record[prefix+'_'+k]=val
 for k in ['1','2','3']:pad_checks.append({'pair':i+1,'pin':k,'control':A['points'][k],'mate':B['points'][k]})
 rows.append(record)
with (OUT/'connector-map.csv').open('w') as f:
 wr=csv.DictWriter(f,fieldnames=rows[0].keys());wr.writeheader();wr.writerows(rows)
(OUT/'verification.json').write_text(json.dumps({'source_sha':SHA,'boards':checks,'floorplan_16_preserved':True,'connector_pin_checks':pad_checks},indent=2))
# Fact geometry for the review image, use Fab bounds, not courtyard text.
data={}
for n,b in boards.items():
 fs=[]
 refs=([*['J'+str(i) for i in range(400,408)],'U500','U800','U700','U100','U200','J700','J1800'] if n=='Control' else [*['J'+str(i) for i in range(4901,4909)],'J101','U1102'] if n=='Power' else ['J1'])
 for r in refs:
  f=fp(b,r);bb=f.GetBoundingBox(False,False);fs.append({'ref':r,'pos':xy(f.GetPosition()),'bbox':[p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())]})
 data[n]=fs
(OUT/'geometry.json').write_text(json.dumps(data,indent=2))
print(json.dumps(checks,indent=2))
