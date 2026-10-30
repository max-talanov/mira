#!/usr/bin/env python3
"""Fault repair: strict native pin delta, package checks and ideal timed contract.

Not SPICE, MCU firmware, metastability or a measured board timing result.
"""
import hashlib,json,re,subprocess,tempfile
from pathlib import Path
from verify_unpowered_signals import SIGNAL_REFS,normalize_signal_rows
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/pcb-preparation/fault-review/validation'
FAULT_REFS={f'U{x}' for x in range(5401,5406)}|{f'R{x}' for x in range(5401,5405)}|{f'C{x}' for x in range(5401,5406)}
LEGACY_CHANGES={('U2401','5'):('unconnected-(U2401-PC15-Pad5)','LINK_READY_H'),('U2602','13'):('AON','LINK_READY_H')}

def normalize_fault_rows(rows):
 out=[]
 for ref,pin,net in normalize_signal_rows(rows):
  if ref in FAULT_REFS:continue
  pair=LEGACY_CHANGES.get((ref,pin))
  if pair and net==pair[1]:net=pair[0]
  out.append((ref,pin,net))
 return sorted(out)

class LinkModel:
 """Ideal TPS3851 timeout plus asynchronous clear and first-edge flip-flop.

 reset is the supervisor's INTERNAL voltage/manual-reset state, not a
 readback of an externally pulled output pin. A falling WDI during clear
 cannot set Q. Timing exactly at a boundary is intentionally not qualified.
 """
 def __init__(self,timeout=200,pulse=200):
  self.timeout=timeout;self.pulse=pulse;self.ready=False;self.reset=True
  self.due=None;self.release=None;self.wdo=True;self.level=False
 def reset_at(self,t,asserted):
  self.reset=asserted;self.ready=False;self.wdo=True;self.release=None
  self.due=None if asserted else t+self.timeout
 def advance(self,t):
  while not self.reset:
   event=self.release if not self.wdo else self.due
   if event is None or event>t:break
   if self.wdo:
    self.wdo=False;self.ready=False;self.due=None;self.release=event+self.pulse
   else:
    self.wdo=True;self.release=None;self.due=event+self.timeout
 def drive(self,t,level):
  self.advance(t);fall=self.level and not level;self.level=level
  if fall and not self.reset and self.wdo:
   self.ready=True;self.due=t+self.timeout
 def beat(self,t):
  self.drive(t-5,True);self.drive(t,False)

