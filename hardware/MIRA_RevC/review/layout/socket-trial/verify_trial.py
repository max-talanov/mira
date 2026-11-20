"""Re-read saved boards, independent socket geometry and all 96 interface assignments."""
import pcbnew as p,sys,json,re,csv,math,hashlib,xml.etree.ElementTree as ET
from collections import Counter
from trial_spec import *
sys.path.insert(0,str(LAYOUT));from sexpr_tools import children,reference
from interface_spec import pinout

def xy(q):return [round(p.ToMM(q.x),6),round(p.ToMM(q.y),6)]
def fp(b,r):return next(f for f in b.GetFootprints() if f.GetReference()==r)
def pads(f):return {a.GetNumber():a for a in f.Pads() if a.GetNumber()}
def rotate(a,angle):
 t=math.radians(angle);x,y=a;return [round(x*math.cos(t)+y*math.sin(t),6),round(-x*math.sin(t)+y*math.cos(t),6)]
def near(a,b):assert len(a)==len(b) and all(abs(x-y)<2e-6 for x,y in zip(a,b)),(a,b)
def netlist(file):
 t=ET.parse(file);return {(n.get('ref'),n.get('pin')):(net.get('name'),n.get('pintype','')) for net in t.findall('./nets/net') for n in net}
def electrical(b):return sorted((f.GetReference(),a.GetNumber(),a.GetNetname()) for f in b.GetFootprints() for a in f.Pads())
boards={n:p.LoadBoard(str(BASE/f'MIRA_{n}/MIRA_{n}.kicad_pcb')) for n in ['Control','Crossbar','Power']};c,m,w=[boards[n] for n in ['Control','Crossbar','Power']]
intent=json.loads((OUT/'afe-placement-intent.json').read_text());refs=set(intent)
# Current local edits, including user project preferences, must survive in content.
# Compared as parsed JSON so a KiCad re-save (key order, indentation, float repr such as
# 0.049999999999999996 -> 0.05) is not a difference; added/removed keys and real value changes are.
def pro_diff(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  return [d for k in sorted(set(a)|set(b)) for d in (pro_diff(a[k],b[k],f'{path}/{k}') if k in a and k in b else [f'{path}/{k}: '+('added' if k in b else 'removed')])]
 if isinstance(a,list) and isinstance(b,list):
  return [f'{path}: length {len(a)} -> {len(b)}'] if len(a)!=len(b) else [d for i,(x,y) in enumerate(zip(a,b)) for d in pro_diff(x,y,f'{path}[{i}]')]
 numeric=all(isinstance(v,(int,float)) and not isinstance(v,bool) for v in (a,b))
 if numeric and math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-12) or not numeric and a==b:return []
 return [f'{path}: {a!r} -> {b!r}']
for n in ['Control','Crossbar','Power']:
 d=pro_diff(*(json.loads(f.read_text()) for f in [OUT/'before'/f'MIRA_{n}.kicad_pro',BASE/f'MIRA_{n}/MIRA_{n}.kicad_pro']))
 assert not d,n+' project preferences differ from before/:\n  '+'\n  '.join(d)
assert (BASE/'MIRA_Power/MIRA_Power.kicad_pcb').read_bytes()==(OUT/'before/MIRA_Power.kicad_pcb').read_bytes()
before_c=p.LoadBoard(str(OUT/'before/MIRA_Control.kicad_pcb'));assert electrical(c)==electrical(before_c)
exclude=refs|{'J1800','J1801','H1800','H1801','H1802'}
def blocks(raw):return {reference(s):s for _,_,s in children(raw) if s.startswith('(footprint ') and reference(s) not in exclude}
assert blocks((BASE/'MIRA_Control/MIRA_Control.kicad_pcb').read_text())==blocks((OUT/'before/MIRA_Control.kicad_pcb').read_text())
cn=netlist(OUT/'control.xml');mn=netlist(OUT/'module.xml')
for b,nodes in [(c,cn),(m,mn)]:
 for f in b.GetFootprints():
  if f.GetAttributes()&p.FP_BOARD_ONLY:continue
  for a in f.Pads():
   if a.GetNumber():assert a.GetNetname()==nodes[f.GetReference(),a.GetNumber()][0],(f.GetReference(),a.GetNumber(),a.GetNetname(),nodes.get((f.GetReference(),a.GetNumber())))
