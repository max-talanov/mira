"""Modify only the current day-1 interface and selected AFE footprints. No routing."""
import sys,re,json,uuid,shutil,hashlib,xml.etree.ElementTree as ET,math,csv
from pathlib import Path
from trial_spec import *
sys.path.insert(0,str(LAYOUT))
from sexpr_tools import children,reference,quote as q
from pcb_text_helpers import connector,grect,gtext,mounting,uid

def replace_children(s,replacements):
 for a,b,val in sorted(replacements,reverse=True):s=s[:a]+val+s[b:]
 return s

def rotate_point(x,y,angle):
 t=math.radians(angle);return (round(x*math.cos(t)+y*math.sin(t),6),round(-x*math.sin(t)+y*math.cos(t),6))

def rotate_foot(s,x,y,angle,oldpos=None,oldangle=0,refs_dwgs=False):
 # Pads use footprint-local XY and absolute orientation. Footprint-zone polygons use board XY.
 nodes=list(children(s));repls=[];delta=angle-oldangle
 for a,b,n in nodes:
  if n.startswith('(at '):repls.append((a,b,f'(at {x} {y} {angle})'))
  elif n.startswith('(pad '):
   m=re.search(r'\(at\s+([-+.\d]+)\s+([-+.\d]+)(?:\s+([-+.\d]+))?\)',n)
   if m:
    rot=float(m[3] or 0)+delta;n=n[:m.start()]+f'(at {m[1]} {m[2]} {rot})'+n[m.end():]
   repls.append((a,b,n))
  elif n.startswith('(zone '):
   ox,oy=oldpos
   def move(m):
    xx,yy=rotate_point(float(m[1])-ox,float(m[2])-oy,delta);return f'(xy {x+xx:.6f} {y+yy:.6f})'
   repls.append((a,b,re.sub(r'\(xy\s+([-+.\d]+)\s+([-+.\d]+)\)',move,n)))
  elif refs_dwgs and n.startswith('(property "Reference"'):
   n=re.sub(r'\(layer "[^"]+"\)','(layer "Dwgs.User")',n,1);repls.append((a,b,n))
  elif refs_dwgs and n.startswith('(property "Value"'):
   if '(hide yes)' not in n:n=n.rstrip()[:-1]+' (hide yes))'
   repls.append((a,b,n))
 return replace_children(s,repls)

# Install a local socket library with its 64 pressure contacts, six NPTH and both approximate STEP views.
lib=BASE/'MIRA_Crossbar/libraries/MIRA_Module.pretty';models=BASE/'MIRA_Crossbar/libraries/MIRA_Module.3dshapes';models.mkdir(exist_ok=True)
source=BASE/'MIRA_Control/libraries/MIRA_RevA.pretty'/(SOCKET+'.kicad_mod')
canonical=source.read_text().replace('libraries/MIRA_RevA.3dshapes/','libraries/MIRA_Module.3dshapes/')
(lib/(SOCKET+'.kicad_mod')).write_text(canonical)
for suffix in ['_APPROX.step','_APPROX_OPEN.step']:
 shutil.copy2(BASE/'MIRA_Control/libraries/MIRA_RevA.3dshapes'/(SOCKET+suffix),models/(SOCKET+suffix))
# Extract the whole repeated sheet from actual schematic instances, not reference ranges.
parts={}
for _,_,s in children((BASE/'MIRA_Control/C_AFE_BL0_BL3.kicad_sch').read_text()):
 if s.startswith('(symbol (lib_id'):
  r=re.search(r'\(property "Reference" "([^"]+)"',s)[1];parts[r]=re.search(r'\(property "Value" "([^"]+)"',s)[1]
