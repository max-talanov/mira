
from pathlib import Path as _P
import json as _J, hashlib as _H
_o=_P(__file__).resolve().parents[1];_r=_P(__file__).resolve().parents[4]
for _pr,_c in _J.loads((_o/'validation.json').read_text())['checks'].items():
 assert _H.sha256((_r/_pr/(_pr+'.kicad_pcb')).read_bytes()).hexdigest()==_c['pcb_sha256'], 'Saved PCB changed: re-export geometry before using snapshot tools'

from pathlib import Path
import json,math,csv
from PIL import Image,ImageDraw,ImageFont
import gzip
R=Path(__file__).resolve().parents[4];O=R/'review/layout/MIRA-01.01.00';D=json.loads(gzip.decompress((O/'checks/boards.json.gz').read_bytes()));A=json.loads((O/'assembly-checks.json').read_text());FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def start(w,h):
 im=Image.new('RGB',(w,h),'#f5f7fa');return im,ImageDraw.Draw(im)
def txt(d,x,y,s,n=18,col='#183142'):d.text((round(x),round(y)),s,font=ImageFont.truetype(FONT,n),fill=col)
def rect(d,bb,c,w=2,fill=None):d.rectangle(tuple(round(v) for v in bb),outline=c,width=w,fill=fill)
def fp(pr,ref):return next(f for f in D[pr]['footprints'] if f['ref']==ref)
def circle(d,q,r,c,w=2):d.ellipse((q[0]-r,q[1]-r,q[0]+r,q[1]+r),outline=c,width=w)
C={'MIRA_Control':'#187b65','MIRA_Power':'#ba8124','MIRA_Crossbar':'#7453a4'}
im,d=start(2300,2050);txt(d,50,25,'MIRA-01.01.00 | TOP: Control F.Cu | saved PCB geometry',30)
txt(d,50,70,'mm: +X right, +Y down, +Z towards viewer. Crossbar transparent: components underneath remain visible.',19)
s=6;pt=lambda x,y:(70+s*(x-10),130+s*(y-20));bb=lambda b:(*pt(*b[:2]),*pt(*b[2:]))
for pr in ['MIRA_Power','MIRA_Control']:
 poly=D[pr]['outlines'][0];d.polygon([pt(*p) for p in poly],fill='#f3ead8' if pr=='MIRA_Power' else '#e3f1e9',outline=C[pr]);d.line([pt(*p) for p in poly+[poly[0]]],fill=C[pr],width=4)
for q in json.loads((O/'planning-zones.json').read_text()):
 if q['name'].startswith(('CH','DAC','REF','FORMING')):
  rect(d,bb(q['bounds_mm']),'#6b9e91',2,'#eff6ef');x,y=pt(q['bounds_mm'][0]+1,q['bounds_mm'][1]+2);txt(d,x,y,q['name'],17)
  if q['name'].startswith('CH'):txt(d,x,y+35,'F + B allocation',17);txt(d,x,y+65,'56 x 112 mm / side',16);txt(d,x,y+94,'PRELIM / ECO #6',17,'#ac4137')
for pr,refs in [('MIRA_Control',['U30001','U40001','U110001','U140001','U180001','U50001','U150001','J50001','J190001']),('MIRA_Power',['U110001','J30001'])]:
 for ref in refs:
  f=fp(pr,ref);rect(d,bb(f['bbox']),C[pr],2,'#d8dee5');x,y=pt(*f['xy']);txt(d,x+7,y-8,ref,15);txt(d,x+7,y+11,{'U30001':'STM32H745','U40001':'SDRAM','U110001':'Zynq' if pr=='MIRA_Control' else 'Cincon','U140001':'DDR3L','U180001':'FX20','U50001':'MCU QSPI','U150001':'Zynq QSPI','J50001':'microSD','J190001':'USB-C','J30001':'24 V'}[ref],14)
for pr,refs in [('MIRA_Control',['J70001','J80001','J80002','J80003','J80004','J160001','J90001','J90002'])]:
 for i,ref in enumerate(refs,1):
  f=fp(pr,ref);rect(d,bb(f['bbox']),'#557d9a',2);x,y=pt(*f['xy']);txt(d,x+6,y,'PC'+str(i),15,'#243f69')
