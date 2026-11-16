"""Review image from geometry re-read from saved KiCad PCB files. Requires Pillow."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
from interface_spec import OUT,PAIRS,MOUNTS,KEY
U=json.loads((OUT/'u1-constraints.json').read_text());G=json.loads((OUT/'geometry.json').read_text());im=Image.new('RGB',(2000,2320),'#f5f7fa');d=ImageDraw.Draw(im)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def t(x,y,s,size=18,col='#213749'):d.text((int(x),int(y)),s,fill=col,font=ImageFont.truetype(FONT,size))
def r(box,col,width=2,fill=None):d.rectangle(tuple(round(v) for v in box),outline=col,width=width,fill=fill)
t(55,25,'MIRA RevC | replaceable adapter interface v0.2 | FX23L A + B',31)
t(55,70,'Control top view: common XY in mm, +X right, +Y down, +Z towards viewer. Module F.Cu up; plugs B.Cu.',19)
s=6;ox=55;oy=100
pt=lambda x,y:(ox+s*x,oy+s*y)
def box(b,col,width=2,fill=None):r((*pt(b[0],b[1]),*pt(b[2],b[3])),col,width,fill)
box((10,20,230,158.2),'#b67a1a',4,'#fff0d8');box((50,20,230,158.2),'#168774',4,'#e2f2ee')
for b,label in [((125,25,165,58),'BL0-15'),((175,25,220,58),'BL16-31'),((130,100,167,145),'NL0-15'),((174,100,207,145),'NL16-31'),((130,148,207,155),'WL')]:
 box(b,'#89b0a9');t(*pt(b[0]+1,b[1]+1),label,15)
box((145,60,209,94),'#c5429a',3);box((147,62,207,92),'#7954a5',4)
for name,col in [('Power','#b47b21'),('Control','#176d79')]:
 for f in G[name]:
  if name=='Power' and f['ref'].startswith('J49'):continue
  b=f['bbox'];box(b,col,2);ref=f['ref']
  if name=='Control' and ref.startswith('J4'):ref+='/J'+str(int(ref[1:])+4501)
  t(*pt(b[0]+.4,b[1]+.3),ref,13,col)
for cr,mr,x,y,dia in MOUNTS+[KEY]:
 px,py=pt(x,y);d.ellipse((px-7,py-7,px+7,py+7),outline='#b83839' if mr=='H3' else '#475a80',width=2)
for x,y in [(55,25),(225,25),(55,150),(225,150)]:
 px,py=pt(x,y);d.ellipse((px-18,py-18,px+18,py+18),outline='#495b63',width=2)
t(1480,180,'PRESERVED FROM DAY 1',22)
for yy,ss in [(225,'Control: 180 x 138.2 mm'),(255,'Power: 220 x 138.2 mm'),(285,'Adapter: 60 x 30 mm'),(330,'Other 2332 Control parts unchanged.'),(360,'Power PCB byte-identical to day 1.'),(410,'A axes: (176, 68.5), 0 deg'),(440,'B axes: (180, 85.5), 0 deg'),(490,'Control S: F.Cu, faces up'),(520,'Adapter P: B.Cu, faces down'),(570,'96 lines: 32 BL + 32 NL + 32 WL'),(610,'Per pair: 48 lines + 22 GND'),(640,'+ 10 reserved NC + 4 power GND'),(690,'Signal pins: rows 1..40 / 41..80'),(730,'No die size / pad map assumed.'),(780,'Readme: dimensional audit, fit,'),(810,'key hardware and open questions.')]:t(1480,yy,ss,18)
t(55,1100,'Saved adapter PCB: real top-side obstructions; socket envelope and pad map remain TBD.',22)
t(1480,865,'TOP: 42 x 10.65 geometric band.',18,'#287b80')
t(1480,900,'Inset 0.5 => 41 x 9.65 (proposal).',18,'#356944')
t(1480,935,'18.9 x 30 central corridor also fits',18)
t(1480,965,'geometrically; edge clearance TBD.',18)
t(1480,1000,'Bottom bodies do not limit a',18)
t(1480,1030,'top-only housing. Pins/legs need fit.',18)
# Enlarged module panels. Back view mirrors X, as when looking directly at B.Cu.
for back,origin in [(False,(80,1220)),(True,(1080,1220))]:
 px0,py0=origin;ss=12
 def dp(x,y):return (px0+((354-x if back else x)-147)*ss,py0+(y-62)*ss)
 def db(b,col,width=2,fill=None):
  a=dp(b[0],b[1]);z=dp(b[2],b[3]);r((min(a[0],z[0]),min(a[1],z[1]),max(a[0],z[0]),max(a[1],z[1])),col,width,fill)
 t(px0-10,1155,'BOTTOM / looking at B.Cu (X mirrored)' if back else 'TOP / looking at F.Cu (+Z)',24,'#674696')
 db((147,62,207,92),'#7954a5',4,'#ebe7f4')
 for b in U['grip_zones']:db(b,'#64a88e',2,'#dbece4')
 def dashbox(b,col,width=2):
  aa=dp(b[0],b[1]);zz=dp(b[2],b[3]);l,h=min(aa[0],zz[0]),min(aa[1],zz[1]);rr,bb=max(aa[0],zz[0]),max(aa[1],zz[1])
  for x in range(round(l),round(rr),14):
   for y in [h,bb]:d.line((x,y,min(x+8,rr),y),fill=col,width=width)
  for y in range(round(h),round(bb),14):
   for x in [l,rr]:d.line((x,y,x,min(y+8,bb)),fill=col,width=width)
 if not back:
  # Under-board body projections are NOT top-side component keepouts.
  dashbox(U['nominal_vertical_corridor'],'#8caeb2',1)
  db(U['nominal_horizontal_band'],'#308f95',2,'#e1f0e9')
  db(U['planning_horizontal_band'],'#438d56',2,'#f4f5df')
  dashbox(U['current_reservation'],'#b6a1ba',1)
  t(*dp(159,73.4),'TOP socket / envelope TBD',17)
  t(*dp(159,76),'41 x 9.65 planning area',17,'#356944')
  t(*dp(159,78.5),'old 38 x 8 is a reservation',14,'#786783')
  for body in U['underside_bodies_dashed']:dashbox(body['bbox'],'#796896',2)
  # Copper and actual drilled holes on F.Cu, measured from saved PCB pad data.
  for a in U['power_PTH']:
   pp=dp(*a['pos']);rad=a['size'][0]*ss/2;hole=a['drill'][0]*ss/2
   d.ellipse((pp[0]-rad,pp[1]-rad,pp[0]+rad,pp[1]+rad),fill='#c18825',outline='#715820',width=1)
   d.ellipse((pp[0]-hole,pp[1]-hole,pp[0]+hole,pp[1]+hole),fill='white')
  for m in U['mounting_and_key']:
   db(m['reservation_bbox'],'#b83839' if m['kind']=='key' else '#425b82',2)
  l,top=dp(U['nominal_horizontal_band'][0],U['nominal_horizontal_band'][1]);rr,bot=dp(U['nominal_horizontal_band'][2],U['nominal_horizontal_band'][3])
  for x in [l,rr]:d.line((x,1205,x,top),fill='#308f95',width=1)
  d.line((l,1205,rr,1205),fill='#308f95',width=2)
  for x in [l,rr]:d.line((x,1200,x,1210),fill='#308f95',width=2)
  t((l+rr)/2-70,1182,'42 mm nominal',16,'#287b80')
  d.line((65,top,65,bot),fill='#308f95',width=2)
  for y in [top,bot]:d.line((60,y,l,y),fill='#308f95',width=1)
  t(5,(top+bot)/2-10,'10.65',16,'#287b80')

 for pair in PAIRS:
  x,y=pair['x'],pair['y'];f=next(f for f in G['Crossbar'] if f['ref']==pair['module'])
  if back:db(next(a['bbox'] for a in U['underside_bodies_dashed'] if a['ref']==pair['module']),'#796896',2,'#d0c4e0')
  if back:
   for a in f['pads']:
    ap=dp(*a['pos']);w,h=a['size'];col='#388477' if a['net']=='GND' else '#8c96a4' if a['net'].startswith('unconnected-') else '#b47e2a'
    if a['pin'] in ['P1','P2','P3','P4']:
     d.ellipse((ap[0]-8,ap[1]-8,ap[0]+8,ap[1]+8),fill=col,outline='#33494d',width=1)
    else:r((ap[0]-w*ss/2,ap[1]-h*ss/2,ap[0]+w*ss/2,ap[1]+h*ss/2),col,1,col)
   for pin in ['1','40','41','80']:
    one=next(a for a in f['pads'] if a['pin']==pin);ap=dp(*one['pos']);d.ellipse((ap[0]-5,ap[1]-5,ap[0]+5,ap[1]+5),fill='#ffe270');t(ap[0]-8,ap[1]-25 if int(pin)<=40 else ap[1]+10,pin,15,'#a04a12')
  lp=dp(x,y);t(lp[0]-70,lp[1]-10,pair['pair']+' / '+pair['module']+(' below' if not back else ''),16 if not back else 19)
 for cr,mr,x,y,dia in MOUNTS+[KEY]:
  pp=dp(x,y);rad=dia*ss/2;d.ellipse((pp[0]-rad,pp[1]-rad,pp[0]+rad,pp[1]+rad),fill='white',outline='#b83839' if mr=='H3' else '#425b82',width=3)
  t(pp[0]-14,pp[1]+18,'KEY' if mr=='H3' else mr,13)
 if back:
  t(px0,1595,'M2: (152,77), (202,77); key hole: (153,86); drill 2.2 mm',16)
  t(px0,1620,'9 x 10 mm grip windows on both short edges; unscrew and lift evenly +Z.',15)
 else:
  t(px0,1595,'Gold rings: PTH copper D1.6 / drill D1.2; blue/red: 5 x 5 reserves.',15)
  t(px0,1620,'Dashed purple: bottom bodies; cyan: 18.9 x 30 geometric corridor.',15)
# Installed side projection Y-Z. Both pairs projected onto one section, dimensions from spec.
t(55,1675,'INSTALLED / Y-Z projection (vertical scale exaggerated)',24)
yzero=1905;zs=10
sp=lambda y,z:(90+(y-55)*20,yzero-z*zs)
def side(y1,y2,z1,z2,col):
 a=sp(y1,z2);b=sp(y2,z1);r((*a,*b),col,1,col)
side(55,99,0,1.6,'#168774');side(62,92,9.6,11.2,'#7954a5')
for pair in PAIRS:
 y=pair['y'];side(y-5.25,y+5.25,1.6,7.4,'#c8b58a');side(y-3.3,y+3.3,2.75,9.6,'#a594bb');t(*sp(y-1,12.2),pair['pair'],18)
a=sp(97,1.6);b=sp(97,9.6);d.line((*a,*b),fill='#203344',width=2);t(b[0]+12,(a[1]+b[1])/2-12,'8 mm',21)
# Separate actual key section at X=153: no projected connector body at the key location.
t(1030,1680,'KEY SECTION / X=153 (different X from connectors)',21)
kx=1300; ks=20
kz=lambda z:1905-z*10
r((1130,kz(1.6),1480,kz(0)),'#168774',1,'#168774')
# Crossbar receiving NPTH D2.2 is shown as a real gap through the board.
for left,right in [(1130,kx-1.1*ks),(kx+1.1*ks,1480)]:r((left,kz(11.2),right,kz(9.6)),'#7954a5',1,'#7954a5')
r((kx-1*ks,kz(15.6),kx+1*ks,kz(1.6)),'#b83839',1,'#b83839')
def dim(x,z1,z2,label,right=True):
 y1,y2=kz(z1),kz(z2);d.line((x,y1,x,y2),fill='#263b4c',width=2)
 for y in [y1,y2]:d.line((x-7,y,x+7,y),fill='#263b4c',width=2)
 t(x+12 if right else x-100,(y1+y2)/2-10,label,18)
dim(1510,1.6,15.6,'14 mm',True);dim(1435,11.2,15.6,'4.4 mm',False)
# Datum and top level leader lines.
d.line((kx+22,kz(15.6),1550,kz(15.6)),fill='#a3484b',width=1)
d.line((1480,kz(1.6),1550,kz(1.6)),fill='#168774',width=2)
t(1610,1735,'Tip Z=15.6',17,'#a42f3b');t(1610,1770,'Adapter F.Cu Z=11.2',17)
t(1610,1805,'Adapter B.Cu Z=9.6',17);t(1610,1850,'DATUM: Control F.Cu Z=1.6',17,'#168774')
t(1030,1930,'14 mm is the exposed projection from Control F.Cu, NOT total pin length.',17)
t(1030,1960,'Installed: 14 = gap 8 + PCB 1.6 + protrusion 4.4 mm.',18)
t(55,1940,'Left: projected connector section; key is shown separately at X=153.',18)
t(55,1970,'8 mm is counted between Control F.Cu and adapter B.Cu.',18)
t(55,2025,'NOMINAL INSERTION / TOLERANCE AND FORCE CHECKS REMAIN OPEN',23)
for y,txt in [(2070,'Key tip enters the receiving hole at g = 14.00 mm.'),
              (2105,'Housing first-touch bound: g <= 12.65 nominal / <= 13.25 mm at height maxima.'),
              (2140,'Key entry precedes that bound by 1.35 nominal / 0.75 mm at height maxima.'),
              (2175,'Reference effective engagement: power starts near g=10.0, signal near g=9.5 mm (not guaranteed limits).'),
              (2220,'Nominal entry: YES. Guarantee requires H_min - tip chamfer - tilt budget > 13.25 mm; these tolerances are TBD.'),
              (2265,'Unverified key base/retention, tip chamfer, tilt, U1/socket height and extraction stroke remain TBD. No routed tracks yet.')]:t(55,y,txt,19)
im.save(OUT/'assembly-top.png')