rows=[];lines=[]
def half(b,r):
 f=fp(b,r);ps=pads(f);one=xy(ps['1'].GetPosition());pos=xy(f.GetPosition());two=xy(ps['2'].GetPosition());three=xy(ps['3'].GetPosition())
 return {'ref':r,'pcb_x':pos[0],'pcb_y':pos[1],'pcb_angle':f.GetOrientationDegrees(),'pcb_side':f.GetLayerName(),'common_x':pos[0],'common_y':pos[1],'common_angle':f.GetOrientationDegrees(),'common_side':'down (-Z)' if f.GetLayer()==p.B_Cu else 'up (+Z)','pin1_x':one[0],'pin1_y':one[1],'pin1_orientation':f'1->2 ({two[0]-one[0]:.3f},{two[1]-one[1]:.3f}); 1->3 ({three[0]-one[0]:.3f},{three[1]-one[1]:.3f})'}
for i in range(10):
 if i<8:ar=f'J{400+i}';br=f'J{4901+i}';mate=w
 else:pair=PAIRS[i-8];ar=pair['control'];br=pair['module'];mate=m
 A=half(c,ar);B=half(mate,br);fa,fb=fp(c,ar),fp(mate,br);pa,pb=pads(fa),pads(fb)
 if i<8:
  for k in pa:
   near(xy(pa[k].GetPosition()),xy(pb[k].GetPosition()));assert pb[k].GetNetname()==('CORE_SENSE_P' if (ar,k)==('J401','17') else pa[k].GetNetname())
 else:
  assert fa.GetLayer()==p.F_Cu and fb.GetLayer()==p.B_Cu;assert fa.GetOrientationDegrees()==fb.GetOrientationDegrees()==pair['angle']
  near(xy(fa.GetPosition()),[pair['x'],pair['y']]);near(xy(fb.GetPosition()),[pair['x'],pair['y']])
  mapping=pinout(pair['pair'])
  for k,net in mapping.items():
   if k.isdigit():local=[-9.75+((int(k)-1)%40)*.5,-4.75 if int(k)<=40 else 4.75];mate_local=[local[0],-3.15 if int(k)<=40 else 3.15]
   else:
    local={'P1':[-12.25,4.675],'P2':[12.25,4.675],'P3':[-12.25,-4.675],'P4':[12.25,-4.675]}[k];mate_local=[local[0],math.copysign(2.375,local[1])]
   for a,v in [(pa[k],local),(pb[k],mate_local)]:
    q=rotate(v,pair['angle']);near(xy(a.GetPosition()),[pair['x']+q[0],pair['y']+q[1]])
   if net=='NC':assert 'no_connect' in cn[ar,k][1] and 'no_connect' in mn[br,k][1]
   else:
    assert pa[k].GetNetname()==pb[k].GetNetname()==net
    if net!='GND':assert mn['U1',net][0]==net;lines.append(net)
 record={'pair':i+1,'status':'all contacts coincide' if i<8 else 'FX23L axes aligned / 90deg / H=8mm / socket map TBD'}
 for prefix,h in [('control',A),('mate',B)]:record.update({prefix+'_'+k:v for k,v in h.items()})
 rows.append(record)
assert Counter(lines)==Counter(f'{fam}{i}' for fam in ['BL','NL','WL'] for i in range(32))
for cr,mr,x,y,d in MOUNTS+[KEY]:near(xy(fp(c,cr).GetPosition()),[x,y]);near(xy(fp(m,mr).GetPosition()),[x,y])
with (LAYOUT/'connector-map.csv').open('w') as f:wri=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');wri.writeheader();wri.writerows(rows)
# Exact transfer of all 64 copper lands and six mechanical holes from source native footprint.
source=p.FootprintLoad(str(BASE/'MIRA_Control/libraries/MIRA_RevA.pretty'),SOCKET);socket=fp(m,SOCKET_REF)
assert socket.GetLayer()==p.F_Cu;near(xy(socket.GetPosition()),list(SOCKET_POS));assert len(list(socket.Pads()))==70

