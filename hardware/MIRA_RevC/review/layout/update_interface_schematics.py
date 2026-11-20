"""Replace only the connector interface sheets; U1 is a logical die placeholder."""
# The active socket trial must not be overwritten by the historical first-day builder.
from pathlib import Path as _GuardPath
_guard_base=_GuardPath(__file__).resolve().parents[2]
if '"MIRA_Module:ICS-CQFP64-1830-1830-100-1"' in (_guard_base/'MIRA_Crossbar/MIRA_Crossbar.kicad_pcb').read_text():
 raise SystemExit('Active ICS socket trial: use review/layout/socket-trial tools; old draft rebuild is intentionally disabled.')

import uuid,re,csv
from pathlib import Path
from interface_spec import BASE,OUT,PAIRS,pinout,POWER_PINS
NS=uuid.UUID('dfbf2968-72be-46f0-a606-091651de0c21')
def uid(s):return str(uuid.uuid5(NS,s))
def fx(size=.85):return f'(effects (font (size {size} {size})))'
def prop(k,val,x=0,y=0,hide=False):return f'(property "{k}" "{val}" (at {x} {y} 0) {"(hide yes)" if hide else ""} {fx()})'
def libsym(name,foot,die=False):
 pins=([f'{fam}{i}' for fam in ['BL','NL','WL'] for i in range(32)] if die else [str(n) for n in range(1,81)]+POWER_PINS)
 per=48 if die else 42
 out=[f'(symbol "{name}" (pin_names (offset 0.65)) (in_bom {"no" if die else "yes"}) (on_board {"no" if die else "yes"})',prop('Reference','U' if die else 'J'),prop('Value',name.split(':')[-1]),prop('Footprint',foot,hide=True),f'(symbol "{name.split(":")[-1]}_1_1" (rectangle (start -17.78 63.5) (end 17.78 -63.5) (stroke (width 0.22) (type default)) (fill (type background)))']
 for i,n in enumerate(pins):
  right=i>=per;x=20.32 if right else -20.32;y=58.42-(i%per)*2.54
  out.append(f'(pin passive line (at {x} {y:.3f} {180 if right else 0}) (length 2.54) (name "{n}" {fx(.7)}) (number "{n}" {fx(.7)}))')
 out.append('))');return '\n'.join(out)
def instance(lib,ref,val,foot,x,y,path,proj,die=False):
 ident=uid(proj+ref)
 return f'(symbol (lib_id "{lib}") (at {x} {y} 0) (unit 1) (in_bom {"no" if die else "yes"}) (on_board {"no" if die else "yes"}) (dnp no) (uuid "{ident}") '+prop('Reference',ref,x,y-68)+prop('Value',val,x,y-65)+prop('Footprint',foot,x,y,True)+f'(instances (project "{proj}" (path "{path}" (reference "{ref}") (unit 1)))))'
def connections(ref,mapping,x,y,die=False):
 pins=list(mapping);per=48 if die else 42;out=[]
 for i,p in enumerate(pins):
  right=i>=per;px=x+(20.32 if right else -20.32);py=y-(58.42-(i%per)*2.54);net=mapping[p];seed=ref+p
  if net=='NC':out.append(f'(no_connect (at {px:.3f} {py:.3f}) (uuid "{uid(seed+"nc")}"))');continue
  lx=px+(5.08 if right else -5.08)
  out.append(f'(wire (pts (xy {px:.3f} {py:.3f}) (xy {lx:.3f} {py:.3f})) (stroke (width 0) (type default)) (uuid "{uid(seed+"wire")}"))')
  out.append(f'(global_label "{net}" (shape bidirectional) (at {lx:.3f} {py:.3f} {0 if right else 180}) (effects (font (size .85 .85)) (justify {"left" if right else "right"})) (uuid "{uid(seed+"label")}"))')
 return '\n'.join(out)
