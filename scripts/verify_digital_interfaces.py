#!/usr/bin/env python3
"""Independent vendor pin/AF and connectivity checks. This is NOT a MIG run."""
from pathlib import Path
import argparse,csv,json,re,subprocess,tempfile,xml.etree.ElementTree as E
from collections import defaultdict,deque
from digital_pin_delta import DELTA,normalize_digital_rows
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/pcb-preparation/digital-interfaces'
FPGA=ROOT/'fpga/digital-interfaces'
def csvread(path):return list(csv.DictReader(path.open()))
def clean(name,pin):
    name=name.removesuffix('_'+pin)
    name=re.sub(r'~\{([^}]+)\}',r'\1#',name)
    name=name.replace('_{','').replace('}','')
    if name.endswith('_N'):name=name[:-2]+'#'
    return name
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--netlist');args=ap.parse_args()
    checks={}
    def ck(key,value):
        checks[key]=bool(value)
        if not value:raise AssertionError(key)
    with tempfile.TemporaryDirectory() as td:
        fn=Path(args.netlist) if args.netlist else Path(td)/'control.xml'
        if not args.netlist:
            subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(fn),str(ROOT/'hardware/MIRA_Control/MIRA_Control.kicad_sch')],check=True)
        r=E.parse(fn)
        nodes=[(n.get('ref'),n.get('pin'),z.get('name'),n.get('pinfunction')) for z in r.findall('nets/net') for n in z.findall('node')]
        m={(ref,p):net for ref,p,net,_ in nodes};func={(ref,p):f for ref,p,_,f in nodes}
        comp={x.get('ref'):x for x in r.findall('components/comp')}
        ck('no_duplicate_component_pin_nodes',len(m)==len(nodes))
        for ref,part in {'U500':'XC7A200T-2FBG484I','U100':'STM32H745IIT6','U800':'MT41K256M16TW-107:P','U200':'IS42S16320F-7TLI'}.items():
            ck(ref+'_exact_part',comp[ref].findtext('value')==part)
        amd={a['Pin']:a for a in csv.DictReader((OUT/'sources/xc7a200tfbg484pkg.csv').read_text().splitlines()[2:]) if re.fullmatch(r'[A-Z]+\d+',a['Pin'])}
        ck('AMD_484_rows',len(amd)==484)
        for p,a in amd.items():ck('FPGA_'+p+'_vendor_function',func.get(('U500',p))==a['Pin Name']+'_'+p)
        st=csvread(OUT/'sources/stm32h745iit6-vendor-pins.csv')
        ck('ST_176_rows',len(st)==176)
        for a in st:ck('STM_'+a['pin']+'_vendor_pin',func['U100',a['pin']].split('_/_')[0].removesuffix('_'+a['pin'])==a['name'])
        for ref,file,count in [('U800','mt41k256m16tw-vendor-pins.csv',96),('U200','is42s16320f-tsop54-vendor-pins.csv',54)]:
            rows=csvread(OUT/'sources'/file);ck(ref+'_vendor_count',len(rows)==count)
            for a in rows:ck(ref+'_'+a['pin']+'_vendor_function',clean(func[ref,a['pin']],a['pin'])==a['name'])
            padfile=ROOT/'hardware/MIRA_Control/libraries/MIRA_RevA.pretty'/(comp[ref].findtext('footprint').split(':')[1]+'.kicad_mod')
            pads=re.findall(r'\(pad\s+"?([^"\s()]+)"?\s',padfile.read_text())
            ck(ref+'_footprint_exact_pads',set(pads)=={a['pin'] for a in rows} and len(pads)==count)
        for ref,expected in [('U500',set(amd)),('U100',{a['pin'] for a in st})]:
            padfile=ROOT/'hardware/MIRA_Control/libraries/MIRA_RevA.pretty'/(comp[ref].findtext('footprint').split(':')[1]+'.kicad_mod')
            pads=re.findall(r'\(pad\s+"?([^"\s()]+)"?\s',padfile.read_text())
            ck(ref+'_footprint_exact_pads',set(pads)==expected and len(pads)==len(expected))
        # Supply bank checks use vendor VCCO definitions, never an assigned net name.
        for p,a in amd.items():
            if a['Pin Name'].startswith('VCCO_'):
                ck('VCCO_'+p,m['U500',p]==('DDR1V35' if a['Bank'] in ['15','16'] else 'IO3V3'))
        ports=csvread(OUT/'fpga-user-ports.csv');by_net={a['net']:a for a in ports}
        ck('unique_ports_and_pads',len(ports)==len({a['pin'] for a in ports})==len({a['port'] for a in ports}))
        for a in ports:
            ck('port_'+a['port']+'_native_pin',m['U500',a['pin']]==a['net'])
            ck('port_'+a['port']+'_bank',amd[a['pin']]['Bank']==a['bank'])
            if a['bank'] in ['15','16']:ck(a['port']+'_DDR_domain_only',a['net'].startswith(('DDR_','FPGA_SYSCLK_')))
            else:ck(a['port']+'_3V3_standard',a['standard']=='LVCMOS33')
        for byte in range(2):
            dqs=[by_net[f'DDR_DQS_{p}{byte}'] for p in ['P','N']]
            group=amd[dqs[0]['pin']]['Memory Byte Group']
            ck(f'DDR_byte{byte}_DQS_designation',all('_DQS_' in amd[a['pin']]['Pin Name'] for a in dqs))
            ck(f'DDR_byte{byte}_DQS_P_N_pair',re.sub(r'L(\d+)P',r'L\1N',amd[dqs[0]['pin']]['Pin Name'])==amd[dqs[1]['pin']]['Pin Name'])
            ck(f'DDR_byte{byte}_DQ_DM_same_group',all(amd[by_net[net]['pin']]['Memory Byte Group']==group and by_net[net]['bank']=='16' for net in [f'DDR_DQ{i}' for i in range(8*byte,8*byte+8)]+[f'DDR_DM{byte}']))
        for a in ports:
            if a['net'].startswith('DDR_') and not a['net'].startswith(('DDR_DQ','DDR_DM')):ck(a['net']+'_command_bank15',a['bank']=='15')
        cp=amd[by_net['DDR_CK_P']['pin']]['Pin Name'];cn=amd[by_net['DDR_CK_N']['pin']]['Pin Name']
        ck('DDR_CK_true_differential_pair',re.sub(r'L(\d+)P',r'L\1N',cp).replace('_DQS_15','_DQS_A18_15')==cn)
        for net in ['FT_CLK','PHY_RXC','MCU_FPGA_SCK_F','FPGA_SYSCLK_P']:
            name=amd[by_net[net]['pin']]['Pin Name'];ck(net+'_clock_capable_P',bool(re.search(r'L\d+P_.*(MRCC|SRCC)',name)))
        ck('reference_clock_same_DDR_bank',by_net['FPGA_SYSCLK_P']['bank']=='15')
        for p in ['H18','K14','D15','C20']:ck('external_VREF_'+p,m['U500',p]=='DDR_VREF')
        # Memory pin connections are checked against independently transcribed manufacturer names.
        ddrmap={'VDD':'DDR1V35','VDDQ':'DDR1V35','VSS':'GND','VSSQ':'GND','VREFDQ':'DDR_VREF','VREFCA':'DDR_VREF','CS#':'GND','ZQ':'DDR_ZQ','CK':'DDR_CK_P','CK#':'DDR_CK_N','CKE':'DDR_CKE','ODT':'DDR_ODT','RAS#':'DDR_RAS_N','CAS#':'DDR_CAS_N','WE#':'DDR_WE_N','RESET#':'DDR_RESET_N','LDQS':'DDR_DQS_P0','LDQS#':'DDR_DQS_N0','UDQS':'DDR_DQS_P1','UDQS#':'DDR_DQS_N1','LDM':'DDR_DM0','UDM':'DDR_DM1'}
        for a in csvread(OUT/'sources/mt41k256m16tw-vendor-pins.csv'):
            name=a['name'];net=m['U800',a['pin']]
            if name=='NC':ck('DDR_NC_'+a['pin'],net.startswith('unconnected'));continue
            expected=ddrmap.get(name,'DDR_'+name.split('/')[0]);ck('DDR_endpoint_'+a['pin'],net==expected)
        ck('DDR_ZQ_240R',comp['R805'].findtext('value')=='240' and {m['R805','1'],m['R805','2']}=={'DDR_ZQ','GND'})
        ck('DDR_RESET_pulldown',comp['R806'].findtext('value')=='10k' and {m['R806','1'],m['R806','2']}=={'DDR_RESET_N','GND'})
        # Low-value series resistors may separate the FMC labels from the SDRAM labels.
        graph=defaultdict(list)
        for ref,co in comp.items():
            if ref.startswith('R') and co.findtext('value') in ['22','33','47','49.9','0','0R','22R','33R','47R']:
                a,b=m.get((ref,'1')),m.get((ref,'2'))
                if a and b and 'GND' not in [a,b]:graph[a].append((b,ref));graph[b].append((a,ref))
        def route(a,b):
            q=deque([(a,[])]);seen=set()
            while q:
                net,path=q.popleft()
                if net==b:return path
                if net in seen or len(path)>2:continue
                seen.add(net);q.extend((n,path+[ref]) for n,ref in graph[net])
            return None
        vendor_sdram=csvread(OUT/'sources/is42s16320f-tsop54-vendor-pins.csv')
        memnames={a['name']:a['pin'] for a in vendor_sdram}
        smap={'FMC_SDCLK':'CLK','FMC_SDCKE0':'CKE','FMC_SDNE0':'CS#','FMC_SDNRAS':'RAS#','FMC_SDNCAS':'CAS#','FMC_SDNWE':'WE#','FMC_NBL0':'DQML','FMC_NBL1':'DQMH'}
        fmcrows=[]
        for a in csvread(OUT/'sources/stm32-selected-af.csv'):
            ck(a['net']+'_AF_endpoint',m['U100',a['pin']]==a['net'])
            if not a['net'].startswith('FMC_'):continue
            ck(a['net']+'_AF12',a['alternate_function']=='GPIO_AF12_FMC')
            mn=smap.get(a['net'],a['net'].replace('FMC_D','DQ') if a['net'].startswith('FMC_D') else a['net'].removeprefix('FMC_'))
            mp=memnames[mn];path=route(a['net'],m['U200',mp]);ck(a['net']+'_SDRAM_connection',path is not None)
            fmcrows.append({**a,'sdram_pin':mp,'sdram_function':mn,'sdram_net':m['U200',mp],'series_resistors':';'.join(path)})
        ck('FMC_39_signals',len(fmcrows)==39)
        with (OUT/'fmc-sdram-pin-map.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(fmcrows[0]));w.writeheader();w.writerows(fmcrows)
        for a in vendor_sdram:
            if a['name'] in ['VDD','VDDQ','VSS','VSSQ']:ck('SDRAM_supply_'+a['pin'],m['U200',a['pin']]==('GND' if a['name'].startswith('VSS') else 'SYS3V3'))
        baseline=json.loads((OUT/'validation/baseline-control-pins.json').read_text())
        ck('only_declared_MIRA04_and_MIRA05_pin_changes',sorted(normalize_digital_rows([(*k,v) for k,v in m.items()]))==sorted(tuple(x) for x in baseline))
        for k,(old,new) in DELTA.items():ck('current_delta_'+k[1],m[k]==new)
        # Pin XDC must describe exactly the currently connected user ports.
        text=(FPGA/'mira_pinout_candidate.xdc').read_text()
        locs=re.findall(r'set_property PACKAGE_PIN (\S+) \[get_ports \{([^}]+)\}\]',text)
        standards=re.findall(r'set_property IOSTANDARD (\S+) \[get_ports \{([^}]+)\}\]',text)
        ck('XDC_exact_pin_map',sorted(locs)==sorted((a['pin'],a['port']) for a in ports))
        ck('XDC_exact_standards',sorted(standards)==sorted((a['standard'],a['port']) for a in ports))
        ck('LVDS_external_termination',all(f'set_property DIFF_TERM FALSE [get_ports {{sys_clk_{s}}}]' in text for s in ['p','n']))
        ck('no_clock_route_override','CLOCK_DEDICATED_ROUTE FALSE' not in text)
        settings=json.loads((FPGA/'mig-settings.json').read_text())
        ck('MIG_not_falsely_claimed',settings['MIG_validation']=='NOT_RUN')
    result={'date':'2026-10-30','checks_passed':len(checks),'checks':checks,'fpga_vendor_pins':484,'stm32_vendor_pins':176,'ddr_vendor_pins':96,'sdram_vendor_pins':54,'fmc_signals':39,'peripheral_AF_pins':56,'FPGA_user_ports':len(ports),'changed_legacy_pins':2,'MIG_run':False,'Vivado_run':False,'timing_closure':False,'PCB_updated':False,'board_measurements':False,'scope':'Static manufacturer mapping, native schematic connectivity, byte groups, VCCO, clock pins, XDC consistency; NOT vendor tool sign-off.'}
    (OUT/'validation/static-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
if __name__=='__main__':main()
