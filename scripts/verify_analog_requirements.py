#!/usr/bin/env python3
"""MIRA.05 native pin regression, independent package pins and DC/load arithmetic.
Does not simulate a semiconductor macro-model or certify pulse peak/settling.
"""
from pathlib import Path
import json,math,itertools,subprocess,tempfile,xml.etree.ElementTree as E,csv,hashlib
from analog_pin_delta import normalize_analog_rows
from analog_dc import summary as dc_summary
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/pcb-preparation/analog-requirements'
def native(path):
 t=E.parse(path)
 m={(n.get('ref'),n.get('pin')):z.get('name') for z in t.findall('nets/net') for n in z.findall('node')}
 c={x.get('ref'):x for x in t.findall('components/comp')}
 return m,c
def main():
 checks={}
 def ck(k,v):
  checks[k]=bool(v)
  if not v:raise AssertionError(k)
 with tempfile.TemporaryDirectory() as td:
  f=Path(td)/'Control.xml'
  subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(f),str(ROOT/'hardware/MIRA_Control/MIRA_Control.kicad_sch')],check=True)
  m,c=native(f)
  (OUT/'validation/control-current.xml').write_bytes(f.read_bytes())
  base=json.loads((OUT/'validation/baseline-control-pins.json').read_text())
  ck('all_other_pins_unchanged',sorted(normalize_analog_rows([(*k,v) for k,v in m.items()]))==sorted(tuple(x) for x in base))
  ck('no_added_or_removed_components',set(c)=={r for r,p,n in base})
  # Manufacturer INA149 SBOS579B pin diagram, independently transcribed.
  expected={'1':'GND','2':'CC_CMD_SENSE','3':'MAT_PI_RAW','4':'N15','5':'GND','6':'CC_AW','7':'P15','8':'unconnected-(U2109-NC-Pad8)'}
  ck('INA149_exact_pins',all(m['U2109',p]==n for p,n in expected.items()))
  # Preserve all eight component-property fixes from intervening version 10.
  intervening=json.loads((OUT/'intervening-bom-delta.json').read_text())
  def properties(x):
   f={p.get('name'):p.text or '' for p in x.findall('fields/field')}
   f.update(Value=x.findtext('value') or '',Footprint=x.findtext('footprint') or '',Datasheet=x.findtext('datasheet') or '',Description=x.findtext('description') or '',Reference=x.get('ref'))
   return f
  for item in intervening:
   ck(item['ref']+'_intervening_properties_preserved',all(properties(c[item['ref']]).get(k)==v for k,v in item['after'].items()))
  _,bc=native(OUT/'validation/baseline-control.xml')
  allowed={'U2109','R2111','R2301','R2302'}|{x['ref'] for x in intervening}
  ck('all_other_component_properties_unchanged',all(properties(c[r])==properties(bc[r]) for r in c if r not in allowed))
  ck('RSH_available_for_service_READ',m['U1327','17']==m['U2103','1']=='MAT_RSH_A0' and m['U1327','16']==m['U2103','16']=='MAT_RSH_A1')
  ck('VMM_bypasses_shared_CC',all(m['U1500',p]==n for p,n in [('3','BL_DAC0'),('2','BL0'),('1','MAT_BL_VMM_0')]))

  ck('INA149_orderable_part',c['U2109'].findtext('value')=='INA149AIDR')
  ck('INA149_SOIC8',c['U2109'].findtext('footprint')=='MIRA_RevA:SOIC-8_3.9x4.9mm_P1.27mm')
  for r,v in {'R2111':'10k','R2112':'10k','R2138':'100','R2301':'1M','R2302':'31.6k','R2103':'100k','R2128':'33k','C2103':'4.7n'}.items():ck(r+'_value',c[r].findtext('value')==v)
  for r,mpn in {'R2111':'RT0603BRD0710KL','R2301':'RT0603BRD071ML','R2302':'RT0603BRD0731K6L'}.items():
   ck(r+'_precision_MPN',c[r].find("property[@name='MPN']").get('value')==mpn)
   ck(r+'_0603',c[r].findtext('footprint')=='MIRA_RevA:R_0603_1608Metric')
  ck('command_buffer_is_source_for_AW',m['U2105','8']==m['U2105','9']==m['U2109','2']=='CC_CMD_SENSE')
  ck('CC_shunt_Kelvin_sense_unchanged',m['U2104','4']=='CC_KELVIN_P' and m['U2104','1']=='MAT_SOURCE' and m['U2103','9']=='CC_KELVIN_P')
  ck('fault_only_qualified_WRITE',m['U2201','2']=='MAT_WRITE_SAFE')
  erc={}
  for board,count in [('Control',43),('Power',61)]:
   f=OUT/'validation'/(board+'-erc.json')
   subprocess.run(['kicad-cli','sch','erc','--severity-all','--exit-code-violations','--format','json','-o',str(f),str(ROOT/'hardware'/('MIRA_'+board)/('MIRA_'+board+'.kicad_sch'))],check=True)
   r=json.loads(f.read_text()); ck(board+'_ERC_clear',not any(s['violations'] for s in r['sheets']));ck(board+'_sheet_count',len(r['sheets'])==count)
   erc[board]={'sheets':len(r['sheets']),'violations':sum(len(s['violations']) for s in r['sheets'])}
 # TPS3808G01: +/-2% threshold, +/-25 nA sense current; divider +/-0.1%; hysteresis max 3%.
 threshold=[]
 for a,b,t,ib in itertools.product([-.001,.001],[-.001,.001],[-.02,.02],[-25e-9,25e-9]):
  r1=1e6*(1+a);r2=31600*(1+b)
  threshold.append(.405*(1+t)*(1+r1/r2)+ib*r1)
 fall_min,fall_max=min(threshold),max(threshold)
 rise_max=fall_max*1.03
 # Conservative design allowances include REF error/temperature, guarded reference attenuation and OPA offsets.
 # Not a claim that these allowances are calibrated production error limits.
 ceiling_nom=5*(1+(10000+100)/10000)
 ceiling_hi=5.01*(1+10100*1.001/(10000*.999))+.01
 ck('ready_asserts_at_min_nominal_P15',rise_max<14.25)
 ck('INA821_static_positive_headroom',fall_min-2-ceiling_hi>.7)
 # Conservative routing RON allowances at nominal +/-15 V, -40..85C; rounded above datasheet max.
 ron8,ron4,ron1=8.,8.,4.
 force=47+ron4+ron8
 source_cmd=8+.8+.008*force
 ck('8V_8mA_source_has_command_headroom',source_cmd<ceiling_nom-.3)
 service_loop=2*ron8+ron8+2*ron4+ron1
 # Return: bank + local BL (two 7208), NL (one 7208), two polarity SPDT, return SPST.
 ck('service_loop_drop_at_8mA_below_0_4V',.008*service_loop<.4)
 tia=[]
 for code,rf,cf in zip(range(5),[100,1000,10000,100000,1000000],[330e-12,100e-12,33e-12,10e-12,3.3e-12]):
  re=1/(1/1e7+1/(rf+4))
  tia.append({'code':code,'Rf_ohm':rf,'Cf_F':cf,'Reff_nominal_ohm':re,'I_at_10V_A':10/re,'profile_limit_A':min(.008,10/re),'ideal_ADC_current_LSB_A':10/(2**18)/.148935704/re,'lumped_RC_tau_s':re*(cf+2.2e-12)})
 # Current comparator includes sheet 3000 100k bleeds, but neglects small Ron and bias; nominal only.
 a=(1/45300)/(1/45300+1/10000+1/100000)
 b=(1/34000)/(1/34000+1/10000+1/100000+1/1500000)
 q=(1/1500000)/(1/34000+1/10000+1/100000+1/1500000)
 k,bias=b/a,q/a*3.3
 # Single-pole ideal small-signal PI model: Kp=0.33, Ki=1/(100k*4.7n).
 ki=1/(100e3*4.7e-9);kp=.33
 timing=[]
 for g in [1,.1,.01]:
  tau=(1+g*kp)/(g*ki)
  timing.append({'plant_gain':g,'closed_loop_tau_s':tau,'to_0_1_percent_s':-math.log(.001)*tau})
 calc={'P15_falling_nominal_V':.405*(1+1e6/31600),'P15_falling_range_V':[fall_min,fall_max],'P15_rising_upper_bound_V':rise_max,'command_ceiling_nominal_V':ceiling_nom,'command_ceiling_design_upper_V':ceiling_hi,'INA821_positive_static_margin_V':fall_min-2-ceiling_hi,'force_R_budget_ohm':force,'source_command_for_8V_8mA_V':source_cmd,'external_service_loop_R_budget_ohm':service_loop,'external_service_loop_drop_8mA_V':.008*service_loop,'service_Rmin_at_8V_8mA_ohm':8/.008-service_loop,'service_Rmax_at_8V_10uA_ohm':8/1e-5-service_loop,'TIA':tia,'ADC_gain_nominal':-.148935704,'ADC_LSB_referred_to_monitor_V':10/(2**18)/.148935704,'ADC_code_at_TIA_10V':round(.148935704*10/5*(2**17)),'comparator_sense_scale':a,'comparator_k_nominal':k,'comparator_offset_nominal_V':bias,'PI_Kp':kp,'PI_Ki_per_s':ki,'PI_ideal_cases':timing,'C_DUT_budget_F':1e-9,'DUT_energy_at_8V_J':.5*1e-9*8**2,'DUT_charge_at_8V_C':1e-9*8,'unregulated_source_fault_upper_ideal_A':10.1/(100*.999+47*.99),'scope':'DC arithmetic, conditional load budgets and ideal single-pole PI examples only; no semiconductor transient simulation.'}
 calc.update(dc_summary())
 ck('matched_CV_gain_within_0_1_percent',abs(calc['CV_nominal_gain']-1)<.001)
 ck('trip_corner_min_exceeds_nominal_ILIM_0_1',calc['trip_corners']['threshold_at_ILIM0_1_V'][0]>.1)
 (OUT/'calculations.json').write_text(json.dumps(calc,indent=2)+'\n')
 for name,rows in [('tia-ranges.csv',tia),('pi-timing-examples.csv',timing)]:
  with (OUT/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
 summary={'checks_passed':len(checks),'checks':checks,'ERC':erc,'schematic_review_complete':True,'hardware_validated':False,'firmware_implemented':False,'PCB_updated':False,'scope':'Explicit current pin/part contracts, preservation of all unrelated pins, native ERC, DC arithmetic. Timing/peak-current/precision/load stability qualification remains open.'}
 (OUT/'validation/summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='checks'},indent=2))
if __name__=='__main__':main()