rect(d,bb([132,60,212,154]),C['MIRA_Crossbar'],5);rect(d,bb([148,72,196,143]),'#cf7b29',3);txt(d,*pt(152,74),'#2 LID APPROX',18,'#a76019')
f=fp('MIRA_Crossbar','J10003');rect(d,bb(f['bbox']),C['MIRA_Crossbar'],2);txt(d,*pt(151,95),'#1 J10003 socket',18)
for tag,ref,mate in [('A','J580001','J10001'),('B','J580002','J10002')]:
 f=fp('MIRA_Control',ref);rect(d,bb(f['bbox']),'#88468d',3);x,y=pt(*f['xy']);txt(d,x-36,y-20,tag,22);one=next(p for p in f['pads'] if p['number']=='1')['xy'];circle(d,pt(*one),5,'#bd2536',3)
for pr in D:
 for f in D[pr]['footprints']:
  if f['ref'].startswith('H'):
   if pr=='MIRA_Power' and f['ref'].startswith('H91'):continue
   circle(d,pt(*f['xy']),9,'#334f61',3)
txt(d,*pt(63,292),'#3 chassis supports required',17,'#a74238')
txt(d,*pt(18,132),'USB <-',17);txt(d,*pt(103,16),'SD -Y',17)
x=1510;y=135
for line in ['ACTUAL BOARD EXTENTS','Control: (50,20)..(230,290)','180 x 270 mm / t=1.6','Power: (10,20)..(230,158.2)','220 x 138.2 mm / t=1.6','Crossbar: (132,60)..(212,154)','80 x 94 mm / t=1.6']:
 txt(d,x,y,line,22);y+=38
y+=20
for line in ['10 MATING PAIRS / XY MATCH','PC1 J70001 / J220001','PC2 J80001 / J230001','PC3 J80002 / J230002','PC4 J80003 / J230003','PC5 J80004 / J230004','PC6 J160001 / J230005','PC7 J90001 / J240001','PC8 J90002 / J240002','A J580001 / J10001','B J580002 / J10002']:
 txt(d,x,y,line,21);y+=35
y+=25
for line in ['OPEN ITEMS (same numbers in journal)','#1 Socket U10001 / physical J10003 ECO','#2 Exact lid, screws, mating CAD / fit','#3 Base supports below Control tail','#4 Samtec insertion / 12 mm hardware','#5 Cable shells / service bend radii','#6 CH96 -> CH48 ECO before placement']:
 txt(d,x,y,line,20,'#a44838' if line.startswith('#') else '#183142');y+=40
txt(d,x,y+20,'54 placed models; parked parts hidden.',19);txt(d,x,y+54,'Analog occupancy ~41% courtyard area',19);txt(d,x,y+86,'of two-sided reserve, routing TBD.',19)
txt(d,60,1940,'Planning frames are Dwgs.User; service paths Cmts.User. NPTH holes are real, not drawn circles.',20)
im.save(O/'views/assembly-top.png')
# Side projection from -Y; CAD Y=-KiCad Y only in STEP.
im,d=start(2300,1150);txt(d,55,25,'MIRA-01.01.00 | SIDE PROJECTION from -Y | X right, Z up | mm',29);txt(d,55,70,'Projection of all Y, not a section. Nominal envelopes and provisional hardware; enclosure not defined.',20)
sx=7;sz=12;pt=lambda x,z:(60+sx*(x-10),820-sz*z);bb=lambda b:(*pt(b[0],b[3]),*pt(b[2],b[1]))
for name,x1,x2,z1,z2 in [('Power',10,230,-13.6,-12),('Control',50,230,0,1.6),('Crossbar',132,212,9.6,11.2)]:rect(d,bb([x1,z1,x2,z2]),C['MIRA_'+name],3,C['MIRA_'+name]);txt(d,*pt(x2+2,z2),name+' '+str(z1)+'..'+str(z2),18)
cin=A['cincon']['bounds_mm'];rect(d,bb([cin[0],cin[2],cin[3],cin[5]]),'#4c5666',3,'#a7afbc');txt(d,*pt(12,5),'U110001 Cincon',17);txt(d,*pt(15,-19),'H12.7 + leads',16)
rect(d,bb([152,11.2,192,22.4]),'#ad7c29',3,'#d2ad68');txt(d,*pt(151,25),'J10003 CLOSED H11.2 APPROX',18)
rect(d,bb([152,11.2,192,56.984]),'#dc8d3b',2);txt(d,*pt(125,61),'#2 OPEN top Z~56.98 / lid model APPROX',19)
for x in [140,204]:
 rect(d,bb([x-5.25,1.6,x+5.25,7.4]),'#795398',2,'#bba5cc');rect(d,bb([x-3.3,2.75,x+3.3,9.6]),'#795398',2)
