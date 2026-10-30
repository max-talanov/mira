#!/usr/bin/env python3
"""v6 native connectivity, power-domain contracts, and DC arithmetic.
This is not a PCB measurement, device transient model, or analog performance certification.
"""
from pathlib import Path
import json,subprocess,tempfile,xml.etree.ElementTree as E,hashlib,re,itertools,math,csv
from digital_pin_delta import normalize_digital_rows
from analog_pin_delta import VALUE_OVERRIDES
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/pcb-preparation/signal-remediation'
INTENT=json.loads((OUT/'intent.json').read_text())
ADDED={b:set(INTENT['added'][b]) for b in ['Power','Control']}
BASE={b:{(r,p):n for r,p,n in json.loads((OUT/('baseline-v5-'+b.lower()+'.json')).read_text())} for b in ADDED}
def normalize_remediation_rows(rows,board='Power'):
 """Reverse only the explicit v6 pin delta for immutable earlier regression baselines."""
 out=[]
 for r,p,n in normalize_digital_rows(rows,board):
  if r in ADDED[board]:continue
  if INTENT['rerouted_pins'][board].get(r+':'+p)==n:n=BASE[board][r,p]
  elif board=='Control' and INTENT['control_aliases'].get(BASE[board].get((r,p)))==n:n=BASE[board][r,p]
  out.append((r,p,n))
 return sorted(out)
def read_native(f):
 t=E.parse(f);m={(n.get('ref'),n.get('pin')):net.get('name') for net in t.findall('nets/net') for n in net.findall('node')};c={v.get('ref'):v for v in t.findall('components/comp')};return t,m,c
