"""Pure text helpers copied from the validated FX23L generator; no PCB writes on import."""
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
