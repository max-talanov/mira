#!/usr/bin/env python3
"""Native KiCad startup repair checks; fixed pin contract plus before/after audit."""
from pathlib import Path
import json,subprocess,tempfile,xml.etree.ElementTree as ET,itertools,hashlib
from verify_unpowered_signals import SIGNAL_REFS
from verify_fault_hardware import FAULT_REFS,normalize_fault_rows
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/pcb-preparation/startup/validation'
CHANNELS=['USB','SYS','FPGA','ANA','P15','N15','CORE','AUX18','AUX25','IO33','DDR','PHY','VTT','ANA5','ANA33','MATRIX']
NEW_REFS={'R1805'}|{f'U{x}' for x in range(5201,5204)}|{f'R{x}' for x in range(5201,5205)}|{f'C{x}' for x in range(5201,5204)}|{f'U{x}' for x in range(5301,5309)}|{f'C{x}' for x in range(5301,5309)}|{f'R{x}' for x in range(5301,5317)}
LEGACY_CLEAR='/POWER_SYSTEM/POWER_CONTROL/2600_PM_PERMIT_INTERLOCKS/GLOBAL_CLEAR_N'

def normalize_startup_rows(rows):
 """Undo ONLY the explicit repair for the older connector regression baseline."""
 out=[]
 for ref,pin,net in normalize_fault_rows(rows):
  if ref in NEW_REFS:continue
  # Sequencing feedback added on 2026-10-29: only this exact pin/net maps back.
  if (ref,pin,net)==('U2401','4','GLOBAL_CLEAR_N'):net='unconnected-(U2401-PC14-Pad4)'
  if net.startswith('CMD_') and net.endswith('_RAW') and ref.startswith(('U27','U28','R27','R28')):net=net[:-4]
  if (ref,pin)==('U2603','9') and net=='MATRIX_PERMIT_RAW':net='MATRIX_PERMIT'
  if (ref,pin) in [('U2601','8'),('U2603','1')] and net in ['GLOBAL_CLEAR_RAW_N','GLOBAL_CLEAR_N']:net=LEGACY_CLEAR
  out.append((ref,pin,net))
 out.extend([('Q1801','1','CMD_VTT'),('Q1801','2','EN_VTT'),('Q1801','3','AON')])
 return sorted(out)

def native(path):
 t=ET.parse(path);m={(n.get('ref'),n.get('pin')):net.get('name') for net in t.findall('nets/net') for n in net.findall('node')}
 c={n.get('ref'):n for n in t.findall('components/comp')};return t,m,c

