#!/usr/bin/env python3
"""Verify all distributed connectors, native KiCad ERC and preserved load circuits.

The interface specification is the reviewed electrical contract, not inferred from
the generated footprints. Requires kicad-cli 10.0.7 for baseline-comparable net names.
"""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/pcb-preparation/distributed-power'
STYLE_RULES={'four_way_junction','single_global_label'}


def run(*args):
    subprocess.run(['kicad-cli',*args],check=True,capture_output=True,text=True)


def write_csv(filename, rows):
    with (OUT/filename).open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=rows[0].keys(),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)


def main():
    spec=json.loads((OUT/'interface.json').read_text())
    baseline=json.loads((OUT/'validation/baseline-nonconnector-connectivity.json').read_text())
    assets=json.loads((OUT/'connector-assets.json').read_text())
    report={};maps={};nodes={};components={};bom=[];pinout=[];pads={}
    with tempfile.TemporaryDirectory(prefix='mira-distributed-') as td:
        for project in ['Power','Control']:
            folder=ROOT/'hardware'/f'MIRA_{project}'
            source=folder/f'MIRA_{project}.kicad_sch'
            xml=Path(td)/(project+'.xml')
            run('sch','export','netlist','--format','kicadxml','-o',str(xml),str(source))
            tree=ET.parse(xml)
            rows=sorted((n.get('ref'),n.get('pin'),net.get('name')) for net in tree.findall('nets/net') for n in net.findall('node'))
            maps[project]={(ref,pin):net for ref,pin,net in rows}
            nodes[project]={(n.get('ref'),n.get('pin')):n for net in tree.findall('nets/net') for n in net.findall('node')}
            components[project]={c.get('ref'):c for c in tree.findall('components/comp')}
            refs={a[project+'_ref'] for a in spec['connectors']}
            load_rows=[r for r in rows if r[0] not in refs]
            digest=hashlib.sha256(json.dumps(load_rows,separators=(',',':')).encode()).hexdigest()
            assert len(load_rows)==baseline[project]['connected_pin_entries']
            assert digest==baseline[project]['sha256_sorted_ref_pin_net'], project+': load/source circuit changed'
            settings=json.loads((folder/f'MIRA_{project}.kicad_pro').read_text())['erc']
            assert not settings['erc_exclusions']
            assert {k for k,v in settings['rule_severities'].items() if v=='ignore'}==STYLE_RULES
            for rule in ['ground_pin_not_ground','footprint_filter','simulation_model_issue']:
                assert settings['rule_severities'][rule] in ['warning','error']
            erc_path=OUT/'validation'/f'{project}.json'
            run('sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(erc_path),str(source))
            erc=json.loads(erc_path.read_text())
            assert not [v for s in erc['sheets'] for v in s['violations']]
            assert len(erc['sheets'])==(51 if project=='Power' else 32)
            report[project]={'active_sheets':len(erc['sheets']),'connector_instances':len(refs),'connected_pin_entries':len(rows),
                             'nonconnector_entries_preserved':len(load_rows),'nonconnector_connectivity_sha256':digest,
                             'erc_errors':0,'erc_warnings':0,'erc_exclusions':0,'ignored_style_checks':sorted(STYLE_RULES)}

        for a in spec['connectors']:
            for project,series in [('Power','SSW'),('Control','HTSW')]:
                ref=a[project+'_ref'];comp=components[project][ref];part=a[project+'_part']
                expected_part=f'{series}-1{a["rows"]:02d}-'+('01' if project=='Power' else '07')+'-S-D'
                assert part==expected_part and comp.findtext('value')==part
                footprint=f'Samtec_{part}_2x{a["rows"]:02d}_P2.54mm_Vertical'
                assert comp.findtext('footprint')=='MIRA_RevA:'+footprint
                props={p.get('name'):p.get('value') for p in comp.findall('property')}
                assert props['MPN']==part and props['PlacementZone']==a['zone']
                assert props['MountSide']==('F.Cu' if project=='Power' else 'B.Cu')
                assert props['Mate']==a[('Control' if project=='Power' else 'Power')+'_part']
                actual_pins={int(pin) for r,pin in maps[project] if r==ref}
                assert actual_pins==set(range(1,a['contacts']+1))
                for pin in a['pins']:
                    key=(ref,str(pin['number']))
                    assert maps[project][key]==pin[project+'_net'],(project,key)
                    assert nodes[project][key].get('pintype')==pin[project+'_type'],(project,key)
                bom.append({'project':project,'ref':ref,'zone':a['zone'],'contacts':a['contacts'],'quantity':1,
                            'manufacturer':'Samtec','mpn':part,'mate':props['Mate'],'mate_ref':props['MateRef'],
                            'footprint':comp.findtext('footprint'),'mount_side':props['MountSide'],
                            'placement_target':a['placement_target'],'datasheet':comp.findtext('datasheet')})
            for pin in a['pins']:
                number=pin['number']
                if number%2==0:assert pin['Power_net']==pin['Control_net']=='GND'
                if a['zone']=='FPGA' and number==17:assert (pin['Power_net'],pin['Control_net'])==('CORE_SENSE_P','CORE1V0')
                else:assert pin['Power_net']==pin['Control_net']
                pinout.append({'zone':a['zone'],'power_ref':a['Power_ref'],'control_ref':a['Control_ref'],'pin':number,
                               'power_net':pin['Power_net'],'control_net':pin['Control_net']})

        for a in assets:
            project=a['project'];part=a['part'];lib=ROOT/'hardware'/f'MIRA_{project}'/'libraries'
            source=(lib/'MIRA_RevA.pretty'/(a['footprint']+'.kicad_mod')).read_text()
            entries=re.findall(r'\(pad "(\d+)" thru_hole \w+ \(at ([-.\d]+) ([-.\d]+)\)\s*\(size ([-.\d]+) ([-.\d]+)\) \(drill ([-.\d]+)\)',source)
            count=len(a['pads']);assert len(entries)==count
            assert {int(p[0]) for p in entries}==set(range(1,count+1))
            pads[project,count]={int(p[0]):(float(p[1]),float(p[2])) for p in entries}
            for pin,x,y,sx,sy,drill in entries:
                assert float(sx)==float(sy)==2 and float(drill)==(1.04 if project=='Power' else 1.02)
            assert '${KIPRJMOD}/libraries/MIRA_RevA.3dshapes/'+a['model'] in source
            assert (lib/'MIRA_RevA.3dshapes'/a['model']).is_file()
            run('fp','export','svg','--footprint',a['footprint'],'--layers','F.Cu,F.SilkS,F.Fab,F.CrtYd',
                '--sketch-pads-on-fab-layers','-o',str(Path(td)/'footprints'),str(lib/'MIRA_RevA.pretty'))
        for a in spec['connectors']:
            for pin in range(1,a['contacts']+1):
                px,py=pads['Power',a['contacts']][pin];cx,cy=pads['Control',a['contacts']][pin]
                assert abs(px+cx)<1e-6 and abs(py-cy)<1e-6,'Mating geometry mismatch'

        # Exactly one modeled external source per Control rail; repeated inputs are passive.
        for rail,source in spec['primary_external_source_pins'].items():
            found=[(a['Control_ref'],p['number']) for a in spec['connectors'] for p in a['pins']
                   if p['Control_net']==rail and nodes['Control'][a['Control_ref'],str(p['number'])].get('pintype')=='power_out']
            assert found==[(source['ref'],source['pin'])],(rail,found)
        negatives=json.loads((ROOT/'docs/pcb-preparation/fixes/negative-supply-review.json').read_text())['checked_pins']
        assert len(negatives)==34
        for p in negatives:
            key=p['ref'],p['vss_pin']
            assert maps['Control'][key]==p['vss_net'] and maps['Control'][p['ref'],p['gnd_pin']]=='GND'
            assert nodes['Control'][key].get('pinfunction').startswith('VSS_NEG_')
            assert nodes['Control'][key].get('pintype')=='power_in'
        # The removed central 64-way footprint must not survive on any active component.
        assert all('132-01-S-D' not in c.findtext('value','') and '132-07-S-D' not in c.findtext('value','')
                   for comps in components.values() for c in comps.values())

    assert len(spec['connectors'])==8 and len(pinout)==118
    insertion=8.51+2.54+5.84-spec['stack_gap_mm'];assert 3.68<=insertion<=6.35
    report['checks']={'connector_pairs':8,'mating_contacts_checked':len(pinout),'unique_native_footprints_loaded':len(assets),
                      'negative_supply_pins_checked':34,'nominal_insertion_mm':round(insertion,2),
                      'baseline_commit':spec['baseline_commit'],'pcb_placement_and_thermal_qualification':'pending'}
    write_csv('connector-bom.csv',bom);write_csv('mating-pinout.csv',pinout)
    (OUT/'validation/summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