assert len(parts)==84
# One shared driver/switch row and four matched sensing/protection columns. Coordinates relative to a 48x33.5 tile.
placement={};tx,ty=TILES[0];dx,dy=tx-121,ty-21
for r,x,y,a in [('U7001',127,26,0),('U7002',137,26,0),('U7003',149,26,90),('U7004',163,26,0)]:placement[r]=[x+dx,y+dy,a]
for ch in range(4):
 cx=127+12*ch
 for j,(y,off) in enumerate([(34,0),(41.3,0),(47,-1.5)]):placement[f'U{7005+3*ch+j}']=[cx+off+dx,y+dy,0]
 placement[f'D{7001+ch}']=[cx+3.5+dx,47+dy,0]
 sites=[]
 for xx in [122.2+12*ch,131.8+12*ch]:
  sites += [(xx,y,90) for y in [33,36.5,40,43.5]]
 sites += [(xx+12*ch,y,0) for y in [50.7,53.1] for xx in [123,127,131]]
 refs=[f'R{i}' for i in range(7017+8*ch,7025+8*ch)]+[f'C{i}' for i in range(7085+6*ch,7091+6*ch)]
 for r,(x,y,a) in zip(refs,sites):placement[r]=[x+dx,y+dy,a]
for r,x,y in [('C7109',125,30.1),('C7110',129,30.1),('C7111',135,30.1),('C7112',139,30.1),('C7113',141.8,22.4),('C7114',156.2,22.4),('C7115',161,30.1),('C7116',165,30.1)]:placement[r]=[x+dx,y+dy,0]
assert set(parts)==set(placement)
(OUT/'afe-placement-intent.json').write_text(json.dumps(placement,indent=2))
with (OUT/'afe-block-members.csv').open('w') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['sheet','ref','value','x_mm','y_mm','angle'])
 for r in sorted(parts):w.writerow(['C_AFE_BL0_BL3',r,parts[r],*placement[r]])

