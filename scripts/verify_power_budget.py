#!/usr/bin/env python3
"""Verify the published budget snapshot independently using Python's standard library."""
import json, math, zipfile, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'docs/pcb-preparation/power-budget'
d = json.loads((P/'power-budget-data.json').read_text())
out = json.loads((P/'power-budget-results.json').read_text())
interface = json.loads((P.parent/'distributed-power/interface.json').read_text())
s = d['settings']
rails = {r['name']:r for r in d['rails']}
checks = 0
def same(actual, expected, label):
    global checks
    assert math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-10), (label,actual,expected)
    checks += 1

core_current = sum(l['peak'] for l in d['loads'] if l['rail']=='CORE1V0')
si = (.6/15000*100-.007*core_current)/(101.007)
core_raw = 1.008+si+.007*(core_current+si)
voltage = {n:abs(r['v']) for n,r in rails.items()}
voltage['CORE1V0'] = core_raw
calc = {}
def rail_calc(n):
    if n in calc: return calc[n]
    r=rails[n]
    children=[x for x in rails if rails[x]['parent']==n]
    loads=[l for l in d['loads'] if l['rail']==n]
    child=[rail_calc(x) for x in children]
    av=sum(l['avg'] for l in loads)+sum(c['in_avg'] for c in child)
    pk=sum(l['peak'] for l in loads)+sum(c['in_peak'] for c in child)
    st=sum(l['start'] for l in loads)+sum(c['in_start'] for c in child)+r['cap_uF']*s['cap_factor']*voltage[n]/(1000*r['ramp'])
    vp=voltage.get(r['parent'],s['vin'])
    def input_i(i): return i+r['iq'] if r['top'] in ('linear','switch') else voltage[n]*i/(vp*r['eta'])+r['iq']
    calc[n]=dict(avg=av,peak=pk,start=st,in_avg=input_i(av),in_peak=input_i(pk),in_start=input_i(st))
    return calc[n]

for i,(n,r) in enumerate(rails.items()):
    c=rail_calc(n);row=out['rails'][i];start=out['start'][i]
    assert row[0]==start[0]==n
    for idx,key in [(13,'avg'),(14,'peak'),(15,'in_avg'),(16,'in_peak')]: same(row[idx],c[key],n+key)
    same(start[9],c['start'],n+'start');same(start[10],c['in_start'],n+'in_start')
    same(sum(x['uF'] for x in r['caprows']),r['cap_uF'],n+'cap inventory')

root_names=[n for n,r in rails.items() if r['parent']=='BUS24']
power=(sum(calc[n]['in_peak'] for n in root_names)+s['vin_aux_a'])*s['vin']
current=(s['vin']-math.sqrt(s['vin']**2-4*s['input_path_ohm']*power))/(2*s['input_path_ohm'])
same(out['input'][1][1],power,'BUS24 peak watts')
same(out['input'][5][1],current,'24V peak current')
same(out['probe']['before'],out['probe']['restored'],'restored input scenario')
assert out['probe']['higher']>current and out['probe']['core5']>current
local={'PHY2V5','MAT_ADC_1V8','MAT_REF_PRE12','MAT_ADC_REF'}
for row in out['contacts']:
    n=row[1]
    expected=sum(l['peak'] for l in d['loads'] if l['rail']==n and l['board']=='Control')+sum(calc[x]['in_peak'] for x,r in rails.items() if r['parent']==n and x in local)
    same(row[5],expected,n+'contact demand')
    same(row[8],max(row[5],row[6])/row[3]*s['sharing_factor'],n+'per contact')
    c=next(c for c in interface['connectors'] if c['Control_ref']==row[0].split('/')[-1])
    pins=[p['number'] for p in c['pins'] if p['Control_net']==n and p['Power_net']!='CORE_SENSE_P']
    assert row[2]==', '.join(map(str,pins)) and row[3]==len(pins)
shared=sum(l['peak'] for l in d['loads'] if l['rail']=='AUX1V8' or (l['rail']=='IO3V3' and l['block'].startswith('U500')))
low=1.008+si-.003*(core_current+shared)-.02*1.008-.01
same(out['core'][-2][3],low,'CORE lower voltage')

# Read exported formula caches; verify the artifact is the same scenario as its JSON.
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(P/'MIRA_Power_Budget_Day2.xlsx') as z:
    errors=[]
    for file in z.namelist():
        if file.startswith('xl/worksheets/sheet') and file.endswith('.xml'):
            tree=ET.fromstring(z.read(file));errors += [(file,c.get('r')) for c in tree.findall('.//m:c',NS) if c.get('t')=='e']
    assert not errors,errors
    input_sheet=ET.fromstring(z.read('xl/worksheets/sheet6.xml'))
    c=input_sheet.find('.//m:c[@r="C30"]/m:v',NS)
    same(float(c.text),current,'XLSX cached 24V peak current')
report={'numeric_comparisons_passed':checks,'contact_rows_checked':len(out['contacts']),'xlsx_formula_errors':0,'hardware_commit':d['baseline'],'excel_desktop_tested':False,'scope':'Calculation and saved-cache checks only; not hardware qualification.'}
print(json.dumps(report,ensure_ascii=False,indent=2))
