"""Russian assembly review and AFE close-up from re-read KiCad geometry, no invented chip mapping."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,math,sys
from trial_spec import *
G=json.loads((OUT/'geometry.json').read_text());V=json.loads((OUT/'verification.json').read_text());AF=set(json.loads((OUT/'afe-placement-intent.json').read_text()))
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n):return ImageFont.truetype(FONT,n)
def text(d,x,y,s,n=18,c='#213747'):d.text((int(x),int(y)),s,font=font(n),fill=c)
def rect(d,b,c,w=2,fill=None):d.rectangle(tuple(round(v) for v in b),outline=c,width=w,fill=fill)
def dash(d,b,c,w=2):
 x,y,X,Y=[round(z) for z in b]
 for a in range(x,X,14):
  for b in [y,Y]:d.line((a,b,min(a+8,X),b),fill=c,width=w)
 for a in range(y,Y,14):
  for b in [x,X]:d.line((b,a,b,min(a+8,Y)),fill=c,width=w)
def draw_fp(d,f,point,scale,labels=False,pads_only=False):
 b=f['bbox'];a=point(b[0],b[1]);z=point(b[2],b[3])
 if not pads_only:rect(d,(*a,*z),'#397580',1,'#e7eff1' if labels else None)
 for p in f['pads']:
  cx,cy=point(*p['pos']);w,h=p['size'];theta=math.radians(p['angle']);col='#438d77' if p['net']=='GND' else '#c18a35'
  if p['drill'][0]>0:
   rad=w*scale/2;d.ellipse((cx-rad,cy-rad,cx+rad,cy+rad),fill=col if p['pin'] else '#56718a',outline='#345568')
   rad=p['drill'][0]*scale/2;d.ellipse((cx-rad,cy-rad,cx+rad,cy+rad),fill='#f8fafb')
  else:
   pts=[]
   for xx,yy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]:pts.append((cx+scale*(xx*math.cos(theta)+yy*math.sin(theta)),cy+scale*(-xx*math.sin(theta)+yy*math.cos(theta))))
   d.polygon(pts,fill=col)
 if labels:
  xx,yy=point(*f['pos']);size=14 if f['ref'].startswith(('R','C')) else 17
  if f['ref'].startswith('U'):
   text(d,xx-34,yy-19,f['ref'],size);text(d,xx-42,yy+3,f['value'],12)
  else:text(d,xx-24,yy-8,f['ref'],size)
# Full-size readable view of the actual 84 components.
close=Image.new('RGB',(2200,1540),'#f5f7fa');dc=ImageDraw.Draw(close)
text(dc,55,25,'Пробная расстановка C_AFE_BL0_BL3 — 84 компонента на F.Cu',30)
text(dc,55,75,'Позиции и медные площадки перечитаны из рабочей PCB Control. Трасс нет; это примерка, не завершённый AFE.',18)
s=36;ox=80;oy=170;tx,ty=TILES[0]
pt=lambda x,y:(ox+(x-tx)*s,oy+(y-ty)*s)
rect(dc,(*pt(tx,ty),*pt(tx+48,ty+33.5)),'#638a8c',3)
for f in G['Control']:
 if f['ref'] in AF:draw_fp(dc,f,pt,s,True)
text(dc,80,1400,'Габарит ячейки 48 × 33,5 мм; фактический охват footprint 47,11 × 32,21 мм.',20)
text(dc,80,1440,'Оставлены проходы между четырьмя ячейками 5 мм и выход из банка 6 мм; разводимость ещё не доказана.',18)
for y,ss in [(170,'Состав по схеме:'),(210,'16 микросхем'),(245,'32 резистора'),(280,'32 конденсатора'),(315,'4 диода'),(390,'Общий ряд:'),(425,'U7001/U7002 OPA4192'),(460,'U7003 ADG442'),(495,'U7004 TMUX6112'),(570,'Четыре канала:'),(605,'INA296A2'),(640,'TLV3202'),(675,'SN74LVC1G74'),(745,'Шунты:'),(780,'R7017 / R7025'),(815,'R7033 / R7041'),(885,'Следующая проверка:'),(920,'Кельвиновский съём'),(955,'Петли ООС'),(990,'Развязка у выводов'),(1025,'Выходы BL / VADC / IADC'),(1100,'Прочие 3 повтора'),(1135,'показаны резервами,'),(1170,'их детали не двигались.')]:text(dc,1850,y,ss,18)
close.save(OUT/'afe-bl0-bl3.png');close.save(LAYOUT/'afe-bl0-bl3.png')
# Assembly overview.
im=Image.new('RGB',(2200,2050),'#f5f7fa');d=ImageDraw.Draw(im)
text(d,60,25,'MIRA RevC — примерка сокета ICS-CQFP64 и банка BL0–15',32)
text(d,60,75,'Сокет сверху, две FX23L снизу. 96 линий интерфейса сохранены; назначение 64 контактов сокета — TBD.',21)
scale=4.6;ox=70;oy=135;pt=lambda x,y:(ox+x*scale,oy+y*scale)
def box(b,c,w=2,fill=None):rect(d,(*pt(b[0],b[1]),*pt(b[2],b[3])),c,w,fill)
box((10,20,230,158.2),'#bb852e',4,'#fbefda')
poly=[pt(x,y) for x,y in CONTROL_PATH];d.polygon(poly,fill='#e2f0ed');d.line(poly+[poly[0]],fill='#218577',width=4)
text(d,310,190,'Контроллер Control',21,'#17786c');text(d,*pt(11,23),'Питание\nPower',17,'#a16b18')
# Function zones correspond to Dwgs.User rectangles in the saved Control PCB.
zones=[((61,32,116,62),'H745 + SDRAM\nU100 / U200','#7d9eae'),((70,78,115,109),'Zynq + DDR3L\nU500 / U800','#7d9eae'),((85,119,119,157),'FX20 + USB-C\nU700 / J700','#7d9eae'),(BANK_BL0,'BL0–15\nC_AFE_BL0_BL3..BL12_BL15','#66a48b'),((175,21,225,49),'BL16–31\nрезерв тесен','#b5a47e'),((121,21,169,49),'NL0–15\nрезерв тесен','#b5a47e'),((55,21,118,30),'NL16–31 / TBD','#b5a47e'),((55,165,85,239),'WL\nC_Rows0..7\nместа мало','#9a8db1')]
for b,label,col in zones:
 box(b,col,2);text(d,*pt(b[0]+1,b[1]+1),label,13)
for f in G['Power']:
 if f['ref'] in ['U1102','J101']:
  box(f['bbox'],'#b47a24',2);text(d,*pt(f['bbox'][0],f['bbox'][1]),f['ref'],12)
for f in G['Control']:
 if f['ref'] not in AF and not f['ref'].startswith('H'):
  box(f['bbox'],'#4f7b84',1);text(d,*pt(f['bbox'][0]+.3,f['bbox'][1]+.2),f['ref'],10)
box(REMOVAL,'#b05492',3);box(ADAPTER,'#76579a',4)
box(LID_APPROX,'#c18c40',1)
for cr,mr,x,y,dd in MOUNTS+[KEY]:
 pp=pt(x,y);rad=dd*scale/2;d.ellipse((pp[0]-rad,pp[1]-rad,pp[0]+rad,pp[1]+rad),fill='white',outline='#ad4444' if mr=='H3' else '#4b6689',width=2)
for i,(x,y) in enumerate(TILES):
 box((x,y,x+48,y+33.5),'#689a86' if i==0 else '#a9b9b3',2)
 if i>0:text(d,*pt(x+1,y+8),f'BL{4*i}–{4*i+3}\nрезерв, 84 детали\nне расставлены',14)
for f in G['Control']:
 if f['ref'] in AF:draw_fp(d,f,pt,scale)
text(d,*pt(91,165),'USB\nпроход\n20 мм',12,'#376b82')
text(d,100,1290,'Control: 180 × 225 мм, открытый проход USB-C сохраняет кромку Y=158,2.',18)
text(d,100,1325,'Нижний вылет относительно Power 86,8 мм: дополнительные опоры TBD.',18)
# Enlarged saved adapter top view.
px,py=1300,220;ss=8.5;mp=lambda x,y:(px+(x-ADAPTER[0])*ss,py+(y-ADAPTER[1])*ss)
def mb(b,c,w=2,fill=None):rect(d,(*mp(b[0],b[1]),*mp(b[2],b[3])),c,w,fill)
text(d,1260,130,'Переходник Crossbar: 80 × 94 мм',25,'#76579a')
text(d,1260,168,'Вид сверху / F.Cu; pin 1 сокета выделен',18)
mb(ADAPTER,'#76579a',4,'#eee9f4')
for b in GRIPS:mb(b,'#4b9b85',2,'#dcefe7');text(d,*mp(b[0]+2,b[1]+3),'Место для пальцев / захват',16,'#2d7864')
# Body and open-lid projections are approximate; the contact pattern is exact to the source footprint.
body=(152,82,192,132);mb(body,'#b68e3d',3,'#f1e6c6');text(d,*mp(164,101),'J3 — сокет\nICS-CQFP64\nКарта матрицы TBD',14)
for bb in [LID_APPROX,(152,76.05,192,139.532)]:dash(d,(*mp(bb[0],bb[1]),*mp(bb[2],bb[3])),'#c57839')
mb((163,76.05,181,79.55),'#c57839',2,'#e9cf9d');text(d,*mp(163,80),'Защёлка ≈',14,'#a9632e')
for f in G['Crossbar']:
 if f['ref'].startswith('J') and f['ref']!='J3':
  dash(d,(*mp(f['bbox'][0],f['bbox'][1]),*mp(f['bbox'][2],f['bbox'][3])),'#7c639b')
  for a in f['pads']:
   if a['drill'][0]>0:
    pp=mp(*a['pos']);rad=a['size'][0]*ss/2;d.ellipse((pp[0]-rad,pp[1]-rad,pp[0]+rad,pp[1]+rad),fill='#be9651');rad=a['drill'][0]*ss/2;d.ellipse((pp[0]-rad,pp[1]-rad,pp[0]+rad,pp[1]+rad),fill='white')
  pp=mp(*f['pos']);text(d,pp[0]-29,pp[1]-30,'FX23L\n'+('A' if f['ref']=='J1' else 'B')+' снизу',14,'#735794')
 elif f['ref']=='J3':
  draw_fp(d,f,mp,ss,pads_only=True)
  pp=mp(*next(a for a in f['pads'] if a['pin']=='1')['pos']);d.ellipse((pp[0]-6,pp[1]-6,pp[0]+6,pp[1]+6),fill='#fff276');text(d,pp[0]-18,pp[1]-25,'1',17,'#9b5625')
 else:
  a=next(a for a in f['pads'] if a['drill'][0]>0);pp=mp(*a['pos']);rad=a['drill'][0]*ss/2;d.ellipse((pp[0]-rad,pp[1]-rad,pp[0]+rad,pp[1]+rad),fill='white',outline='#a24248' if f['ref']=='H3' else '#426180',width=3);text(d,pp[0]-30,pp[1]+12,'Ключ' if f['ref']=='H3' else f['ref']+' M2',14)
text(d,1280,1045,'64 медных контакта + 6 отверстий сокета — исходный footprint.',17)
text(d,1280,1080,'Пунктир FX23L — снизу; оранжевый — примерка крышки APPROX.',17)
# Side section, socket-height evidence is explicitly approximate.
text(d,1270,1130,'Разрез: высоты сокета только по APPROX STEP',22)
z0=1535;zs=5.4;sp=lambda y,z:(1280+(y-60)*9,z0-z*zs)
def side(y1,y2,z1,z2,c):rect(d,(*sp(y1,z2),*sp(y2,z1)),c,1,c)
side(60,154,0,1.6,'#218577');side(60,154,9.6,11.2,'#76579a')
side(97,111,1.6,9.6,'#a293b1');side(82,132,11.2,22.4,'#bd9857')
d.line((*sp(128.5,20.6),*sp(139.5,57)),fill='#c77b3d',width=8)
text(d,*sp(85,26),'Закрыто ≈11,2 мм',17,'#996e30');text(d,*sp(68,54),'Открыто ≈45,8 мм / ≈105°',17,'#b36b30')
text(d,1280,1560,'Зазор Control–Crossbar 8 мм; крепёж сокета снизу — примерка TBD.',16)
text(d,1280,1595,'Штифт: 14 мм от F.Cu Control, выступ над модулем 4,4 мм.',17)
text(d,1280,1630,'Ход крышки, защёлка и усилие снятия требуют образца/чертежа.',17)
# Useful AFE preview plus room assessment; detailed image is separate.
text(d,90,1390,'Пробный блок BL0–BL3 — крупный вид в afe-bl0-bl3.png',23)
thumb=close.crop((70,155,1820,1400));thumb.thumbnail((730,520));im.paste(thumb,(90,1440))
for y,ss in [(1450,'84 детали: 16 U + 32 R + 32 C + 4 D.'),(1490,'Фактический охват: 47,11 × 32,21 мм.'),(1530,'Ещё 3 повтора помещаются по габаритам.'),(1570,'Проходы между ячейками: 5 мм.'),(1610,'Коридор выхода из банка: 6 мм.'),(1650,'Заполнение footprint: около 48% банка.'),(1700,'Полная трассировка пока не выполнена.'),(1740,'Петли ООС и кельвиновский съём — проверить.'),(1780,'BL16/NL/WL: резервы, вместимость TBD.')]:text(d,850,y,ss,18)
text(d,95,1970,'Источник: текущие PCB после сохранения и перечитывания KiCad 10.0.5. Локальные настройки .kicad_pro сохранены.',18)
text(d,95,2005,'Новые механические размеры, кроме исходных площадок/отверстий, — проектная примерка. Коммит и push не выполнялись.',18)
im.save(OUT/'assembly-top.png');im.save(LAYOUT/'assembly-top.png')