def main():
 from verify_startup import native
 checks={};timing=[]
 def ck(name,value):
  checks[name]=bool(value)
  if not value:raise AssertionError(name)
 with tempfile.TemporaryDirectory() as td:
  f=Path(td)/'Power.xml'
  subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(f),str(ROOT/'hardware/MIRA_Power/MIRA_Power.kicad_sch')],check=True)
  t,m,c=native(f)
  def pins(ref,expect):ck(ref+'_native_pins',all(m.get((ref,str(p)))==net for p,net in expect.items()))
  pins('U5401',{1:'AON',2:'LINK_CWD',3:'AON',4:'GND',5:'AON',6:'HOST_ALIVE_PM',7:'LINK_WDO_N',8:'LINK_RESET_N',9:'GND'})
  pins('U5402',{1:'unconnected-(U5402-NC-Pad1)',2:'HOST_ALIVE_PM',3:'GND',4:'LINK_EDGE_H',5:'AON'})
  pins('U5403',{1:'LINK_EDGE_H',2:'AON',4:'GND',5:'LINK_READY_H',6:'LINK_CLEAR_N',7:'AON',8:'AON'})
  pins('U5404',{1:'LINK_RESET_N',2:'LINK_WDO_N',3:'GND',4:'LINK_CLEAR_N',5:'AON'})
  pins('U5405',{2:'HOST_WDO_N',3:'GND',4:'HOST_RESET_N',5:'AON'})
  for r,a,b in [('R5401','AON','LINK_CWD'),('R5402','AON','LINK_RESET_N'),('R5403','AON','LINK_WDO_N'),('R5404','LINK_READY_H','GND')]:pins(r,{1:a,2:b})
  for i in range(5401,5406):pins('C'+str(i),{1:'AON',2:'GND'})
  pins('U2401',{5:'LINK_READY_H',11:'HOST_ALIVE_PM'})
  pins('U2602',{13:'LINK_READY_H'})
  ck('link_ready_has_only_intended_consumers',{k for k,v in m.items() if v=='LINK_READY_H'}=={('U5403','5'),('R5404','1'),('U2401','5'),('U2602','13')})
  ck('CWD_has_only_10k_and_timer',{k for k,v in m.items() if v=='LINK_CWD'}=={('R5401','2'),('U5401','2')})
  parts={'U5401':'TPS3851H33EDRBR','U5402':'74LVC1G14GV','U5403':'SN74LVC1G74DCUR','U5404':'74LVC1G08GV','U5405':'SN74LVC1G07DBVR','R5401':'10k','R5402':'10k','R5403':'10k','R5404':'100k',**{f'C{x}':'100n' for x in range(5401,5406)}}
  for ref,value in parts.items():ck(ref+'_part',c[ref].findtext('value')==value)
  # Native libpart electrical pin type, not just net names, proves wired-OR output.
  source=c['U5405'].find('libsource')
  lp=next(p for p in t.findall('libparts/libpart') if p.get('lib')==source.get('lib') and p.get('part')==source.get('part'))
  ck('host_reset_driver_is_open_collector',next(p for p in lp.findall('pins/pin') if p.get('num')=='4').get('type') =='open_collector')
  ck('no_AON_pullup_added_on_host_reset',not any(ref.startswith('R54') for ref,pin in m if m[ref,pin]=='HOST_RESET_N'))
  for ref in sorted(FAULT_REFS):
   fp=c[ref].findtext('footprint').split(':')[1]
   file=ROOT/'hardware/MIRA_Power/libraries/MIRA_RevA.pretty'/(fp+'.kicad_mod')
   pads=set(re.findall(r'\(pad\s+"?(\d+)"?\s',file.read_text()))
   ck(ref+'_footprint_pin_set',pads=={pin for r,pin in m if r==ref})
   model=re.findall(r'\(model\s+"([^"]+)"',file.read_text())
   ck(ref+'_local_3D_model',bool(model) and all((ROOT/'hardware/MIRA_Power'/name.replace('${KIPRJMOD}/','')).is_file() for name in model))
  baseline=json.loads((OUT/'baseline-sequencing-power-pins.json').read_text())['pins']
  after=[[*k,v] for k,v in sorted(m.items())]
  ck('only_two_documented_legacy_pin_changes',normalize_fault_rows(after)==[tuple(a) for a in baseline])
  ck('exactly_14_added_components',set(c)-SIGNAL_REFS-{a[0] for a in baseline}==FAULT_REFS and len(FAULT_REFS)==14)
  historical_m={(r,p):n for r,p,n in normalize_signal_rows(after)}
  delta=[{'ref':ref,'pin':pin,'before':old,'after':historical_m.get((ref,pin))} for ref,pin,old in baseline if historical_m.get((ref,pin))!=old]
  ck('legacy_delta_is_exact',len(delta)==2 and all((a['before'],a['after'])==LEGACY_CHANGES[a['ref'],a['pin']] for a in delta))
 # Datasheet timeout corners; no tolerance claim about propagation/detection ramps.
 for timeout in [170,200,230]:
  for pulse in [170,230]:
   tag=f'{timeout}ms_timeout_{pulse}ms_pulse'
   q=LinkModel(timeout,pulse);q.reset_at(0,False);q.advance(2000)
   ck(tag+'_no_first_edge_stays_blocked',not q.ready)
   q=LinkModel(timeout,pulse);q.reset_at(0,False)
   for moment in range(10,2011,50):q.beat(moment)
   ck(tag+'_50ms_heartbeat_stays_ready',q.ready and q.wdo)
   last=2010;q.advance(last+timeout-1)
   ck(tag+'_not_early',q.ready)
   q.advance(last+timeout)
   ck(tag+'_timeout_clears_readiness',not q.ready and not q.wdo)
   q.advance(last+timeout+pulse+1)
   ck(tag+'_WDO_release_does_not_restore_ready',q.wdo and not q.ready)
   q.beat(last+timeout+pulse+10)
   ck(tag+'_fresh_heartbeat_can_restore_ready',q.ready)
   q.reset_at(last+timeout+pulse+11,True)
   ck(tag+'_supply_reset_clears_ready',not q.ready)
   timing.append({'timeout_ms':timeout,'WDO_low_ms':pulse,'all_checks_passed':True})
 for level in [False,True]:
  q=LinkModel();q.reset_at(0,False);q.beat(10);q.drive(15,level);q.advance(211)
  ck('stuck_'+str(int(level))+'_blocks',not q.ready)
 q=LinkModel();q.reset_at(0,False);q.beat(10);q.advance(210);q.beat(250)
 ck('edge_during_clear_cannot_arm',not q.ready)
 q.advance(411);ck('ignored_edge_not_replayed_after_clear',not q.ready)
 ck('firmware_max_gap_below_min_timeout',100<170)
 result={'kicad_version':subprocess.check_output(['kicad-cli','version'],text=True).strip(),'checks_passed':len(checks),'checks':checks,'added_components':len(FAULT_REFS),'legacy_pin_changes':delta,'native_power_pin_net_sha256':hashlib.sha256(json.dumps(after,separators=(',',':')).encode()).hexdigest(),'timing_corners':timing,'heartbeat_design_target_ms':50,'heartbeat_firmware_max_gap_ms':100,'hardware_timeout_range_ms':[170,230],'extra_AON_budget_mA':2,'added_bypass_uF':0.5,'scope':'Native connectivity, packages and ideal event/latch model at valid supplies; not electrical transient, MCU firmware or prototype verification. Measure ramp, propagation, disconnect-to-stop, reset and unpowered-input behavior on hardware.'}
 (OUT/'hardware-summary.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['checks','timing_corners']},indent=2))
if __name__=='__main__':main()