for x in [136,206]:rect(d,bb([x-2.5,-12,x+2.5,0]),'#788796',2,'#bcc6cf');rect(d,bb([x-2,1.6,x+2,9.6]),'#788796',2,'#bcc6cf')
rect(d,bb([207,1.6,209,15.6]),'#bd3743',2,'#d3a6aa');txt(d,*pt(191,34),'KEY top Z15.6',17)
# Cincon lateral gap dimension.
a,b=pt(40.4,2),pt(50,2);d.line((a,b),fill='#bd3743',width=3);txt(d,a[0]-70,a[1]-45,'9.60 mm',19,'#ad3441')
x=1730;y=150
for s in ['SURFACE GAPS','Power F -> Control B: 12 mm','Control F -> Crossbar B: 8 mm','All PCB thicknesses: 1.6 mm','','Cincon top Z=+0.70 mm','above Control B plane,','but XY clear by 9.60 mm.','','#3 Tail support -> base REQUIRED','#4 Samtec depth ~4.89 mm','final hardware / tolerance TBD','','Module: remove M2 screws,','lift both grips evenly +Z.','Lift >=6 mm to clear key','plus tolerance; no cable pull.']:
 txt(d,x,y,s,19);y+=34
im.save(O/'views/assembly-side.png')
# Two direct module views: X mirrored on back, no double flip in geometry.
im,d=start(2300,1660);txt(d,55,25,'MIRA-01.01.00 | CROSSBAR / CQFP64 | actual saved PCB XY',30);txt(d,55,72,'Top F.Cu up. Bottom: looking directly at B.Cu, Xdisplay=344-X (mirrored). +Z lift is out of top view.',20)
for back,ox in [(False,80),(True,1230)]:
 sc=10;pt=lambda x,y:(ox+sc*((344-x if back else x)-132),190+sc*(y-60));bbox=lambda b:(min(pt(b[0],b[1])[0],pt(b[2],b[3])[0]),pt(b[0],b[1])[1],max(pt(b[0],b[1])[0],pt(b[2],b[3])[0]),pt(b[2],b[3])[1])
 txt(d,ox,130,'BOTTOM B.Cu / X MIRRORED' if back else 'TOP F.Cu / +Z REMOVE',25)
 rect(d,bbox([132,60,212,154]),'#7453a4',4,'#eee9f5')
 for f in D['MIRA_Crossbar']['footprints']:
  if f['ref'].startswith('J'):
   visible=(f['side']=='B.Cu')==back;rect(d,bbox(f['bbox']),'#7453a4' if visible else '#9eabb1',3 if visible else 1,'#d6c7e6' if visible else None)
   x,y=pt(*f['xy']);txt(d,x-65,y-25,f['ref'],20)
  for p in f['pads']:
   if not p['number'] or p['type']==2:
    circle(d,pt(*p['xy']),6,'#3d5063',2)
   elif p['number']!='1':
    x,y=pt(*p['xy']);d.ellipse((x-2,y-2,x+2,y+2),fill='#a56325')
   elif p['number']=='1':circle(d,pt(*p['xy']),8,'#c52d40',3);x,y=pt(*p['xy']);txt(d,x+10,y,'1',22,'#c52d40')
 if not back:
  rect(d,bbox([148,72,196,143]),'#d38b32',2);txt(d,*pt(151,69),'#2 LID APPROX',18);txt(d,*pt(152,65),'GRIP +Z',21);txt(d,*pt(152,146),'GRIP +Z',21)
 else:txt(d,*pt(186,80),'#2 SOCKET SCREWS',18)
 txt(d,ox,1170,'A: (140,102), 90deg; B: (204,106), 90deg',18)
 txt(d,ox,1208,'Socket centre (172,107), angle0; pin1 (161.5,99.5)',18)
 txt(d,ox,1246,'H1 (136,66), H2 (206,149), key H3 (208,66)',18)
for y,s in [(1350,'#1 32 BL + 8 NL + 8 WL accepted. U10001 holds logical map; J10003 is the single physical socket, NC trial UUID.'),(1390,'#2 Six socket NPTH retained. Underside screws: install/remove on detached module; exact screw head and lid path TBD.'),(1430,'Remove M2 hold-downs, lift evenly by both edge grips +Z >=6mm plus tolerance. Check mating force on physical sample.'),(1470,'Closed socket projection 40 x 55.95mm; open lid height ~45.784mm APPROX. No exact-fit certification from envelope models.')]:txt(d,55,y,s,19)
im.save(O/'views/module-top-bottom.png')
