"""Update only the current local interface; unaffected PCB S-expressions are preserved.
KiCad 10 native syntax. Canonical footprints checked against individual Hirose drawings from Downloads.
"""
import uuid,re,json,hashlib,xml.etree.ElementTree as ET
from interface_spec import BASE,OUT,PAIRS,MOUNTS,KEY,POWER_PINS,OUTLINE
from sexpr_tools import children,reference,quote as q
NS=uuid.UUID('dfbf2968-72be-46f0-a606-091651de0c21')
def uid(s):return str(uuid.uuid5(NS,s))
def prop(k,val,x,y,layer,hide=False):return f'(property {q(k)} {q(val)} (at {x} {y} 0) (layer {q(layer)}) {"(hide yes)" if hide else ""} (effects (font (size .8 .8) (thickness .12))))'
def frect(x,y,X,Y,layer):return f'(fp_rect (start {x} {y}) (end {X} {Y}) (stroke (width .1) (type default)) (fill none) (layer {q(layer)}))'
def grect(box,label=None,layer='Dwgs.User'):
 x,y,X,Y=box;s=f'(gr_rect (start {x} {y}) (end {X} {Y}) (stroke (width .15) (type default)) (fill none) (layer {q(layer)}) (uuid "{uid(str(box)+str(label)+layer)}"))'
 return s+(gtext(label,(x+X)/2,(y+Y)/2) if label else '')
def gtext(s,x,y,layer='Dwgs.User',size=.8):return f'(gr_text {q(s)} (at {x} {y}) (layer {q(layer)}) (uuid "{uid(s+str(x)+str(y)+layer)}") (effects (font (size {size} {size}) (thickness .12))))'
def keepout(x1,x2,ox=0,oy=0,tag=''):
 return f'(zone (layer "F.Cu") (uuid "{uid("ko"+str(x1)+tag)}") (name "FX23L floating copper exclusion") (hatch edge .5) (connect_pads (clearance 0)) (min_thickness .1) (keepout (tracks not_allowed) (vias not_allowed) (pads not_allowed) (copperpour not_allowed) (footprints allowed)) (fill (thermal_gap .5) (thermal_bridge_width .5)) (polygon (pts (xy {ox+x1} {oy-3.85}) (xy {ox+x2} {oy-3.85}) (xy {ox+x2} {oy+3.85}) (xy {ox+x1} {oy+3.85}))))'
def connector(plug,ref='REF**',x=0,y=0,nets=None,board=False):
 part='FX23L-80P-0.5SV8' if plug else 'FX23L-80S-0.5SV';lib='MIRA_Module' if plug else 'MIRA_C';name='Hirose_'+part
 bottom=plug and board;face='B' if bottom else 'F';mirror=-1 if plug and not bottom else 1
 footprintname=lib+':'+name if board else name
 out=[f'(footprint {q(footprintname)}', '(version 20260206) (generator "pcbnew")' if not board else '',f'(layer "{face}.Cu")']
 if board:
  proj='MIRA_Crossbar' if plug else 'MIRA_Control';path=('/fe09b8b1-4cb9-5c2a-ab95-aa43c2c9d5fa' if plug else '/ad010b50-c509-466c-b833-d1667dfb0702/ef755ccb-5b73-5aca-9579-d146067941ac/7fe25520-7c9e-563d-afd4-e8f39ab20063')+'/'+uid(proj+ref)
  out += [f'(at {x} {y}) (uuid "{uid(proj+ref)}") (path {q(path)})']
 out += ['(descr "Hirose individual drawing CL573-2004-3 / CL573-2304-7; P1..P4 = Power Contact No.1..4; unnumbered retention tabs")','(attr smd)',prop('Reference',ref,0,-7.3 if not plug else -5.5,face+'.SilkS'),prop('Value',part,0,0,face+'.Fab',True)]
 row=3.15 if plug else 4.75;length=1.9 if plug else 1.8;F=29.9 if plug else 32.2
 def net(n):return f'(net {q(nets[n])}) (pinfunction {q(n)}) (pintype "passive")' if nets and n in nets else ''
 for n in range(1,81):
  px=-9.75+(n-1)%40*.5;py=(-row if n<=40 else row)*mirror
  out.append(f'(pad "{n}" smd rect (at {px} {py}) (size .3 {length}) (layers "{face}.Cu" "{face}.Paste" "{face}.Mask") (solder_mask_margin .025) (solder_paste_margin -.025) {net(str(n))})')
 for num,(px,sign) in zip(POWER_PINS,[(-12.25,1),(12.25,1),(-12.25,-1),(12.25,-1)]):
  py=sign*(2.375 if plug else 4.675)*mirror
  out.append(f'(pad "{num}" thru_hole circle (at {px} {py}) (size 1.6 1.6) (drill 1.2) (layers "*.Cu" "*.Mask") (remove_unused_layers no) {net(num)})')
 for px in [-(F/2+1.225),F/2+1.225]:out.append(f'(pad "" smd rect (at {px} 0) (size 2.45 3.2) (layers "{face}.Cu" "{face}.Paste" "{face}.Mask"))')
 half=16.85 if plug else 18.;h=3.3 if plug else 5.25
 out += [frect(-half,-h,half,h,face+'.Fab'),frect(-(F/2+2.45+.5),-(row+length/2+.5),F/2+2.45+.5,row+length/2+.5,face+'.CrtYd'),frect(-10.2,-1.8*mirror,-9.6,-1.4*mirror,face+'.SilkS')]
 if not plug:out += [keepout(-16.1,-9.9,x,y,ref if board else ''),keepout(9.9,16.1,x,y,ref if board else '')]
 out.append(')');return '\n'.join(out).replace('(thickness .12)))','(thickness .12)) (justify mirror))') if bottom else '\n'.join(out)
