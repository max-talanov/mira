"""RevC power electrical checks on KiCad XML exports. Run: python review/prelayout/verify_power.py"""
from pathlib import Path
from itertools import product
from math import sqrt
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent.parent / 'netlists'

class Board:
    def __init__(self, name):
        xml = ET.parse(root / (name + '.xml'))
        self.values = {part.get('ref'): part.findtext('value') for part in xml.findall('./components/comp')}
        self.nets = {(pin.get('ref'), pin.get('pin')): net.get('name')
                     for net in xml.findall('./nets/net') for pin in net}
    def check(self, ref, names):
        for pin, net in names.items():
            assert self.nets.get((ref, str(pin))) == net, (ref, pin, net)
    def resistance(self, ref):
        value = self.values[ref].lower().rstrip('r')
        return float(value.rstrip('k')) * (1000 if value.endswith('k') else 1)

p, c = Board('power'), Board('control')
p.check('U1001',{1:'GND',2:'BUS24',3:'EN_P15_VIN',5:'FB_P15',6:'P15_VCC',7:'CB_P15',8:'P15_SW',9:'GND'})
assert p.values['U1001']=='LMR36520FADDAR'
p.check('Q5804',{1:'CMD_P15'})
p.check('U1102',{1:'BUS24',2:'GND',3:'GND',5:'N15_RAW',6:'N15_REMOTE_EN'})
assert p.values['U1102']=='ECB40W18-72S15N'
p.check('Q1103',{1:'CMD_N15',2:'GND',3:'N15_REMOTE_EN'})
assert all(ref not in p.values for ref in ('Q1101','Q1102','R1103'))
p.check('R1102',{1:'CMD_N15',2:'GND'})
p.check('C1010',{1:'P15_RAW',2:'GND'})
p.check('C1111',{1:'BUS24',2:'GND'})
p.check('U3001',{1:'PG_SYS',2:'PG_SYS'})
p.check('U3101',{1:'CMD_SYS',2:'CMD_SYS'})
p.check('U2401',{10:'EN_REQ_USB',50:'PG_USB'})
assert c.nets['U500','G10'].startswith('unconnected-')
c.check('U7950',{1:'PS_POR_MR_N',2:'GND',3:'CORE1V0',4:'CORE_POR_REF',5:'AON'})
c.check('U605',{1:'PS_POR_N',2:'GND',3:'PS_POR_MR_N',4:'POR_CT',5:'IO3V3',6:'AON'})
c.check('R7740',{1:'PS_POR_N',2:'IO3V3'})
r = p.resistance
print('IC, rail-enable, optional USB, G10 and local reset pin checks passed.')
# TPS26631 thresholds: 0.1% divider, threshold limits 1.176..1.224 V,
# plus worst-sign input leakage up to 150 nA at each threshold pin.
for mode in ('UVLO','OVP'):
    thresholds=[]
    for tol in product((.999,1.001),repeat=4):
        top1,top2,mid,bot = [r(ref)*factor for ref,factor in zip(('R304','R303','R302','R301'),tol)]
        top=top1+top2
        for vt, iu, io in product((1.176,1.224),(-150e-9,150e-9),(-150e-9,150e-9)):
            if mode=='OVP':
                vu=vt+mid*(vt/bot+io)
                thresholds.append(vu+top*(vt/bot+io+iu))
            else:
                vo=(vt-mid*io)/(1+mid/bot)
                thresholds.append(vt+top*((vt-vo)/mid+iu))
    print('%s rising %.2f..%.2f V' % (mode,min(thresholds),max(thresholds)))
    assert max(thresholds)<18 if mode=='UVLO' else min(thresholds)>36
trip=18000/r('R305')
print('Input IOL %.3f A; %.3f..%.3f A (7%% IC and 1%% resistor)'%(trip,trip*.93/1.01,trip*1.07/.99))
# Operator envelope: total P15 and N15 each 1.05 A; first-stage loads, not double-counted secondary rails.
branches={'P15':(15,1.05,.84),'N15':(15,1.05,.83),'FPGA5V5':(5.525,2.1,.85),
          'SYS3V3':(3.315,1.0,.85),'ANA6':(6,.36,.82),'AON':(3.28,.20,.80),'USB5':(5,0,.80)}
power=sum(v*i/eff for v,i,eff in branches.values())+.7
for vin in (18,24,36):
    path=.20
    amps=(vin-sqrt(vin**2-4*path*power))/(2*path)
    print('%2d V: %.2f W at BUS24, %.2f A input, %.2f V at BUS24'%(vin,power,amps,vin-amps*path))
    assert amps<trip*.93/1.01
# Alert bounds are engineering allowances, not manufacturer's all-condition guarantees.
for amp,lim,shunt,gain,offset in [('U3603','R3611','R1004',20,.0035),('U3701','R3703','R1205',50,.004),('U3801','R3805','R1605',50,.004)]:
    assert ('A1I' if gain==20 else 'A2I') in p.values[amp]
    nominal=r(lim)*80e-6/(r(shunt)*gain)
    corners=[((src*r(lim)*tol+err)/(gain*gtol)+v_offset)/(r(shunt)*stol)
             for src,tol,err,gtol,v_offset,stol in product((79.2e-6,80.8e-6),(.99,1.01),(-offset,offset),(.997,1.003),(-.00015,.00015),(.985,1.015))]
    print('%s %s nominal %.3f A, assumed corner range %.3f..%.3f A'%(amp,shunt,nominal,min(corners),max(corners)))
negative=[]
for d1,d2,d3,d4 in product((.9965,1.0035),repeat=4):
    k=(r('R3405')*d4)/(r('R3403')*d3)
    a=(1+k)*(r('R3404')*d2)/(r('R3401')*d1+r('R3404')*d2)
    for aon,raw,shunt,v_error in product((3.18,3.38),(-15.6,-14.4),(.985,1.015),(-.012,.012)):
        for div in (.997,1.003):
            threshold=aon*r('R3202')/(r('R3201')+r('R3202'))*div
            negative.append((threshold-(a-k)*raw+v_error)/(a*r('R1107')*shunt))
print('N15 static nominal %.3f A, assumed corner range %.3f..%.3f A'%(3.28*r('R3202')/(r('R3201')+r('R3202'))/2,min(negative),max(negative)))
print('CORE supervisor reference %.3f V at AON=3.28 V'%(3.28*c.resistance('R7951')/(c.resistance('R7950')+c.resistance('R7951'))))
