"""Compare electrical pin partitions after hierarchy/annotation changes.

python3 compare_netlists.py PROJECT BEFORE.xml AFTER.xml [--reference-map MAP.json]
Net names and sheet paths are deliberately excluded from connectivity identity.
"""
import argparse
import gzip
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def load(path, aliases):
    with (gzip.open(path, "rb") if path.suffix == ".gz" else path.open("rb")) as source:
        root = ET.parse(source)
    components = {}
    sources = {}
    for comp in root.findall('components/comp'):
        ref = aliases.get(comp.get('ref'), comp.get('ref'))
        assert ref not in components, f'duplicate component {ref}'
        lib = comp.find('libsource')
        sources[comp.get('ref')] = (lib.get('lib'), lib.get('part'))
        components[ref] = {
            'value': comp.findtext('value'),
            'footprint': comp.findtext('footprint'),
            'datasheet': comp.findtext('datasheet'),
            'libsource': dict(lib.attrib),
            'pins': sorted(pin.get('num') for pin in comp.findall('units/unit/pins/pin')),
            'population': sorted((p.get('name'), p.get('value'))
                                 for p in comp.findall('property')
                                 if p.get('name') in ('dnp', 'exclude_from_bom', 'exclude_from_board')),
        }
    definitions = {
        (part.get('lib'), part.get('part')):
            sorted(tuple(sorted(pin.attrib.items())) for pin in part.findall('pins/pin'))
        for part in root.findall('libparts/libpart')
    }
    pins = set()
    groups = set()
    for net in root.findall('nets/net'):
        group = frozenset((aliases.get(node.get('ref'), node.get('ref')), node.get('pin'))
                          for node in net.findall('node'))
        assert group and not (pins & group), f'pin assigned more than once: {group}'
        pins |= group
        groups.add(group)
    return components, definitions, groups, pins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project')
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    parser.add_argument('--reference-map', type=Path,
                        default=Path(__file__).with_name('reference-map.json'))
    args = parser.parse_args()
    mapping = json.loads(args.reference_map.read_text())[args.project]
    assert len(mapping) == len(set(mapping.values())), 'annotation is not bijective'
    before = load(args.before, {})
    after = load(args.after, {new: old for old, new in mapping.items()})
    labels = ['component attributes / pin numbers', 'symbol pin definitions',
              'electrical pin partitions', 'connected pin identities']
    for label, a, b in zip(labels, before, after):
        if a != b:
            if isinstance(a, dict):
                changed = [k for k in a.keys() | b.keys() if a.get(k) != b.get(k)]
                print(label, 'changed keys:', changed[:20])
            else:
                print(label, 'removed:', list(a - b)[:5], 'added:', list(b - a)[:5])
            raise SystemExit('FAIL: ' + label)
    result = dict(project=args.project, components=len(before[0]),
                  pins=len(before[3]), nets=len(before[2]), result='PASS')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
