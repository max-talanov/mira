import sys,re
from trial_spec import *
sys.path.insert(0,str(LAYOUT))
from sexpr_tools import children
from pcb_text_helpers import uid
name='ICS_CQFP64_Socket';lib='MIRA_Module:'+name;foot='MIRA_Module:'+SOCKET

def fx():return '(effects (font (size .8 .8)))'
def prop(k,v,x=0,y=0,hide=False):return f'(property "{k}" "{v}" (at {x} {y} 0) {"(hide yes)" if hide else ""} {fx()})'
def symbol(n):
 out=[f'(symbol "{n}" (pin_names (offset .65)) (in_bom yes) (on_board yes)',prop('Reference','J'),prop('Value',name),prop('Footprint',foot,hide=True),f'(symbol "{name}_1_1" (rectangle (start -17.78 43.18) (end 17.78 -43.18) (stroke (width .2) (type default)) (fill (type background)))']
 for i in range(64):
  right=i>=32;x=20.32 if right else -20.32;y=40.64-(i%32)*2.54
  out.append(f'(pin passive line (at {x} {y:.3f} {180 if right else 0}) (length 2.54) (name "CONTACT_{i+1}" {fx()}) (number "{i+1}" {fx()}))')
 return '\n'.join(out)+'))'
raw=(OUT/'before/MIRA_Crossbar.kicad_sch').read_text();a,b,n=next((a,b,n) for a,b,n in children(raw) if n.startswith('(lib_symbols '));raw=raw[:a]+n[:-1]+symbol(lib)+')'+raw[b:]
x,y=177.8,254.;u=uid('socket-J3')
instance=f'(symbol (lib_id "{lib}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{u}")'+prop('Reference','J3',x,y-48)+prop('Value',SOCKET+' / matrix pin map TBD',x,y-45)+prop('Footprint',foot,x,y,True)+f'(instances (project "MIRA_Crossbar" (path "/fe09b8b1-4cb9-5c2a-ab95-aa43c2c9d5fa" (reference "J3") (unit 1)))))'
notes=[instance]
for i in range(64):
 px=x+(20.32 if i>=32 else -20.32);py=y-(40.64-(i%32)*2.54);notes.append(f'(no_connect (at {px:.3f} {py:.3f}) (uuid "{uid("socket-TBD-"+str(i+1))}"))')
notes.append(f'(text "J3: mechanical socket installed. CONTACT_1..64 -> BL/NL/WL mapping TBD.\\nNo-connect flags are temporary unassigned contacts, not a released NC pinout.\\nU1 above remains the 96-line logical boundary, not a physical die pin map." (at 230 220 0) (effects (font (size 1.2 1.2)) (justify left top)) (uuid "{uid("socket-note")}"))')
raw=raw.rstrip()[:-1]+'\n'+'\n'.join(notes)+'\n)\n';(BASE/'MIRA_Crossbar/MIRA_Crossbar.kicad_sch').write_text(raw)
p=BASE/'MIRA_Crossbar/libraries/MIRA_Module.kicad_sym';s=p.read_text()
if f'(symbol "{name}"' not in s:p.write_text(s.rstrip()[:-1]+'\n'+symbol(name)+'\n)\n')
print('Added J3 native 64-contact socket symbol; all matrix assignments explicitly TBD; U1 logical 96 lines preserved.')