def socket_geometry(f,offset):
 return sorted((a.GetNumber(),tuple(round(x-y,6) for x,y in zip(xy(a.GetPosition()),offset)),tuple(xy(a.GetSize())),tuple(xy(a.GetDrillSize())),int(a.GetAttribute()),a.GetLayerSet().FmtBin()) for a in f.Pads())
assert socket_geometry(source,[0,0])==socket_geometry(socket,SOCKET_POS)
for k,a in pads(socket).items():assert a.GetNetname().startswith('unconnected-(J3-');assert 'no_connect' in mn['J3',k][1]
assert all(not a.IsOnLayer(p.F_Paste) for a in pads(socket).values())
# Read actual trial tile bounds and density, not just the nominal target positions.
bounds=[];area=0
for r in refs:
 f=fp(c,r);near(xy(f.GetPosition()),intent[r][:2]);assert f.GetOrientationDegrees()==intent[r][2];bb=f.GetBoundingBox(False,False);b=[p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())];bounds.append(b);area+=(b[2]-b[0])*(b[3]-b[1])
union=[min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds)]
assert union[0]>=TILES[0][0] and union[1]>=TILES[0][1] and union[2]<=TILES[0][0]+TILE_SIZE[0] and union[3]<=TILES[0][1]+TILE_SIZE[1],union
for x,y in TILES:
 assert x>=BANK_BL0[0] and y>=BANK_BL0[1] and x+TILE_SIZE[0]<=BANK_BL0[2] and y+TILE_SIZE[1]<=BANK_BL0[3]
assert all(len(b.GetTracks())==0 for b in boards.values())
# Export only saved, actual geometry for review rendering.
geometry={}
for n,b in boards.items():
 selected=refs|{'J1800','J1801','H1800','H1801','H1802','U500','U800','U700','U100','U200','J700'}|{f'J{x}' for x in range(400,408)} if n=='Control' else {f.GetReference() for f in b.GetFootprints()} if n=='Crossbar' else {'J101','U1102'}|{f'J{x}' for x in range(4901,4909)}
 geometry[n]=[]
 for f in b.GetFootprints():
  if f.GetReference() not in selected:continue
  bb=f.GetBoundingBox(False,False);geometry[n].append({'ref':f.GetReference(),'value':f.GetValue(),'pos':xy(f.GetPosition()),'angle':f.GetOrientationDegrees(),'side':f.GetLayerName(),'bbox':[p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())],'pads':[{'pin':a.GetNumber(),'pos':xy(a.GetPosition()),'size':xy(a.GetSize()),'drill':xy(a.GetDrillSize()),'angle':a.GetOrientationDegrees(),'net':a.GetNetname()} for a in f.Pads()]})
(OUT/'geometry.json').write_text(json.dumps(geometry,indent=2));(LAYOUT/'geometry.json').write_text(json.dumps(geometry,indent=2))
report={'source_sha':json.loads((OUT/'start-state.json').read_text())['source_sha'],'KiCad':p.Version(),'all_boards_readable':True,'all_local_project_preferences_preserved':True,'Power_PCB_unchanged':True,'unchanged_Control_footprints':len(blocks((BASE/'MIRA_Control/MIRA_Control.kicad_pcb').read_text())),'AFE_components_placed':len(refs),'socket_contacts':64,'socket_NPTH':6,'socket_source_geometry_equal':True,'socket_BL_NL_WL_assignment':'TBD: 64-contact socket cannot be assumed to expose 96 independent lines','connector_pairs':10,'lines_verified_to_logical_boundary':len(lines),'PCB_to_schematic_nets_match':True,'AFE_actual_bbox':union,'AFE_sum_bbox_area_mm2':area,'AFE_4_blocks_fit_nominally':True,'AFE_four_tile_courtyard_bbox_fill_fraction':round(4*area/((BANK_BL0[2]-BANK_BL0[0])*(BANK_BL0[3]-BANK_BL0[1])),3),'routing_corridors_mm':{'between_tile_columns':5,'between_tile_rows':5,'west_bank_exit':6},'routing_proven':False,'tracks_added':0,'boards':{n:{'footprints':len(b.GetFootprints()),'pads':sum(len(list(f.Pads())) for f in b.GetFootprints()),'sha256':hashlib.sha256((BASE/f'MIRA_{n}/MIRA_{n}.kicad_pcb').read_bytes()).hexdigest()} for n,b in boards.items()}}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