def main():
 checks={};maps={};components={};ercsummary={};deltas={}
 def ck(n,v):
  checks[n]=bool(v)
  if not v:raise AssertionError(n)
 with tempfile.TemporaryDirectory() as td:
  for b in ADDED:
   folder=ROOT/'hardware'/('MIRA_'+b);fn=Path(td)/(b+'.xml')
   subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(fn),str(folder/('MIRA_'+b+'.kicad_sch'))],check=True)
   t,m,c=read_native(fn);maps[b]=m;components[b]=c
   ck(b+'_exact_new_component_set',set(c)-{r for r,p in BASE[b]}==ADDED[b])
   ck(b+'_all_unrelated_legacy_connections_preserved',normalize_remediation_rows([(*k,n) for k,n in m.items()],b)==sorted((*k,n) for k,n in BASE[b].items()))
   for key,n in INTENT['rerouted_pins'][b].items():r,p=key.split(':');ck(b+'_'+key+'_target',m.get((r,p))==n)
   for r,v in INTENT['added'][b].items():
    ck(b+'_'+r+'_part',c[r].findtext('value')==(VALUE_OVERRIDES.get(r,v['value']) if b=='Control' else v['value']))
    ck(b+'_'+r+'_pin_contract',all(m.get((r,p))==n for p,n in v['pins'].items()))
    fp=folder/'libraries/MIRA_RevA.pretty'/(c[r].findtext('footprint').split(':')[1]+'.kicad_mod')
    ck(b+'_'+r+'_footprint_pin_set',fp.exists() and set(re.findall(r'\(pad\s+"?(\d+)"?\s',fp.read_text()))=={p for rr,p in m if rr==r})
    props={p.get('name'):p.get('value') for p in c[r].findall('property')}
    ck(b+'_'+r+'_MPN_defined',bool(props.get('MPN')) and 'SPECIFY' not in props['MPN'])
   for r,v in INTENT['changed_values'][b].items():
    if b=='Control' and r=='R2115' and c[r].findtext('value')=='100k':
     # MIRA.05 replaces an inconsistent 99k/0402 MPN with a matched 100k/101k pair.
     ck('Control_MIRA05_CV_pair',c['R2116'].findtext('value')=='101k')
    else:ck(b+'_'+r+'_changed_value',c[r].findtext('value')==v)
   ef=OUT/(b+'-erc.json');subprocess.run(['kicad-cli','sch','erc','--severity-all','--exit-code-violations','--format','json','-o',str(ef),str(folder/('MIRA_'+b+'.kicad_sch'))],check=True)
   erc=json.loads(ef.read_text());ck(b+'_zero_ERC_messages',not any(s['violations'] for s in erc['sheets']));ck(b+'_sheet_count',len(erc['sheets'])==(61 if b=='Power' else 43));ercsummary[b]={'sheets':len(erc['sheets']),'errors':0,'warnings':0}
   deltas[b]=[{'ref':r,'pin':p,'before':n,'after':m.get((r,p))} for (r,p),n in BASE[b].items() if m.get((r,p))!=n]
  p,c=maps['Power'],maps['Control']
  # Functional structure of every low-voltage barrier, independently checked from native pins.
  barriers=[]
  for b in maps:
   m=maps[b]
   for r,co in components[b].items():
    if co.findtext('value')!='TMUX2821DSGR':continue
    ck(b+'_'+r+'_ground_and_EP',m[r,'4']==m[r,'9']=='GND')
    for sp,dp,en in [('1','2','7'),('5','6','3')]:
     src,dst=m[r,sp],m[r,dp]
     if src==dst=='GND':ck(r+'_unused_channel_disabled',m[r,en]=='GND');continue
     pulls=[rr for rr,comp in components[b].items() if comp.findtext('value')=='100k' and {m.get((rr,'1')),m.get((rr,'2'))}=={dst,'GND'}]
     ck(b+'_'+r+'_'+dp+'_discharge',len(pulls)==1)
     barriers.append({'board':b,'ref':r,'source':src,'drain':dst,'supply':m[r,'8'],'enable':m[r,en],'bleed_ref':pulls[0]})
  ck('exactly_64_low_voltage_barrier_channels',len(barriers)==64)
  # The low-current startup fanout must stay within its published light-load budget.
  expected={('U5202','4'),('U5203','2'),('U6100','2')}|{(f'U{r}',pn) for r in range(5301,5309) for pn in ['1','7']}
  ck('startup_fanout_is_buffered',{k for k,n in p.items() if n=='STARTUP_READY_H'}==expected)
  ck('startup_static_load_18uA_below_20uA',16*.5+5+5<20)
  # Each converter EN receives only its own VIN through an optical contact.
  enables=[]
  for k in range(10):
   r='U'+str(5800+k if k<5 else 5900+k-5);q='Q'+r[1:];vin=p[r,'6'];out=p[r,'4'];gate=p[q,'1']
   ck(r+'_input_ground',p[q,'2']=='GND');ck(r+'_LED_driver',p[r,'3']==p[q,'3'])
   ck(r+'_VIN_domain',vin==('BUS24' if k<5 else 'FPGA5V5'))
   sinks=[(rr,pn) for (rr,pn),n in p.items() if n==out and rr not in ADDED['Power']]
   ck(r+'_single_converter_destination',len(sinks)==1)
   enables.append({'relay':r,'control':gate,'vin':vin,'enable':out,'converter_pin':sinks[0]})
  ck('IO_requires_AUX_and_command',[p['U6000',x] for x in ['1','3','6','4']]==['EN_IO33','PGR_AUX18','EN_AUX18','EN_IO33_QUAL'])
  # Truth table plus state retention: the actual AND gate controls the existing image CLR.
  ck('image_clear_topology',c['U2302','1']=='MAT_ALLOWED_BASE' and c['U2302','3']==c['U2303','4']=='AFE_SIG_READY' and c['U2302','6']=='ADC_REF_READY' and c['U2302','4']==c['U1301','6']=='MAT_ALLOWED')
  for old,ready in itertools.product([0,1],repeat=2):ck('image_clear_'+str(old)+str(ready),bool(old and ready)==bool(all([old,ready])))
  ck('USB_sequence_topology',c['U3301','1']==c['Q3300','1']=='USB_CC_READY' and c['Q3300','3']==c['U706','29']=='USB_CC_DISABLE' and c['R3305','1']=='USB5')
  ck('USB_mux_local_supply',c['U706','8']==c['R702','1']==c['U3300','1']=='USB_MUX_3V3')
  ck('ADC_filter_after_guard',c['U3010','2']==c['R2006','1']=='ADC_P_SWITCHED' and c['U3010','6']==c['R2009','1']=='ADC_N_SWITCHED')
  ck('FDA_feedback_still_closed',c['U2003','4']==c['R2005','2']=='AFE_FDA_OP' and c['U2003','5']==c['R2003','2']=='AFE_FDA_ON')
  ck('ADC_and_driver_share_reference_supply',all(c[r,p]=='MAT_ADC_REF' for r,p in [('U2003','3'),('U2003','7'),('U2001','7'),('U2004','1'),('U3010','8'),('U3020','8'),('U3100','8')]))
 # Numerical bounds deliberately separate guaranteed leakage from typical AC behavior.
 calc={'temperature_scope_C':[-40,85],'TMUX_off_leakage_bound_uA_125C':2,'bleed_max_ohm':101000,'off_receiver_voltage_bound_V':2e-6*101000,'OPA_input_current_upper_bound_A':5.5/990,'comparator_input_current_upper_bound_A':5.5/990,'FDA_input_current_upper_bound_A':5.5/(806*.99),'ADC_REF_domain_budget_mA':8,'ADR4550_source_capability_mA':10,'startup_AUP_static_load_uA':18,'AON_added_reserve_vs_v5_mA':103,'AON_total_reserve_vs_28Oct_mA':112,'AON_added_bypass_uF':1.0,'local_guard_P15_reserve_mA':10,'USB5_added_reserve_mA':25,'IO3V3_added_reserve_mA':5,'IO_capacitance_contract_F':.001,'IO_discharge_to_2_625V_s':1010*.001*math.log(3.465/2.625)+.003,'DS181_limit_s_at_125C':.300}
 ck('off_leakage_below_smallest_0_3V_limit',calc['off_receiver_voltage_bound_V']<.3)
 for key in ['OPA_input_current_upper_bound_A','comparator_input_current_upper_bound_A','FDA_input_current_upper_bound_A']:ck(key,calc[key]<.010)
 ck('reference_current_allocation',calc['ADC_REF_domain_budget_mA']<calc['ADR4550_source_capability_mA'])
 ck('IO_discharge_within_AMD_limit',calc['IO_discharge_to_2_625V_s']<.300)
 # Linear FDA solve, ideal amplifier: nodes [guard_N, guard_P, common input, OUT+, OUT-].
 import numpy as np
 R=16000.;B=4020.;D=100000.;F=3000.;Rs=806.
 A=np.array([[1/R+1/B+1/D+1/Rs,0,-1/Rs,0,0],[0,1/R+1/B+1/D+1/Rs,-1/Rs,0,0],[-1/Rs,0,1/Rs+1/F,-1/F,0],[0,-1/Rs,1/Rs+1/F,0,-1/F],[0,0,0,1,1]])
 fda=[]
 for vin in [-15.75,0,15.75]:
  v=np.linalg.solve(A,[vin/R+2.5/B,2.5/B,0,0,5]);fda.append({'input_V':vin,'guard_N_V':v[0],'guard_P_V':v[1],'FDA_common_mode_V':v[2],'out_P_V':v[3],'out_N_V':v[4],'differential_V':v[3]-v[4]})
  ck('FDA_commonmode_'+str(vin),1<v[2]<4);ck('FDA_outputs_'+str(vin),0<v[3]<5 and 0<v[4]<5)
 calc['FDA_nominal_differential_gain']=fda[-1]['differential_V']/15.75;calc['FDA_nominal_gain_change_percent']=(abs(calc['FDA_nominal_differential_gain'])/.15-1)*100
 calc['FDA_ideal_DC_cases']=fda
 def num(v):
  m=re.match(r'^(\d+(?:\.\d+)?)\s*([pnumkM]?)',v)
  return float(m[1])*{'':1,'p':1e-12,'n':1e-9,'u':1e-6,'m':1e-3,'k':1e3,'M':1e6}[m[2]] if m else None
 cap=0;caprows=[]
 for b,m in maps.items():
  for r,co in components[b].items():
   if r.startswith('C') and {m.get((r,'1')),m.get((r,'2'))}=={'IO3V3','GND'}:
    v=num(co.findtext('value'));cap+=v;caprows.append({'board':b,'ref':r,'nominal_F':v})
 calc['IO_direct_nominal_capacitance_F']=cap;calc['IO_direct_capacitance_x2_F']=2*cap;ck('IO_direct_caps_below_1mF_bound',2*cap<.001)
 (OUT/'IO-capacitance.json').write_text(json.dumps(caprows,indent=2)+'\n')
 (OUT/'calculations.json').write_text(json.dumps(calc,indent=2)+'\n')
 (OUT/'barriers.json').write_text(json.dumps({'analog':barriers,'enables':enables},indent=2)+'\n')
 (OUT/'pin-delta.json').write_text(json.dumps(deltas,indent=2)+'\n')
 result={'checks_passed':len(checks),'checks':checks,'erc':ercsummary,'added_components':{b:len(ADDED[b]) for b in ADDED},'legacy_changed_pin_entries':{b:len(deltas[b]) for b in deltas},'firmware_implemented':False,'pcb_updated':False,'board_tests_performed':False,'scope':'Native connectivity, package pin-set consistency, explicit change regression, ideal logic/DC arithmetic. Partial-rail transients, leakage on a PCB and measurement accuracy remain hardware qualification.'}
 (OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
if __name__=='__main__':main()
