#!/usr/bin/env python3
"""Check native netlist pins and Boolean interlocks; not a transient simulation."""
import json,subprocess,tempfile,itertools
from pathlib import Path
from verify_startup import native
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/pcb-preparation/sequencing'

def main():
 checks={}
 def ck(name,value):
  checks[name]=bool(value)
  if not value:raise AssertionError(name)
 with tempfile.TemporaryDirectory() as td:
  xml=Path(td)/'Power.xml'
  subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(xml),str(ROOT/'hardware/MIRA_Power/MIRA_Power.kicad_sch')],check=True)
  tree,m,c=native(xml)
  rows=json.loads((OUT/'rail-contract.json').read_text())['rails']
  ck('exactly_15_unique_rails',len(rows)==len({a['channel'] for a in rows})==15)
  ck('PM_feedback_on_PC14',m['U2401','4']=='GLOBAL_CLEAR_N')
  ck('clear_feedback_source_and_latch',m['U5203','4']==m['U2603','1']==m['U2401','4'])
  ck('feedback_net_has_only_three_pins',{k for k,v in m.items() if v=='GLOBAL_CLEAR_N'}=={('U5203','4'),('U2603','1'),('U2401','4')})
  ck('PC15_reads_link_readiness',m['U2401','5']=='LINK_READY_H')
  for a in rows:
   ch=a['channel'];ref=a['converter']
   ck(ch+'_request_pin',m['U2401',str(a['request_pin'])]==a['request']=='EN_REQ_'+ch)
   ck(ch+'_PG_pin',m['U2401',str(a['pg_pin'])]==a['pg'])
   ck(ch+'_converter_EN',m[ref,str(a['enable_pin'])]==a['enable_net'])
   ck(ch+'_converter_part',c[ref].findtext('value')==a['part'])
  for ref in ['U1201','U1301','U1401','U1501','U1601','U1701']:
   ck(ref+'_parent_FPGA5V5',m[ref,'11']=='FPGA5V5')
  ck('VTT_parent_DDR_and_AON',m['U1801','2']=='DDR1V35' and m['U1801','10']=='AON')
  ck('ANA5_parent_ANA6',m['U1901','9']=='ANA6')
  ck('ANA33_parent_ANA5',m['U2001','9']=='ANA5')
  # Independently evaluated combinational logic from native pin/net topology.
  # HCS21 is a dual four-input AND, HC08 is a quad two-input AND.
  gates={}
  for ref,comp in c.items():
   value=comp.findtext('value','')
   pins=[]
   if '74HCS21' in value:pins=[('6',['1','2','4','5']),('8',['9','10','12','13'])]
   elif '74HC08' in value:pins=[('3',['1','2']),('6',['4','5']),('8',['9','10']),('11',['12','13'])]
   elif ref=='U5203':pins=[('4',['1','2'])]
   elif ref=='U5501':pins=[('4',['2'])]
   for op,ins in pins:gates[m[ref,op]]=[m[ref,p] for p in ins]
  def evaluate(net,states,stack=()):
   if net in states:return bool(states[net])
   if net=='AON':return True
   if net=='GND':return False
   if net in stack:raise AssertionError('logic cycle '+net)
   if net not in gates:raise AssertionError('unknown input '+net)
   return all(evaluate(x,states,stack+(net,)) for x in gates[net])
  stop=m['U2601','12'];matrix_clear=m['U2603','13']
  state={x:True for x in ['AON_RESET_N','PM_WDO_N','PG_INPUT','FLT_INPUT_N','OC_OK_N','PM_RESET_N','STARTUP_READY_H',stop,'GLOBAL_PWR_PERMIT','HOST_WDO_N','HOST_RESET_N','MATRIX_INHIBIT_N','LINK_READY_H']}
  for a in rows:state[a['pg']]=True;state[a['request']]=True;state['CMD_'+a['channel']]=True
  ck('all_healthy_global_and_matrix_clear',evaluate('GLOBAL_CLEAR_N',state) and evaluate(matrix_clear,state))
  for a in rows:
   ch=a['channel'];s={**state,a['pg']:False}
   ck(ch+'_PG_loss_clears_matrix_only',not evaluate(matrix_clear,s) and evaluate('GLOBAL_CLEAR_N',s))
   s={**state,'CMD_'+ch:False}
   ck(ch+'_command_loss_clears_matrix',not evaluate(matrix_clear,s))
   for req,permit in itertools.product([False,True],repeat=2):
    s={**state,a['request']:req,'GLOBAL_PWR_PERMIT':permit}
    ck(ch+f'_raw_gate_req{int(req)}_permit{int(permit)}',evaluate('CMD_'+ch+'_RAW',s)==(req and permit))
  for fault in ['AON_RESET_N','PM_WDO_N','PG_INPUT','FLT_INPUT_N','OC_OK_N','PM_RESET_N','STARTUP_READY_H',stop]:
   ck('global_clear_follows_'+fault,not evaluate('GLOBAL_CLEAR_N',{**state,fault:False}))
  for fault in ['GLOBAL_PWR_PERMIT','HOST_WDO_N','HOST_RESET_N','MATRIX_INHIBIT_N','LINK_READY_H']:
   ck('matrix_clear_follows_'+fault,not evaluate(matrix_clear,{**state,fault:False}))
  s={**state,**{a['pg']:False for a in rows},**{'CMD_'+a['channel']:False for a in rows}}
  ck('global_start_not_blocked_by_unpowered_rails',evaluate('GLOBAL_CLEAR_N',s) and not evaluate(matrix_clear,s))
 result={'kicad_version':subprocess.check_output(['kicad-cli','version'],text=True).strip(),'checks_passed':len(checks),'checks':checks,'scope':'Native connectivity and ideal Boolean interlocks only. No firmware implementation or hardware timing qualification.','hardware_tests':'pending'}
 (OUT/'validation').mkdir(exist_ok=True)
 (OUT/'validation/summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