def mounting(ref,x,y,key=False,control=False):
 val=('KEY post D2 projection14.0 nominal' if control else 'KEY receive D2.2') if key else 'M2 spacer8mm / D2.2'
 return f'(footprint "" (layer "F.Cu") (at {x} {y}) (uuid "{uid("mount"+ref)}") (attr board_only exclude_from_pos_files exclude_from_bom) '+prop('Reference',ref,0,0,'F.Fab',True)+prop('Value',val,0,0,'F.Fab',True)+'(pad "" np_thru_hole circle (at 0 0) (size 2.2 2.2) (drill 2.2) (layers "*.Cu" "*.Mask"))'+frect(-2.5,-2.5,2.5,2.5,'F.CrtYd')+frect(-2.5,-2.5,2.5,2.5,'B.CrtYd')+')'+gtext(ref+(' KEY' if key else ' M2'),x,y+3.3,size=.65)
# Snapshot every unaffected footprint text and Power bytes before touching boards.
power=BASE/'MIRA_Power/MIRA_Power.kicad_pcb';powerhash=hashlib.sha256(power.read_bytes()).hexdigest()
regression={}
for module in [False,True]:
 project='MIRA_Crossbar' if module else 'MIRA_Control';path=BASE/project/(project+'.kicad_pcb');raw=path.read_text();oldrefs={'J1','J2','H1','H2','H3'} if module else {'J1800','J1801','H1800','H1801','H1802'}
 preserved={reference(s):s for _,_,s in children(raw) if s.startswith('(footprint ') and reference(s) not in oldrefs}
 tree=ET.parse(OUT/'netlists'/('module.xml' if module else 'control.xml'));nets={}
 for net in tree.findall('./nets/net'):
  for node in net:nets[node.get('ref'),node.get('pin')]=net.get('name')
 cuts=[]
 for start,end,s in children(raw):
  remove=s.startswith('(footprint ') and reference(s) in oldrefs
  if module and s.startswith(('(gr_','(zone ')):remove=True
  if not module and s.startswith('(gr_circle') and re.search(r'\(center\s+(154\s+67|200\s+67)\)',s):remove=True
  if not module and s.startswith('(gr_text ') and any(t in s for t in ['A / J1800','B / J1801','H1800 M2','H1801 M2','H1802 KEY','KEY post D2 H14.0','Adapter v0.2: 8mm']):remove=True
  if remove:cuts.append((start,end))
 for start,end in reversed(cuts):raw=raw[:start]+raw[end:]
 if not module:raw=raw.replace('Crossbar removal +Z / clear access / height TBD','Adapter removal +Z / grip short edges / H=8mm')
 additions=[]
 for pair in PAIRS:
  ref=pair['module' if module else 'control'];ns={pin:name for (r,pin),name in nets.items() if r==ref}
  additions += [connector(module,ref,pair['x'],pair['y'],ns,True),gtext(pair['pair']+' / '+ref,pair['x'],pair['y']+6.6)]
 for cr,mr,x,y,d in MOUNTS:additions.append(mounting(mr if module else cr,x,y))
 cr,mr,x,y,d=KEY;additions.append(mounting(mr if module else cr,x,y,True,not module))
 additions.append(gtext('KEY post D2 H14.0 nominal; tolerance TBD',153,91,size=.65))
 if module:
  additions += [grect(OUTLINE,layer='Edge.Cuts'),gtext('MIRA adapter v0.2 / 60 x 30 / remove +Z',177,59),grect((158,73,196,81),'U1 / socket placement area ONLY'),gtext('U1 SIZE / PAD MAP TBD',177,77,'F.SilkS',.8),grect((147,72,156,82),'GRIP short edge'),grect((198,72,207,82),'GRIP short edge'),gtext('TOP / F.Cu up; plugs on B.Cu / H=8mm',177,96)]
 else:additions += [gtext('Adapter v0.2: 8mm; pair axes (176,68.5) and (180,85.5)',177,56,size=.8)]
 raw=raw.rstrip()[:-1]+'\n'+'\n'.join(additions)+'\n)\n';raw=re.sub(r'(?m)^[ \t]+$','',raw);path.write_text(raw)
 after={reference(s):s for _,_,s in children(raw) if s.startswith('(footprint ') and reference(s) not in oldrefs}
 assert after==preserved
 regression[project]={'unaffected_footprints_preserved_bytewise':True,'count':len(preserved)}
 lib=BASE/project/'libraries'/('MIRA_Module.pretty' if module else 'MIRA_C.pretty');part='FX23L-80P-0.5SV8' if module else 'FX23L-80S-0.5SV'
 (lib/('Hirose_'+part+'.kicad_mod')).write_text(connector(module)+'\n')
assert hashlib.sha256(power.read_bytes()).hexdigest()==powerhash
regression['Power']={'unchanged':True,'sha256':powerhash}
(OUT/'placement-regression.json').write_text(json.dumps(regression,indent=2));print(json.dumps(regression))
