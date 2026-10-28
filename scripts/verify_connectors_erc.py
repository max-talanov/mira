#!/usr/bin/env python3
"""Native netlist/ERC regression for the connector selection and VSS symbol fix.

Requires kicad-cli 10.0.7 (the recorded baseline exporter). Does not edit circuits.
"""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/pcb-preparation/connectors-erc'
VALIDATION = OUT / 'validation'
BASELINE = json.loads((VALIDATION / 'baseline-connectivity.json').read_text())
ASSETS = json.loads((OUT / 'connector-assets.json').read_text())
STYLE_RULES = {'four_way_junction', 'single_global_label'}
REFS = {'Power': ['J4901', 'J4902'], 'Control': ['J400', 'J401']}


def run(*args):
    subprocess.run(['kicad-cli', *args], check=True, capture_output=True, text=True)


def main():
    maps, nodes, components, report, bom, pad_maps = {}, {}, {}, {}, [], {}
    with tempfile.TemporaryDirectory(prefix='mira-connectors-') as temp:
        for project in ['Power', 'Control']:
            folder = ROOT / 'hardware' / f'MIRA_{project}'
            source = folder / f'MIRA_{project}.kicad_sch'
            netlist = Path(temp) / (project + '.xml')
            run('sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(netlist), str(source))
            tree = ET.parse(netlist)
            rows = sorted((n.get('ref'), n.get('pin'), net.get('name'))
                          for net in tree.findall('nets/net') for n in net.findall('node'))
            digest = hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()
            assert len(rows) == BASELINE[project]['pins']
            assert digest == BASELINE[project]['sha256_sorted_ref_pin_net'], project + ': connectivity changed'
            maps[project] = {(ref, pin): net for ref, pin, net in rows}
            nodes[project] = {(n.get('ref'), n.get('pin')): n for net in tree.findall('nets/net') for n in net.findall('node')}
            components[project] = {c.get('ref'): c for c in tree.findall('components/comp')}
            settings = json.loads((folder / f'MIRA_{project}.kicad_pro').read_text())['erc']
            assert not settings['erc_exclusions'], project + ': unexpected ERC exclusions'
            assert {k for k, v in settings['rule_severities'].items() if v == 'ignore'} == STYLE_RULES
            for rule in ['ground_pin_not_ground', 'footprint_filter', 'simulation_model_issue']:
                assert settings['rule_severities'][rule] in ['warning', 'error']
            erc_file = VALIDATION / (project + '.json')
            run('sch', 'erc', '--format', 'json', '--severity-all', '--exit-code-violations', '-o', str(erc_file), str(source))
            erc = json.loads(erc_file.read_text())
            assert not [v for sheet in erc['sheets'] for v in sheet['violations']]
            assert {x['key'] for x in erc['ignored_checks']} == STYLE_RULES
            report[project] = {'connected_pin_entries': len(rows), 'unchanged_from_commit': BASELINE[project]['commit'],
                               'connectivity_sha256': digest, 'erc_violations': 0, 'erc_exclusions': 0,
                               'ignored_style_checks': sorted(STYLE_RULES)}

        for asset in ASSETS:
            project = asset['project']
            count = len(asset['pads'])
            ref = REFS[project][0 if count == 64 else 1]
            comp = components[project][ref]
            assert comp.findtext('value') == asset['part']
            assert comp.findtext('footprint') == 'MIRA_RevA:' + asset['footprint']
            props = {p.get('name'): p.get('value') for p in comp.findall('property')}
            assert props['MPN'] == asset['part'] and props['Manufacturer'] == 'Samtec'
            assert props['MountSide'] == asset['planned_mount_side']
            lib = ROOT / 'hardware' / f'MIRA_{project}' / 'libraries'
            footprint = lib / 'MIRA_RevA.pretty' / (asset['footprint'] + '.kicad_mod')
            text = footprint.read_text()
            pads = re.findall(r'\(pad "(\d+)" thru_hole \w+ \(at ([-.\d]+) ([-.\d]+)\)\s*\(size ([-.\d]+) ([-.\d]+)\) \(drill ([-.\d]+)\)', text)
            assert len(pads) == count and {int(p[0]) for p in pads} == set(range(1, count + 1))
            pad_maps[project, count] = {int(p[0]): (float(p[1]), float(p[2])) for p in pads}
            for pin, x, y, sx, sy, drill in pads:
                assert float(sx) == float(sy) == 2
                assert float(drill) == (1.04 if project == 'Power' else 1.02)
            model_path = '${KIPRJMOD}/libraries/MIRA_RevA.3dshapes/' + asset['model']
            assert model_path in text and (lib / 'MIRA_RevA.3dshapes' / asset['model']).is_file()
            # Native footprint loading, in addition to checking pad geometry and model paths.
            run('fp', 'export', 'svg', '--footprint', asset['footprint'], '--layers', 'F.Cu,F.SilkS,F.Fab,F.CrtYd',
                '--sketch-pads-on-fab-layers', '-o', str(Path(temp) / 'fp'), str(lib / 'MIRA_RevA.pretty'))
            bom.append({'project': project, 'ref': ref, 'quantity': 1, 'manufacturer': 'Samtec',
                        'mpn': asset['part'], 'mate': props['Mate'], 'footprint': comp.findtext('footprint'),
                        'mount_side': props['MountSide'], 'datasheet': comp.findtext('datasheet')})

        pinout = []
        for count, pref, cref in [(64, 'J4901', 'J400'), (18, 'J4902', 'J401')]:
            for pin in range(1, count + 1):
                px, py = pad_maps['Power', count][pin]
                cx, cy = pad_maps['Control', count][pin]
                assert abs(px + cx) < 1e-6 and abs(py - cy) < 1e-6, 'Mating pin alignment'
                pn, cn = maps['Power'][pref, str(pin)], maps['Control'][cref, str(pin)]
                if count == 18 and pin == 17:
                    assert (pn, cn) == ('CORE_SENSE_P', 'CORE1V0')
                else:
                    assert pn == cn, 'Mating net mismatch'
                pinout.append({'power_ref': pref, 'control_ref': cref, 'pin': pin, 'power_net': pn, 'control_net': cn})

        negatives = json.loads((ROOT / 'docs/pcb-preparation/fixes/negative-supply-review.json').read_text())['checked_pins']
        assert len(negatives) == 34
        for item in negatives:
            vp, gp = (item['ref'], item['vss_pin']), (item['ref'], item['gnd_pin'])
            assert maps['Control'][vp] == item['vss_net']
            assert maps['Control'][gp] == 'GND'
            assert nodes['Control'][vp].get('pinfunction').startswith('VSS_NEG_')
            assert nodes['Control'][vp].get('pintype') == 'power_in'
            assert nodes['Control'][gp].get('pintype') == 'power_in'

    insertion = 8.51 + 2.54 + 5.84 - 12
    assert 3.68 <= insertion <= 6.35
    report['checks'] = {'mating_contacts_checked': 82, 'negative_supply_pins_checked': 34,
                        'native_footprints_loaded': 4, 'nominal_insertion_mm': round(insertion, 2),
                        'core_A_per_force_contact_at_5_2A': 5.2 / 8,
                        'core_A_per_return_contact_at_5_2A': round(5.2 / 9, 4),
                        'scope': 'Connectivity, symbol semantics and nominal connector geometry; not PCB or thermal qualification.'}
    for name, rows in [('connector-bom.csv', bom), ('mating-pinout.csv', pinout)]:
        with (OUT / name).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
    (VALIDATION / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
