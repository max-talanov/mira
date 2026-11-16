"""Render review from geometry.json re-read from the saved KiCad boards. Pillow."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json
P=Path(__file__).resolve().parent; g=json.loads((P/'geometry.json').read_text())
im=Image.new('RGB',(1800,1440),'#f5f7fa');d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def t(x,y,s,size=20,color='#203344'):d.text((x,y),s,font=ImageFont.truetype(font,size),fill=color)
s=6; ox=100;oy=100
def box(b,color,width=3,fill=None):d.rectangle((ox+b[0]*s,oy+b[1]*s,ox+b[2]*s,oy+b[3]*s),outline=color,width=width,fill=fill)
def label(b,txt,color='#203344',size=16):t(ox+b[0]*s+3,oy+b[1]*s+3,txt,size,color)
t(55,20,'MIRA-01.02.00 | Draft assembly | view from Control F.Cu',30)
t(55,65,'mm; O=(0,0), +X right, +Y down, +Z towards viewer. Geometry read from saved PCBs.',18)
box((10,20,230,158.2),'#c07c16',4,'#fff0d8');box((50,20,230,158.2),'#168774',4,'#e2f2ee')
for b,txt in [((125,25,165,58),'BL0-15'),((175,25,220,58),'BL16-31'),((130,100,167,145),'NL0-15'),((174,100,207,145),'NL16-31'),((130,148,207,155),'WL'),((132,94,207,98),'routes to J1800')]:
 box(b,'#86aba5',2);label(b,txt,size=15)
box((145,60,209,94),'#bd4295',3)
box((147,62,207,92),'#7954a5',4)
t(ox+147*s,oy+63*s,'Crossbar 60 x 30',16,'#674394')
t(ox+146*s,oy+89*s,'Removal +Z; height TBD',14,'#a5267b')
for n,color in [('Power','#ba7819'),('Control','#176e7a')]:
 for f in g[n]:
  if n=='Power' and f['ref'].startswith('J49'):continue
  b=f['bbox'];box(b,color,2)
  txt=f['ref']
  if n=='Control' and txt.startswith('J4'):txt+='/J'+str(int(txt[1:])+4501)
  label(b,txt,color,14)
for x,y in [(55,25),(225,25),(55,150),(225,150),(154,67),(200,67)]:
 d.ellipse((ox+(x-3)*s,oy+(y-3)*s,ox+(x+3)*s,oy+(y+3)*s),outline='#3b4e55',width=2)
box((15,55,40.4,105.8),'#b34821',4);label((15,65,40,100),'Cincon\nH 12.7\n25.4 x\n50.8',size=17)
d.line((ox,oy,ox+100,oy),fill='#203344',width=3);d.line((ox,oy,ox,oy+90),fill='#203344',width=3)
t(ox+105,oy-12,'+X',16);t(ox-30,oy+90,'+Y',16);t(ox-25,oy-25,'O',16)
t(1510,160,'OUTLINES',22)
for y,txt,col in [(205,'Control: 180 x 138.2','#168774'),(240,'Power: 220 x 138.2','#ba7819'),(275,'Crossbar: 60 x 30','#7954a5')]:t(1510,y,txt,16,col)
t(1510,335,'Standoffs: marks only',16);t(1510,365,'Drills / heights: TBD',16)
t(1510,420,'B.Cu Control headers',16);t(1510,450,'face F.Cu Power sockets.',16)
t(1510,510,'Crossbar transform:',16);t(1510,540,'X=x; Y=164-y;',16);t(1510,570,'F.Cu faces down.',16)
t(1510,650,'U1 size / bonding: TBD',16)
t(1510,710,'Only key parts shown.',16);t(1510,740,'Remaining staging stays',16);t(1510,770,'outside / unplaced.',16)
t(55,1080,'SIDE SECTION / X-Z (Y projected; vertical scale exaggerated)',24)
# Side: top face Power z=-12, bottom face Control z=0; Crossbar F-facing-down z=4.6.
z0=1240;zs=6
sx=lambda x:100+x*6
sz=lambda z:z0-z*zs
def side(x1,x2,z1,z2,col):d.rectangle((sx(x1),sz(z2),sx(x2),sz(z1)),fill=col)
side(10,230,-13.6,-12,'#c07c16');side(50,230,0,1.6,'#168774');side(147,207,4.6,6.2,'#7954a5');side(15,40.4,-12,.7,'#b34821')
for x in [65,122,215]:side(x-1.5,x+1.5,-12,0,'#69838b')
side(153,201,1.6,4.6,'#b2a1c4')
d.line((sx(45),sz(-12),sx(45),sz(0)),fill='#203344',width=2)
t(sx(47),sz(-6)-10,'12 mm face-to-face target',16)
t(sx(12),1140,'Cincon 12.7 mm; 9.6 mm lateral gap to Control',18,'#a33f20')
t(sx(145),1120,'FX8 nominal 3 mm; exact BOM / tolerance TBD',16,'#674394')
t(55,1360,'1.6 mm PCB thickness from files. Samtec assembled height, other component heights and extraction stroke: TBD.',18)
t(55,1390,'Draft mechanical fit, no routing. Reservations and standoff circles are on Dwgs.User, not fabrication holes or keepouts.',17)
im.save(P/'assembly-top.png')