def main():
 OUT.mkdir(parents=True,exist_ok=True);checks={}
 def ck(n,v):
  checks[n]=bool(v)
  if not v:raise AssertionError(n)
 with tempfile.TemporaryDirectory() as td:
  fn=Path(td)/'Power.xml';subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(fn),str(ROOT/'hardware/MIRA_Power/MIRA_Power.kicad_sch')],check=True)
  t,m,c=native(fn)
  def pins(ref,d):ck(ref+'_pin_contract',all(m.get((ref,str(k)))==v for k,v in d.items()))
  pins('U5201',{1:'STARTUP_RESET_N',2:'GND',3:'AON',4:'STARTUP_CT',5:'STARTUP_SENSE',6:'AON'})
  pins('U5202',{2:'STARTUP_RESET_N',3:'GND',4:'STARTUP_READY_H',5:'AON'})
  pins('U5203',{1:'GLOBAL_CLEAR_RAW_N',2:'STARTUP_READY_H',3:'GND',4:'GLOBAL_CLEAR_N',5:'AON'})
  for r,d in {'R5201':{1:'AON',2:'STARTUP_SENSE'},'R5202':{1:'STARTUP_SENSE',2:'GND'},'R5203':{1:'AON',2:'STARTUP_RESET_N'},'R5204':{1:'AON',2:'STARTUP_CT'}}.items():pins(r,d)
  for i in range(8):
   nets=['MATRIX_PERMIT' if a=='MATRIX' else 'CMD_'+a for a in CHANNELS[2*i:2*i+2]]
   pins(f'U{5301+i}',{1:'STARTUP_READY_H',2:nets[0]+'_RAW',6:nets[0],7:'STARTUP_READY_H',5:nets[1]+'_RAW',3:nets[1],8:'AON',4:'GND'})
   for j,net in enumerate(nets):pins(f'R{5301+2*i+j}',{1:net,2:'GND'})
  for ref in [f'C{x}' for x in range(5201,5204)]+[f'C{x}' for x in range(5301,5309)]:pins(ref,{1:'AON',2:'GND'})
  pins('U2401',{4:'GLOBAL_CLEAR_N'})
  pins('R1805',{1:'CMD_VTT',2:'EN_VTT'});pins('U1801',{7:'EN_VTT',10:'AON'});pins('U2603',{1:'GLOBAL_CLEAR_N',9:'MATRIX_PERMIT_RAW'});pins('U2601',{8:'GLOBAL_CLEAR_RAW_N'})
  ck('old_VTT_source_follower_removed','Q1801' not in c)
  ck('matrix_connector_uses_qualified_permit',m['J2603','1']=='MATRIX_PERMIT')
  ck('ready_fanout_is_16_OE_clear_and_monitor_buffer',{k for k,v in m.items() if v=='STARTUP_READY_H'}=={('U5202','4'),('U5203','2'),('U6100','2')}|{(f'U{r}',pin) for r in range(5301,5309) for pin in ['1','7']})
  expected_values={'R1805':'0R','R5201':'590k','R5202':'100k','R5203':'150k','R5204':'100k','U5201':'TPS3808G01DBVR','U5202':'74AUP1G34GW','U5203':'74LVC1G08GV'}
  for i,ch in enumerate(CHANNELS):expected_values[f'R{5301+i}']='10k' if ch in ['VTT','MATRIX'] else ('47k' if ch=='N15' else '220k')
  for r in range(5301,5309):expected_values[f'U{r}']='74AUP2G126DC'
  for r,v in expected_values.items():ck(r+'_value',c[r].findtext('value')==v)
  before=json.loads((OUT/'baseline-power-pins.json').read_text())['pins'];after=[[*k,v] for k,v in sorted(m.items())]
  ck('all_unrelated_legacy_pins_preserved',normalize_startup_rows(after)==[tuple(x) for x in before])
  ck('new_component_set_exact',{r for r in c if r not in {x[0] for x in before}}==NEW_REFS|FAULT_REFS|SIGNAL_REFS)
  # All actual signal consumers retain their former nets; only the listed drivers move to RAW.
  changes=[{'ref':r,'pin':pin,'before':old,'after':m.get((r,pin))} for r,pin,old in before if m.get((r,pin))!=old]
  (OUT/'pin-delta.json').write_text(json.dumps(changes,indent=2)+'\n')
  # Match new symbol pin numbers to the local footprint pad numbers.
  for ref in sorted(NEW_REFS):
   comp=c[ref];fp=comp.findtext('footprint');file=ROOT/'hardware/MIRA_Power/libraries/MIRA_RevA.pretty'/(fp.split(':')[1]+'.kicad_mod')
   import re
   pads=set(re.findall(r'\(pad\s+"?(\d+)"?\s',file.read_text()))
   pins_used={pin for r,pin in m if r==ref}
   ck(ref+'_footprint_pin_set',pins_used==pads)
  erc=OUT/'Power-erc.json';subprocess.run(['kicad-cli','sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(erc),str(ROOT/'hardware/MIRA_Power/MIRA_Power.kicad_sch')],check=True)
  erc_data=json.loads(erc.read_text());ck('61_active_Power_sheets',len(erc_data['sheets'])==61);ck('zero_erc_messages',not any(s['violations'] for s in erc_data['sheets']))
 # Abstract sequential contract, explicitly not transistor or transient simulation.
 seq=[];q=0;prev_clk=0
 for event,ready,clear,clk in [('cold start',0,0,0),('ARM while blocked',0,1,1),('release ARM',0,1,0),('AON ready',1,1,0),('ARM',1,1,1),('release ARM',1,1,0),('AON fault',0,1,0),('AON restored',1,1,0),('fresh ARM',1,1,1)]:
  clr=ready and clear
  if not clr:q=0
  elif clk and not prev_clk:q=1
  prev_clk=clk;seq.append({'event':event,'ready':ready,'clear':clr,'arm':clk,'permit':q,'output_enable':bool(ready and q)})
 ck('no_automatic_rearm',seq[7]['permit']==0 and seq[8]['permit']==1)
 # DC corner arithmetic from cited datasheets, -40..85 C.
 thresholds=[.405*(1+sv*.02)*(1+590000*(1+st*.01)/(100000*(1+sb*.01)))+si*25e-9*590000*(1+st*.01) for sv,st,sb,si in itertools.product([-1,1],repeat=4)]
 margins={'supervisor_reset_pullup_plus_input_uA_below_1_3V':1.3/(150000*.99)*1e6+.5,'supervisor_POR_load_limit_uA':15,'AUP_ready_fanout_uA':16*.5+5+5,'AUP_light_load_limit_uA':20,'POR_VOL_max_V':.2,'AUP_VIL_at_0_8V_V':.8*.3,'buffer_ready_VOL_max_V':.1,'VTT_VOH_conservative_min_at_3V_V':2.55,'TPS51200_EN_VIH_V':1.7,'VTT_logic_high_margin_V':.85,'sense_falling_nominal_V':.405*6.9,'sense_falling_corner_min_V':min(thresholds),'sense_falling_corner_max_V':max(thresholds),'sense_rising_upper_with_3pct_hysteresis_V':max(thresholds)+.405*.03*6.9,'added_output_pulldown_current_nominal_mA':(13*3.28/220000+3.28/47000+2*3.28/10000)*1000,'added_bypass_uF':1.1,'recommended_extra_AON_budget_mA':5,'scope':'DC design arithmetic only; no measured ramps, fast-collapse immunity, temperature test or SPICE result.'}
 ck('POR_load_margin',margins['supervisor_reset_pullup_plus_input_uA_below_1_3V']<15);ck('ready_fanout_margin',margins['AUP_ready_fanout_uA']<20);ck('POR_logic_low_margin',.2<.8*.3);ck('VTT_high_margin',2.55>1.7)
 result={'kicad_version':subprocess.check_output(['kicad-cli','version'],text=True).strip(),'checks_passed':len(checks),'checks':checks,'changed_legacy_pin_entries':len(changes),'removed_pins':3,'new_pin_entries':len(m)-len(before)+3,'startup_components':len(NEW_REFS),'fault_components':len(FAULT_REFS),'new_components':len(NEW_REFS|FAULT_REFS|SIGNAL_REFS),'matrix_and_rail_channels':16,'sequence_model':seq,'dc_margins':margins,'hardware_tests':'pending'}
 (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['checks','sequence_model','dc_margins']},indent=2))
if __name__=='__main__':main()
