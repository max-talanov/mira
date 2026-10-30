#!/usr/bin/env python3
"""Native delta and Ioff receiver pin contract. This is not electrical qualification."""
import json,subprocess,tempfile,hashlib,re,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/pcb-preparation/unpowered-signals'
from verify_signal_remediation import ADDED as REMEDIATION_REFS, normalize_remediation_rows
V5_SIGNAL_REFS={'U5501','U5502','R5501','R5502','R5503','C5501','C5502'}
SIGNAL_REFS=V5_SIGNAL_REFS | REMEDIATION_REFS['Power']
SIGNAL_CHANGES={('U2602','10'):('HOST_RESET_N','HOST_RESET_AON_N'),('R3305','2'):('PM_UART_RX','HOST_UART_TX_RAW'),('R3306','1'):('PM_UART_RX','HOST_UART_TX_RAW')}
def normalize_signal_rows(rows):
 """Reverse only the documented v5 delta; historical baselines stay immutable."""
 out=[]
 for r,p,n in normalize_remediation_rows(rows,'Power'):
  if r in SIGNAL_REFS:continue
  pair=SIGNAL_CHANGES.get((r,p))
  if pair and n==pair[1]:n=pair[0]
  out.append((r,p,n))
 return sorted(out)
def main():
 from verify_signal_remediation import main as verify_v6
 verify_v6()
 checks={};digests={}
 def ck(n,v):
  checks[n]=bool(v)
  if not v:raise AssertionError(n)
 with tempfile.TemporaryDirectory() as td:
  for board in ['Power','Control']:
   f=Path(td)/(board+'.xml');subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(f),str(ROOT/'hardware'/('MIRA_'+board)/('MIRA_'+board+'.kicad_sch'))],check=True)
   t=ET.parse(f);m={(n.get('ref'),n.get('pin')):net.get('name') for net in t.findall('nets/net') for n in net.findall('node')};c={n.get('ref'):n for n in t.findall('components/comp')}
   m={(r,p):n for r,p,n in normalize_remediation_rows([(*k,v) for k,v in m.items()],board)};c={r:v for r,v in c.items() if r not in REMEDIATION_REFS[board]}
   rows=sorted([*k,v] for k,v in m.items());baseline=json.loads((OUT/('baseline-v4-'+board.lower()+'-pins.json')).read_text())['pins']
   digests[board]=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
   ck(board+'_unrelated_pins_unchanged',(normalize_signal_rows(rows) if board=='Power' else [tuple(r) for r in rows])==[tuple(r) for r in baseline])
   if board=='Control':continue
   ck('exactly_seven_new_parts',set(c)-{r[0] for r in baseline}==V5_SIGNAL_REFS)
   delta=[{'ref':r,'pin':p,'before':n,'after':m.get((r,p))} for r,p,n in baseline if m.get((r,p))!=n]
   ck('exactly_three_legacy_pin_changes',len(delta)==3 and all((d['before'],d['after'])==SIGNAL_CHANGES[(d['ref'],d['pin'])] for d in delta))
   def pins(r,e):ck(r+'_pins',all(m.get((r,str(p)))==n for p,n in e.items()))
   pins('U5501',{1:'unconnected-(U5501-NC-Pad1)',2:'HOST_RESET_N',3:'GND',4:'HOST_RESET_AON_N',5:'AON'})
   pins('U5502',{1:'unconnected-(U5502-NC-Pad1)',2:'HOST_UART_TX_RAW',3:'GND',4:'PM_UART_RX',5:'AON'})
   for r,net in [('R5501','HOST_RESET_N'),('R5502','HOST_RESET_AON_N'),('R5503','PM_UART_RX')]:pins(r,{1:net,2:'GND'});ck(r+'_100k',c[r].findtext('value')=='100k')
   for r in ['C5501','C5502']:pins(r,{1:'AON',2:'GND'});ck(r+'_100n',c[r].findtext('value')=='100n')
   for r in ['U5501','U5502']:
    ck(r+'_exact_Ioff_MPN',c[r].findtext('value')=='74LVC1G17GV,125')
    source=c[r].find('libsource');lp=next(p for p in t.findall('libparts/libpart') if p.get('lib')==source.get('lib') and p.get('part')==source.get('part'))
    ck(r+'_power_input_output_types',{p.get('num'):p.get('type') for p in lp.findall('pins/pin')}=={'1':'no_connect','2':'input','3':'power_in','4':'output','5':'power_in'})
   pins('U2602',{10:'HOST_RESET_AON_N'});pins('R3305',{1:'HOST_UART_TX',2:'HOST_UART_TX_RAW'});pins('R3306',{1:'HOST_UART_TX_RAW',2:'GND'})
   ck('reset_AON_fanout_exact',{k for k,v in m.items() if v=='HOST_RESET_AON_N'}=={('U5501','4'),('U2602','10'),('R5502','1')})
   ck('UART_raw_fanout_exact',{k for k,v in m.items() if v=='HOST_UART_TX_RAW'}=={('U5502','2'),('R3305','2'),('R3306','1')})
   ck('UART_PM_fanout_exact',{k for k,v in m.items() if v=='PM_UART_RX'}=={('U5502','4'),('U2401','41'),('R5503','1')})
   for r in sorted(V5_SIGNAL_REFS):
    fp=c[r].findtext('footprint').split(':')[1];file=ROOT/'hardware/MIRA_Power/libraries/MIRA_RevA.pretty'/(fp+'.kicad_mod')
    ck(r+'_package_pin_numbers',set(re.findall(r'\(pad\s+"?(\d+)"?\s',file.read_text()))=={p for rr,p in m if rr==r})
   # Existing unresolved routes are made explicit, not silently called safe.
   pins('D3301',{2:'AON',3:'ADC_VTT'});pins('D3501',{2:'AON',3:'MON_V_INPUT'})
   pins('U3902',{24:'AON'})
 result={'date':'2026-10-30','checks_passed':len(checks),'checks':checks,'native_pin_sha256':digests,'added_components':7,'legacy_pin_changes':delta,'checklist_status':'Historical v5 regression; current status is in signal-remediation/README.md','scope':'Historical v5 connectivity regression after explicit v6 normalization; current actual-net validation runs first. No board measurement.','AON_budget_delta_mA':2,'AON_bypass_delta_uF':0.2}
 (OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
