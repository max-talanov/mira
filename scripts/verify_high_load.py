#!/usr/bin/env python3
"""Export native KiCad netlists and check the new power/sense paths; no schematic edits."""
from pathlib import Path
import subprocess, tempfile, xml.etree.ElementTree as ET, json, itertools
ROOT=Path(__file__).resolve().parents[1]
INTERFACE=ROOT/'docs/pcb-preparation/distributed-power/interface.json'
OUT=ROOT/('docs/pcb-preparation/distributed-power/validation/high-load' if INTERFACE.exists() else 'docs/pcb-preparation/high-load/validation'); OUT.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='mira-verify-') as td:
 maps={};trees={}
 for project in ['Power','Control']:
  path=Path(td)/(project+'.xml')
  subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(path),str(ROOT/f'hardware/MIRA_{project}/MIRA_{project}.kicad_sch')],check=True)
  trees[project]=ET.parse(path);maps[project]={(node.get('ref'),node.get('pin')):net.get('name') for net in trees[project].findall('nets/net') for node in net.findall('node')}
 p,c=maps['Power'],maps['Control']; checks={}
 def check(name,condition):
  checks[name]=bool(condition)
  if not condition:raise AssertionError(name)
 if INTERFACE.exists():
  interface=json.loads(INTERFACE.read_text())
  check('distributed_interface_pin_map',all(p[a['Power_ref'],str(pin['number'])]==pin['Power_net'] and c[a['Control_ref'],str(pin['number'])]==pin['Control_net'] for a in interface['connectors'] for pin in a['pins']))
 else:
  check('original_64_pin_map_preserved',all(p['J4901',str(i)]==c['J400',str(i)] for i in range(1,65)))
 check('eight_core_force_contacts',all(p['J4902',str(i)]==c['J401',str(i)]=='CORE1V0' for i in range(1,16,2)))
 check('core_return_contacts',all(p['J4902',str(i)]==c['J401',str(i)]=='GND' for i in range(2,27 if INTERFACE.exists() else 19,2)))
 check('control_sense_is_on_load_net',c['J401','17']=='CORE1V0')
 check('sense_reaches_upper_divider',p['J4902','17']==p['R1203','1']==p['R1210','2']=='CORE_SENSE_P')
 check('sense_not_shorted_to_raw_or_output',len({p['R1210','1'],p['R1210','2'],p['R1205','2']})==3)
 check('local_fallback_and_shunt_preserved',p['R1210','1']==p['R1205','1']=='CORE_RAW' and p['R1205','2']=='CORE1V0')
 check('module_input',p['U1102','1']=='BUS24' and p['U1102','2']=='GND')
 check('module_output_polarity',p['U1102','4']=='GND' and p['U1102','5']==p['R1107','1']=='N15_RAW' and p['R1107','2']=='N15')
 check('trim_unconnected',p['U1102','6'].startswith('unconnected-'))
 check('remote_default_pulldown',p['U1102','3']==p['R1103','1']=='N15_REMOTE_EN' and p['R1103','2']=='GND')
 check('pmos_common_source',p['Q1101','2']==p['Q1102','2']==p['R1101','1']==p['C1110','1']=='N15_EN_SOURCE')
 check('pmos_gate_control',p['Q1101','1']==p['Q1102','1']==p['Q1103','3']==p['R1101','2']==p['C1110','2']=='N15_EN_GATE')
 check('pmos_external_drains',p['Q1101','3']=='AON' and p['Q1102','3']=='N15_REMOTE_EN')
 check('n15_command_reaches_driver',p['U2702','6']==p['U5303','5']=='CMD_N15_RAW' and p['U5303','3']==p['Q1103','1']=='CMD_N15' and p['U5303','7']=='STARTUP_READY_H')
 check('nm_os_enable_drive',p['Q1103','1']==p['R1102','1']=='CMD_N15' and p['Q1103','2']==p['R1102','2']=='GND')
 check('analog_feedback_still_present',c['U1903','1']==c['U1903','2'] and c['U1903','6']==c['U1903','7'])
 values={a.get('ref'):a.findtext('value') for a in trees['Power'].findall('components/comp')}
 check('correct_wide_input_single_output_module',values['U1102']=='TEN 30-2413WIN')
 check('ovp_values',values['R301']=='13.7k' and values['R302']=='14.3k')
 check('n15_ocp_divider_values',values['R3201']=='13.7k' and values['R3202']=='10.0k')
 check('n15_ocp_reference_path',p['R3201','1']=='AON' and p['R3201','2']==p['R3202','1']==p['U3201','5'] and p['R3202','2']=='GND')
 (OUT/'connectivity.json').write_text(json.dumps(checks,indent=2)+'\n')