def note(s,x,y,key):return f'(text "{s}" (at {x} {y} 0) (effects (font (size 1.2 1.2)) (justify left top)) (uuid "{uid(key)}"))'
for module in [False,True]:
 project='MIRA_Crossbar' if module else 'MIRA_Control';lib='MIRA_Module' if module else 'MIRA_C';name=lib+':FX23L80'+('P' if module else 'S');part='FX23L-80P-0.5SV8' if module else 'FX23L-80S-0.5SV';foot=lib+':Hirose_'+part
 path=BASE/project/('MIRA_Crossbar.kicad_sch' if module else 'C_Crossbar.kicad_sch')
 raw=path.read_text();sheetuid=re.search(r'\(uuid "([^"]+)"\)',raw)[1]
 instpath='/fe09b8b1-4cb9-5c2a-ab95-aa43c2c9d5fa' if module else '/ad010b50-c509-466c-b833-d1667dfb0702/ef755ccb-5b73-5aca-9579-d146067941ac/7fe25520-7c9e-563d-afd4-e8f39ab20063'
 symbols=[libsym(name,foot)]
 if module:symbols.append(libsym(lib+':MatrixLogical96','',True))
 out=[f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{sheetuid}") (paper "A2") (title_block (title "Replaceable crossbar interface | FX23L A+B") (rev "C-layout-02") (company "MIRA"))','(lib_symbols '+'\n'.join(symbols)+')',note('Interface v0.2: two FX23L-80 pairs; 8 mm assembled gap. 48 lines + 22 GND + 10 NC per pair.',20,15,'title'+project)]
 for i,p in enumerate(PAIRS):
  ref=p['module' if module else 'control'];x=101.6+152.4*i;y=111.76
  out += [instance(name,ref,part,foot,x,y,instpath,project),connections(ref,pinout(p['pair']),x,y),note(f'Pair {p["pair"]}: '+('BL0..31 / WL0..15' if i==0 else 'NL0..31 / WL16..31'),x-40,185,project+ref+'title')]
 if module:
  die=lib+':MatrixLogical96';out += [instance(die,'U1','Logical matrix boundary / die pads and size TBD','',406.4,111.76,instpath,project,True),connections('U1',{f'{f}{i}':f'{f}{i}' for f in ['BL','NL','WL'] for i in range(32)},406.4,111.76,True),note('U1 logical pins are line names, NOT physical die pad numbers. Custom socket / routing permitted above fixed A/B interface.',20,205,'die-note')]
 out += [note('P1..P4 = Hirose Power Contact No.1..4, four independent 3 A contacts, all GND. Retention tabs are mechanical, not extra signal positions.',20,195,'power-note'+project),'(embedded_fonts no)']
 if module:out.append('(sheet_instances (path "/" (page "1")))')
 out.append(')');path.write_text('\n'.join(out)+'\n')
 # Add native symbol to local library without disturbing existing symbols.
 libpath=BASE/project/'libraries'/f'{lib}.kicad_sym';txt=libpath.read_text()
 # Name is unique on initial application. Idempotent replacement requires the saved library unchanged.
 local=libsym(name.split(':')[1],foot)
 if f'(symbol "{name.split(":")[1]}"' not in txt:libpath.write_text(txt.rstrip()[:-1]+'\n'+local+'\n)\n')
 if module and '(symbol "MatrixLogical96"' not in libpath.read_text():
  txt=libpath.read_text();libpath.write_text(txt.rstrip()[:-1]+'\n'+libsym('MatrixLogical96','',True)+'\n)\n')
with (OUT/'crossbar-pin-map.csv').open('w') as f:
 wr=csv.writer(f,lineterminator="\n");wr.writerow(['pair','control_ref','control_pin','adapter_ref','adapter_pin','net','class'])
 for pair in PAIRS:
  for pin,net in pinout(pair['pair']).items():wr.writerow([pair['pair'],pair['control'],pin,pair['module'],pin,net,'power_GND' if pin in POWER_PINS else 'reserve_NC' if net=='NC' else 'signal_GND' if net=='GND' else 'line'])
print('Updated two interface sheets, symbols and 168-contact map.')
