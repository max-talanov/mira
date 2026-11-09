"""Cross-project checks on the native KiCad XML exports. Run from any directory."""
import csv
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

here=Path(__file__).resolve().parent
base=Path(sys.argv[1]) if len(sys.argv)>1 else here.parent/'netlists'
plan=Path(sys.argv[2]) if len(sys.argv)>2 else here.parent.parent/'pinplan'

class Netlist:
    def __init__(self, name):
        path=base/(name+'.xml')
        tree=ET.parse(path)
        self.comp={c.get('ref'):c.findtext('value') for c in tree.findall('./components/comp')}
        self.net={}
        self.nodes={}
        self.functions={}
        for net in tree.findall('./nets/net'):
            name=net.get('name')
            self.nodes[name]=[]
            for node in net:
                ref,pin=node.get('ref'),node.get('pin')
                key=ref,pin
                assert key not in self.net, key
                self.net[key]=name
                self.functions[key]=node.get('pinfunction','').removesuffix('_'+pin)
                self.nodes[name].append(key)
    def check(self,ref,pin,name):
        actual=self.net[ref,str(pin)]
        assert actual==name,(ref,pin,actual,name)

c,w,m=(Netlist(name) for name in ['control','power','module'])
for ref in range(400,408):
    cr='J'+str(ref);pr='J'+str(ref+4501)
    a={pin for r,pin in c.net if r==cr};b={pin for r,pin in w.net if r==pr}
    assert a==b
    for pin in a:
        expected='CORE_SENSE_P' if (cr,pin)==('J401','17') else c.net[cr,pin]
        w.check(pr,pin,expected)
count=sum(1 for r,p in c.net if r in {'J'+str(x) for x in range(400,408)})
print('All eight Control-Power connectors:',count,'contacts, including remote sense.')
for pin in range(1,141):
    name=(['BL','NL','WL','GND'][(pin-1)%4] if pin<=128 else 'GND')
    if name!='GND':name+=str((pin-1)//4)
    c.check('J1800',pin,name);m.check('J1',pin,name)
for i in range(32):
    line='WL'+str(i)
    assert sorted(c.comp[r].split(' ')[0] for r,p in c.nodes[line] if r!='J1800')==['120','27']
    for family in ['BL','NL']:
        name=family+str(i)
        assert sorted(c.comp[r] for r,p in c.nodes[name] if r!='J1800')==['ADG442','OPA4192','TMUX6112','TMUX7208']
        for suffix,component,channel in [('_SET','DAC81416','OUT'),('_VADC','AD4696BCPZ','IN'),('_IADC','AD4696BCPZ','IN')]:
            idx=(i//16)+(2 if family=='NL' else 0)
            if component=='DAC81416':expected='U'+str(1000+idx)
            else:expected='U'+str(2000+idx*2+(suffix=='_IADC'))
            matches=[(r,c.functions[r,p]) for r,p in c.nodes[name+suffix] if c.comp[r]==component]
            assert matches==[(expected,channel+str(i%16))],(name,suffix,matches,expected)
for ref in [r for r in c.comp if c.comp[r]=='TMUX6212']:c.check(ref,13,'VWL_PRE12')
for ref in [r for r in c.comp if c.comp[r]=='INA296A2']:c.check(ref,4,'GND')
print('32 WL electrodes separated from the supply; 64 driver and 128 ADC paths; all 140 module contacts.')
# Micron 4 Gb DDR3L, Rev Q, Figure 7. Unused balls are explicitly checked.
balls={
'DDR1V35':'A1 A8 B2 C1 C9 D2 D9 E9 F1 G7 H2 H9 K2 K8 N1 N9 R1 R9',
'GND':'A9 B1 B3 B9 D1 D8 E1 E2 E8 F9 G1 G8 G9 J2 J8 M1 M9 P1 P9 T1 T9',
'DDR_VREF':'H1 M8','DDR_ZQ':'L8'}
for rail,pins in balls.items():
    for pin in pins.split():c.check('U800',pin,rail)
for pin in 'J1 J9 L1 L9 M7'.split():assert c.net['U800',pin].startswith('unconnected-')
ddr=list(csv.DictReader((plan/'ps-ddr3l-x16.csv').open()))
for row in ddr:
    sig=row['Zynq_pin'].removesuffix('_502')
    sig=re.sub(r'DQS_([PN])([01])',r'DQS\2_\1',sig)
    sig=re.sub(r'CK([PN])$',r'CK_\1',sig)
    c.check('U500',row['Zynq_ball'],sig);c.check('U800',row['U800_ball'],sig)
assert sum(len(a.split()) for a in balls.values())+len(ddr)+5==96
print('DDR3L: all 96 physical balls checked, 49 PS signal connections.')
pl=list(csv.DictReader((plan/'pl-pins.csv').open()))
for row in pl:
    if row['MIRA_candidate'] not in ['RESERVED','OPEN']:c.check('U500',row['ball'],row['MIRA_candidate'])
for pin in ['A1','A5']:c.check('U700',pin,'FX_PCLK')
for i in range(32):
    ref,pin=next((r,p) for (r,p),f in c.functions.items() if r=='U700' and f==f'P{i//16}D{i%16}')
    c.check(ref,pin,f'FX_D{i}')
for ref,prefix in [('U7304','FX_USB3TX1_AC'),('U7305','FX_USB3TX2_AC'),('U7306','FX_USB3RX1'),('U7307','FX_USB3RX2')]:
    for pin,suffix in [(1,None),(2,'_P'),(3,'_N')]:c.check(ref,pin,'GND' if suffix is None else prefix+suffix)
for row in csv.DictReader((here/'FX20-decoupling.csv').open()):
    ball=row['ball_or_site'];net=row['pcb_net']
    if ball not in ['bulk','bulk / port']:c.check('U700',ball,net)
    for cap in [row['100n_or_bulk'],row['10n']]:
        if cap:assert {c.net[cap,'1'],c.net[cap,'2']}=={net,'GND'}
print('148 PL assignments; 32 GPIF data and both clocks; four ESD122 pinouts; per-ball FX20 bypass map.')
for cur in [c,w]:
    opens=[(ref,pin,f) for (ref,pin),f in cur.functions.items() if cur.net[ref,pin].startswith('unconnected-') and re.match(r'^(V_\{(DD|SS|REF)|VCC[A-Z_]|VDD[A-Z_]|VSS[A-Z_]|GND)',f)]
    assert not opens,opens
print('No marked-open power or reference balls matching the reviewed naming families.')