# Input divider: include resistor tolerance+100 K TCR excursion, threshold limits and both pin leakage limits.
# Precision bottom/middle: 0.1%+25ppm/K*100K; existing upper: conservative 1%+100ppm/K*100K.
trips=[]
for st,sm,sb,sv,io,iu in itertools.product([-1,1],repeat=6):
 rt=360000*(1+st*.02);rm=14300*(1+sm*.0035);rb=13700*(1+sb*.0035);v=1.2*(1+sv*.02)
 trips.append(v*(1+(rt+rm)/rb)+io*150e-9*(rt+rm)+iu*150e-9*rt)
result={'nominal_OVP_V':1.2*388000/13700,'rising_OVP_corner_min_V':min(trips),'rising_OVP_corner_max_V':max(trips),'module_continuous_input_max_V':36,'conditions':'Static divider calculation only; no surge response, ageing, PCB leakage or let-through simulation.'}
assert max(trips)<36
(OUT/'ovp-corners.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'connectivity_checks_passed':len(checks),'ovp':result},indent=2))

# DC positive-only sense model. The return resistance is outside the feedback loop.
assumptions={'force_path_ohm_including_shunt':.007,'return_ohm':.003,'sense_wire_ohm':1,
             'source_tolerance':.02,'transient_reserve_V':.01,
             'additional_shared_return_A':(.3+.4)*1.3 if INTERFACE.exists() else 0}
scenarios=[]
for current in [0,4,5.2]:
 sense_current=(.6/15000*100-.007*current)/(100+1+.007)
 load_positive=1.008+sense_current
 raw=load_positive+.007*(current+sense_current)
 load_voltage=load_positive-.003*(current+assumptions['additional_shared_return_A'])
 scenarios.append({'current_A':current,'raw_V':raw,'load_V_nominal':load_voltage,
                   'lower_V_with_2pct_and_10mV':load_voltage-.02*1.008-.01,'sense_line_A':sense_current})
(OUT/'core-dc-scenarios.json').write_text(json.dumps({'assumptions':assumptions,'scenarios':scenarios,
 'open_sense_no_load_nominal_V':.6*(1+(10200+100)/15000),
 'scope':'Conditional DC calculation, not measured PCB performance or feedback-loop simulation.'},indent=2)+'\n')

# N15 differential-amplifier mismatch is included explicitly, not just gain error.
# Precision resistors: 0.1% + 25 ppm/K * 100 K. Shunt envelope: 2% total.
# Error budgets at amplifier output / comparator input include headroom for DC errors;
# they do not represent measured noise, ripple or startup behaviour.
ocp=[]
for signs in itertools.product([-1,1],repeat=11):
 sa,sv,s1,s3,s4,s5,st,sb,ss,se,sc=signs
 aon=3.3+sa*.15;vraw=-15+sv*.75
 r1=10000*(1+s1*.0035);r3=10000*(1+s3*.0035)
 r4=200000*(1+s4*.0035);r5=200000*(1+s5*.0035)
 rt=13700*(1+st*.0035);rb=10000*(1+sb*.0035);shunt=.1*(1+ss*.02)
 b=r5/r3;k=(1+b)*r4/(r1+r4)
 trip=(aon*rb/(rt+rb)+sc*.010-se*.050-(k-b)*vraw)/(k*shunt)
 ocp.append(trip)
ocp_result={'nominal_trip_A_at_AON_3_28V':3.28/2.37/2,'corner_min_A':min(ocp),'corner_max_A':max(ocp),
 'provisional_target_A':.36*1.3,'shunt_power_W_at_corner_max':max(ocp)**2*.102,
 'assumptions':{'AON_V':[3.15,3.45],'N15_RAW_V':[-15.75,-14.25],'precision_resistor_total_tolerance':.0035,
 'shunt_total_tolerance':.02,'amplifier_output_error_budget_V':.05,'comparator_input_error_budget_V':.01},
 'scope':'Static protection coordination only. Connector, fault energy, startup and dynamic immunity require validation.'}
assert min(ocp)>.36*1.3
assert ocp_result['shunt_power_W_at_corner_max']<.25
(OUT/'n15-ocp-corners.json').write_text(json.dumps(ocp_result,indent=2)+'\n')
print(json.dumps({'n15_ocp':ocp_result},indent=2))