for module in [False,True]:
 project='MIRA_Crossbar' if module else 'MIRA_Control';path=BASE/project/(project+'.kicad_pcb');raw=path.read_text()
 # Work from the preserved current board on each rerun; never rebuild from HEAD.
 raw=(OUT/'before'/(project+'.kicad_pcb')).read_text()
 changes=[]
 oldrefs={'J1','J2','H1','H2','H3'} if module else {'J1800','J1801','H1800','H1801','H1802'}
 for a,b,n in children(raw):
  if n.startswith('(gr_'):changes.append((a,b,''))
  elif n.startswith('(footprint '):
   r=reference(n)
   if r in oldrefs:changes.append((a,b,''))
   elif not module and r in placement:
    m=re.search(r'\(at\s+([-+.\d]+)\s+([-+.\d]+)(?:\s+([-+.\d]+))?\)',n);x,y,ang=placement[r];changes.append((a,b,rotate_foot(n,x,y,ang,oldpos=(float(m[1]),float(m[2])),oldangle=float(m[3] or 0),refs_dwgs=True)))
 raw=replace_children(raw,changes)
 additions=[]
 # Fetch actual existing connector pad nets. Interface assignment never changes.
 for pair in PAIRS:
  ref=pair['module' if module else 'control'];before=(OUT/'before'/(project+'.kicad_pcb')).read_text()
  old=next(s for _,_,s in children(before) if s.startswith('(footprint ') and reference(s)==ref)
  nets={re.match(r'\(pad "([^"]+)"',s)[1]:re.search(r'\(net "([^"]+)"\)',s)[1] for _,_,s in children(old) if s.startswith('(pad "') and re.match(r'\(pad "([^"]+)"',s) and re.search(r'\(net "([^"]+)"\)',s)}
  f=connector(module,ref,pair['x'],pair['y'],nets,True)
  f=rotate_foot(f,pair['x'],pair['y'],pair['angle'],oldpos=(pair['x'],pair['y']),refs_dwgs=True)
  additions += [f,gtext(f'FX23L {pair["pair"]}: {ref}',pair['x'],pair['y']-24,size=.8)]
 for cr,mr,x,y,d in MOUNTS:additions.append(mounting(mr if module else cr,x,y))
 cr,mr,x,y,d=KEY;additions.append(mounting(mr if module else cr,x,y,True,not module))
 additions += [gtext('Вид сверху: X вправо, Y вниз; размеры мм',102,15,size=1)]
 if module:additions.append(grect(ADAPTER,layer='Edge.Cuts'))
 else:
  for a,z in zip(CONTROL_PATH,CONTROL_PATH[1:]+CONTROL_PATH[:1]):additions.append(f'(gr_line (start {a[0]} {a[1]}) (end {z[0]} {z[1]}) (stroke (width .1) (type default)) (layer "Edge.Cuts") (uuid "{uid(str(a)+str(z))}"))')
  additions.append(gtext('Открытый USB-проход 20 мм / штекер TBD',100,200,size=.7))
 for box in GRIPS:additions.append(grect(box,'ЗАХВАТ: снять вверх +Z',layer='Dwgs.User'))
 if module:
  # Retain every source contact and hole exactly; only add reference/path and explicitly TBD nets.
  f=canonical;first=next((a,b,s) for a,b,s in children(f) if s.startswith('(layer '));f=f[:first[1]]+f'\n(at {SOCKET_POS[0]} {SOCKET_POS[1]}) (uuid "{uid("socket-J3")}") (path "/fe09b8b1-4cb9-5c2a-ab95-aa43c2c9d5fa/{uid("socket-J3")}")'+f[first[1]:]
  f=f.replace(f'(footprint "{SOCKET}"',f'(footprint "MIRA_Module:{SOCKET}"',1).replace('"REF**"','"J3"',1)
  edits=[]
  for a,b,n in children(f):
   if n.startswith(('(version ','(generator ')):edits.append((a,b,''))
   elif n.startswith('(pad "'):
    num=re.match(r'\(pad "([^"]*)"',n)[1]
    if num:n=n[:-1]+f' (net "unconnected-(J3-CONTACT_{num}-Pad{num})") (pinfunction "CONTACT_{num}") (pintype "passive"))';edits.append((a,b,n))
  f=replace_children(f,edits);additions.append(f)
  additions += [grect(LID_APPROX,'Крышка / защёлка: оценка STEP, TBD'),gtext('J3 сокет ICS-CQFP64 / 64 контакта',172,156,size=.8),gtext('BL/NL/WL -> J3: TBD, матрица не подтверждена',172,159,size=.8)]
 else:
  additions += [grect(ADAPTER,'Переходник Crossbar 80x94 / зазор 8 мм'),grect(REMOVAL,'Снятие +Z / пальцы / высоты TBD'),grect(LID_APPROX,'Открытие крышки: только APPROX STEP'),grect((61,32,116,62),'100_MCU_POWER_CLOCKS_AND_DEBUG / U100 H745\n200_MCU_FMC_AND_SDRAM / U200'),grect((70,78,115,109),'C_SOC0..2 / U500 Zynq\nC_DDR / U800 DDR3L'),grect((85,119,119,157),'C_FX20 / U700\nC_USB_C / J700'),grect(BANK_BL0,'BL0..15: C_AFE_BL0_BL3..C_AFE_BL12_BL15\nU7001..U7064; C_Bank0: U1000/U2000/U2001'),grect((175,21,225,49),'BL16..31 / U7065..U7128\nC_Bank1: U1001/U2002/U2003; резерв тесен'),grect((121,21,169,49),'NL0..15 / U7129..U7192\nC_Bank2 / U1002/U2004/U2005; TBD'),grect((55,21,118,30),'NL16..31 / C_AFE_NL16_NL19..NL28_NL31\nU7193..U7256 / C_Bank3; места мало'),grect((55,165,85,239),'WL / C_Rows0..7\nU7273..U7288 / U7331..U7378\nC_GROUP_WORDLINES; вместимость TBD'),grect((115,164,121,239),'Коридор к FX23L A'),gtext('Вылет Control ниже Power: дополнительные опоры TBD',140,243,size=.8)]
  for i,(x,y) in enumerate(TILES):
   additions.append(grect((x,y,x+TILE_SIZE[0],y+TILE_SIZE[1]),'BL0..3: 84 детали' if i==0 else f'Резерв BL{4*i}..{4*i+3}: 84 детали, не расставлены'))
 raw=raw.rstrip()[:-1]+'\n'+'\n'.join(additions)+'\n)\n';raw=re.sub(r'(?m)^[ \t]+$','',raw);path.write_text(raw)
print('Updated current Control and Crossbar; socket 64+6; 84 AFE placements; no tracks; Power and local project settings unchanged.')
