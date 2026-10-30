#!/usr/bin/env python3
"""Native path audit and ideal asynchronous latch fault injection, not SPICE/firmware."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from verify_startup import native
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/pcb-preparation/fault-review'

def main():
 checks={};results=[]
 def ck(n,v):
  checks[n]=bool(v)
  if not v:raise AssertionError(n)
 with tempfile.TemporaryDirectory() as td:
  maps={};comps={};digests={}
  for board in ['Power','Control']:
   f=Path(td)/(board+'.xml');subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(f),str(ROOT/'hardware'/('MIRA_'+board)/('MIRA_'+board+'.kicad_sch'))],check=True)
   _,maps[board],comps[board]=native(f)
   digests[board]=hashlib.sha256(json.dumps(sorted([*k,v] for k,v in maps[board].items()),separators=(',',':')).encode()).hexdigest()
  p,c=maps['Power'],maps['Control']
  def pins(board,ref,expect):
   ck(board+'_'+ref+'_pins',all(maps[board].get((ref,str(pin)))==net for pin,net in expect.items()))
  pins('Power','U2501',{1:'AON',5:'AON',6:'PM_WDI',7:'PM_WDO_N',8:'AON_RESET_N',2:'unconnected-(U2501-CWD-Pad2)'})
  pins('Power','U2502',{1:'SYS3V3',5:'SYS3V3',6:'HOST_WDI',7:'HOST_WDO_N',8:'HOST_RESET_N',2:'unconnected-(U2502-CWD-Pad2)'})
  pins('Power','U2603',{2:'AON',4:'AON',12:'AON',10:'AON',3:'PWR_ARM_PULSE',11:'MATRIX_ARM_PULSE',5:'GLOBAL_PWR_PERMIT',9:'MATRIX_PERMIT_RAW'})
  pins('Power','D2501',{1:'AON_RESET_N',2:'PM_WDO_N',3:'PM_RESET_N'})
  pins('Power','U2401',{11:'HOST_ALIVE_PM',12:'PM_RESET_N',15:'PM_WDI',16:'PM_WDO_N',49:'HOST_WDO_N',4:'GLOBAL_CLEAR_N',5:'LINK_READY_H'})
  pins('Power','U3301',{5:'MATRIX_PERMIT',6:'MATRIX_PERMIT_POWER',4:'GND',14:'SYS3V3'})
  pins('Power','J4901',{1:'HOST_WDI',3:'HOST_ALIVE',13:'MATRIX_PERMIT_POWER',15:'HOST_RESET_N',17:'MATRIX_INHIBIT_N'})
  pins('Control','J400',{1:'HOST_WDI',3:'HOST_ALIVE',13:'MATRIX_PERMIT_POWER',15:'HOST_RESET_N',17:'MATRIX_INHIBIT_N'})
  pins('Control','U100',{166:'HOST_WDI',56:'HOST_ALIVE',33:'HOST_RESET_N'})
  pins('Control','R402',{1:'MATRIX_PERMIT_POWER',2:'GND'})
  pins('Control','U401',{2:'MATRIX_PERMIT_POWER',4:'MATRIX_PERMIT',5:'IO3V3'})
  pins('Power','R2509',{1:'HOST_RESET_N',2:'SYS3V3'})
  pins('Power','R2508',{1:'HOST_WDO_N',2:'AON'})
  pins('Control','U1301',{6:'MAT_ALLOWED',1:'MAT_CONFIG_LATCH',2:'MAT_ARM_DATA',5:'MAT_IMAGE_ARMED',7:'IO3V3'})
  pins('Control','U1336',{1:'MAT_FRAME_VALID',2:'MAT_REQUEST_VALID_RAW',4:'MAT_ARM_DATA'})
  pins('Control','U1331',{1:'MAT_SPI_LATCH',2:'MAT_SPI_OE_N',4:'MAT_CONFIG_LATCH'})
  pins('Control','U1305',{2:'MAT_RUN',4:'MAT_OE_N'})
  for ref in ['U1404','U1405','U1406','U1407','U1408','U1409']:pins('Control',ref,{13:'MAT_OE_N',10:'MAT_ALLOWED'})
  for ref in ['Q2101','Q2104','Q2106']:pins('Power',ref,{1:'MATRIX_PERMIT',2:'GND'})
  pins('Power','U5405',{2:'HOST_WDO_N',4:'HOST_RESET_N',5:'AON',3:'GND'})
  ck('PM_watchdog_parts_exact',all(comps['Power'][r].findtext('value')=='TPS3851H33EDRBR' for r in ['U2501','U2502']))
  # Compile the actual AND/inverter topology. Other signals are explicitly supplied states.
  graphs={}
  for board in ['Power','Control']:
   graph={};mp=maps[board]
   for ref,comp in comps[board].items():
    v=comp.findtext('value','');gs=[]
    if '74HCS21' in v:gs=[('6',['1','2','4','5'],'AND'),('8',['9','10','12','13'],'AND')]
    elif '74HC08' in v:gs=[('3',['1','2'],'AND'),('6',['4','5'],'AND'),('8',['9','10'],'AND'),('11',['12','13'],'AND')]
    elif '74LVC1G08' in v:gs=[('4',['1','2'],'AND')]
    elif '74LVC1G11' in v:gs=[('4',['1','3','6'],'AND')]
    elif '74LVC1G17' in v:gs=[('4',['2'],'AND')]
    elif '74LVC1G04' in v:gs=[('4',['2'],'NOT')]
    for op,ip,kind in gs:graph[mp[ref,op]]=(kind,[mp[ref,i] for i in ip])
   graphs[board]=graph
  def ev(board,net,state,seen=()):
   if net in state:return bool(state[net])
   if net in ['AON','IO3V3']:return True
   if net=='GND':return False
   if net in seen:raise AssertionError('cycle '+net)
   kind,ins=graphs[board][net]
   vals=[ev(board,n,state,seen+(net,)) for n in ins]
   return all(vals) if kind=='AND' else not vals[0]
  rails=json.loads((ROOT/'docs/pcb-preparation/sequencing/rail-contract.json').read_text())['rails']
  stop=p['U2601','12'];matrix_clear=p['U2603','13']
  healthy={n:True for n in ['AON_RESET_N','PM_WDO_N','PG_INPUT','FLT_INPUT_N','OC_OK_N','PM_RESET_N','STARTUP_READY_H',stop,'HOST_WDO_N','HOST_RESET_N','MATRIX_INHIBIT_N','LINK_READY_H','HOST_ALIVE_PM','UART_VALID','PC_LINK_VALID','FPGA_PROGRESS']}
  healthy.update({a['pg']:True for a in rails})
  class Machine:
   def __init__(self):self.g=self.m=self.image=True;self.pg=self.pm=self.pl=False
   def step(self,change=None,garm=False,marm=False,load=False):
    s={**healthy,**(change or {})}
    # Common-anode D2501: either supervisor fault can pull PM reset low.
    s['PM_RESET_N']=s['PM_RESET_N'] and s['AON_RESET_N'] and s['PM_WDO_N']
    s['HOST_RESET_N']=s['HOST_RESET_N'] and s['HOST_WDO_N']
    clear=ev('Power',p['U2603','1'],s)
    if not clear:self.g=False
    elif garm and not self.pg:self.g=True
    s['GLOBAL_PWR_PERMIT']=self.g
    for a in rails:s['CMD_'+a['channel']]=self.g and s['STARTUP_READY_H']
    mc=ev('Power',matrix_clear,s)
    if not mc:self.m=False
    elif marm and not self.pm:self.m=True
    permit=self.m and s['STARTUP_READY_H']
    cs={'ADC_REF_READY':s.get('ADC_REF_READY',True),'AFE_SIG_RESET_N':s.get('AFE_SIG_RESET_N',True),'MATRIX_PERMIT':permit,'MAT_FAULT_N':True,'MAT_FAULT_CLEAR_N':True,'MAT_IMAGE_ARMED':self.image,'MAT_OUTPUT_REQ':True,'MAT_REQUEST_VALID':True,'MAT_CONFIG_MATCH':True,'MAT_WRITE_DAC_GUARD_OK':True}
    allowed=ev('Control',c['U1301','6'],cs)
    if not allowed:self.image=False
    elif load and not self.pl:self.image=True # valid frame/data assumed in this scenario only
    cs['MAT_IMAGE_ARMED']=self.image
    oe=ev('Control','MAT_OE_N',cs)
    cs.update(MAT_SERVICE_REQ=True,MAT_VMM_REQ=True,MAT_READ_REQ=True,MAT_WRITE_REQ=True,MAT_PULSE=True)
    dangerous={n:ev('Control',n,cs) for n in ['MAT_SERVICE_SAFE','MAT_VMM_SAFE','MAT_READ_SAFE','MAT_WRITE_PULSE','MAT_VMM_DRIVE_SAFE']}
    self.pg,self.pm,self.pl=garm,marm,load
    return {'global_permit':self.g,'matrix_permit':permit,'image_armed':self.image,'MAT_OE_N':oe,'energizing_logic':dangerous,'commanded_rails':sum(s['CMD_'+a['channel']] for a in rails)}
  local=Machine();lf=local.step({'AFE_SIG_RESET_N':False});lr=local.step();la=local.step(load=True)
  ck('local_guard_loss_clears_image',not lf['image_armed'] and lf['MAT_OE_N'] and not any(lf['energizing_logic'].values()))
  ck('local_guard_restore_needs_reload',not lr['image_armed'] and la['image_armed'])
  ref_model=Machine();rf=ref_model.step({'ADC_REF_READY':False});rr=ref_model.step();ra=ref_model.step(load=True)
  ck('reference_loss_clears_image',not rf['image_armed'] and rf['MAT_OE_N'])
  ck('reference_recovery_needs_reload',not rr['image_armed'] and ra['image_armed'])
  cases=[('PM watchdog','PM_WDO_N','global'),('PM external reset','PM_RESET_N','global'),('AON supervisor','AON_RESET_N','global'),('startup qualifier','STARTUP_READY_H','global'),('input PG','PG_INPUT','global'),('input fault','FLT_INPUT_N','global'),('overcurrent','OC_OK_N','global'),('global STOP',stop,'global'),('host watchdog','HOST_WDO_N','matrix'),('host reset','HOST_RESET_N','matrix'),('matrix inhibit','MATRIX_INHIBIT_N','matrix'),('application heartbeat timeout','LINK_READY_H','matrix')]+[(a['rail']+' PG loss',a['pg'],'matrix') for a in rails]
  for title,signal,kind in cases:
   model=Machine();fault=model.step({signal:False});restored=model.step()
   ck(title+'_matrix_disabled',not fault['matrix_permit'] and not fault['image_armed'] and fault['MAT_OE_N'] and not any(fault['energizing_logic'].values()))
   ck(title+'_expected_global_scope',fault['global_permit']==(kind!='global') and fault['commanded_rails']==(0 if kind=='global' else 15))
   ck(title+'_no_auto_rearm',not restored['matrix_permit'] and not restored['image_armed'] and restored['MAT_OE_N'] and restored['global_permit']==(kind!='global'))
   if kind=='global':model.step(garm=True);model.step()
   power_rearm=model.step(marm=True)
   ck(title+'_requires_Control_reload',power_rearm['matrix_permit'] and not power_rearm['image_armed'] and power_rearm['MAT_OE_N'])
   model.step();loaded=model.step(load=True)
   ck(title+'_valid_reload_can_restore',loaded['image_armed'] and not loaded['MAT_OE_N'])
   results.append({'event':title,'signal':signal,'hardware_scope':kind,'at_fault':fault,'after_signal_restored_without_ARM':restored,'after_Power_rearm_without_Control_reload':power_rearm})
  for signal in ['UART_VALID','PC_LINK_VALID','FPGA_PROGRESS']:
   model=Machine();f=model.step({signal:False})
   ck(signal+'_no_direct_hardware_detection',f['matrix_permit'] and f['global_permit'] and not f['MAT_OE_N'])
   killed=model.step({'MATRIX_INHIBIT_N':False})
   ck(signal+'_PM_KILL_path_disables_matrix',not killed['matrix_permit'] and killed['MAT_OE_N'])
   results.append({'event':signal+' lost while heartbeat continues','hardware_detection':'message/progress validity requires firmware to stop application heartbeat or assert KILL','at_fault':f,'after_PM_asserts_MATRIX_KILL':killed})
  # MCU kill signals drive grounded-source MOSFETs at the actual clear input nets.
  pins('Power','Q2601',{1:'PWR_KILL_GPIO',2:'GND',3:stop})
  pins('Power','Q2602',{1:'MATRIX_KILL_GPIO',2:'GND',3:'MATRIX_INHIBIT_N'})
  model=Machine();model.step({'HOST_WDO_N':False},marm=True);held=model.step(marm=True)
  ck('ARM_held_high_through_fault_does_not_rearm',not held['matrix_permit'])
  model.step();ck('fresh_ARM_edge_after_fault_is_required',model.step(marm=True)['matrix_permit'])
 result={'kicad_version':subprocess.check_output(['kicad-cli','version'],text=True).strip(),'checks_passed':len(checks),'checks':checks,'native_pin_net_sha256':digests,'fault_scenarios':len(results),'scenarios':results,'scope':'Ideal combinational gates/asynchronous flip-flops at valid supply levels. PG low is injected; no analogue detector, watchdog, discharge, propagation-delay or firmware simulation. Hardware and firmware tests pending.'}
 (OUT/'validation').mkdir(parents=True,exist_ok=True);(OUT/'validation/summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['checks','scenarios']},indent=2))
if __name__=='__main__':main()
