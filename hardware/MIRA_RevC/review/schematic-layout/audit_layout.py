"""Check page numbers, annotation, UUID identity and PCB binding/geometry.

Run with --baseline pointing to the pre-edit project tree.
"""
import argparse
import json
import re
from pathlib import Path
from kicad_sexpr import child, children, kind, leaves, prop, quoted, uuid, walk


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    maps = json.loads(Path(__file__).with_name('reference-map.json').read_text())
    manifest = json.loads(Path(__file__).with_name('pages.json').read_text())
    result = {}
    for project, mapping in maps.items():
        root = args.root / project / (project + '.kicad_sch')
        current = walk(root)
        # walk() sorts real sheet instance pages; root sheet_instances is separate.
        numbers = [int(re.search(r'\(page "(\d+)"\)', child(root.read_text(), 'sheet_instances'))[1])]
        numbers += [int(n['page']) for n in current[1:]]
        assert numbers == list(range(100, 100 * (len(current) + 1), 100)), project
        assert numbers == [n['page'] for n in manifest[project]]
        before = walk(args.baseline / project / (project + '.kicad_sch'))
        old = {uuid(x): x for n in before for x in leaves(n['text'], 'symbol')}
        new = {uuid(x): (x, n) for n in current for x in leaves(n['text'], 'symbol')}
        assert old.keys() == new.keys(), f'{project}: lost/added symbol UUID'
        first_page = {}
        for n, page in zip(current, numbers):
            for sym in leaves(n['text'], 'symbol'):
                first_page.setdefault(prop(sym, 'Reference'), page)
                instances = child(sym, 'instances')
                assert quoted(child(child(instances, 'project'), 'path'))[0] == n['path']
        for uid, oldsym in old.items():
            newsym, node = new[uid]
            ref = prop(newsym, 'Reference')
            assert ref == mapping[prop(oldsym, 'Reference')]
            assert re.match(r'[^\d]+' + str(first_page[ref]) + r'\d{2}$', ref), ref
            for key in ('Value', 'Footprint', 'Datasheet'):
                assert prop(oldsym, key) == prop(newsym, key), (ref, key)
            for key in ('lib_id', 'unit', 'dnp', 'in_bom', 'on_board'):
                assert child(oldsym, key) == child(newsym, key), (ref, key)
        oldpcb = (args.baseline / project / (project + '.kicad_pcb')).read_text()
        pcb = (args.root / project / (project + '.kicad_pcb')).read_text()
        a = {uuid(f): f for f in leaves(oldpcb, 'footprint')}
        b = {uuid(f): f for f in leaves(pcb, 'footprint')}
        assert a.keys() == b.keys(), f'{project}: footprint UUIDs changed'
        restored = pcb
        for uid, original in a.items():
            final = b[uid]
            normalized = final
            oldref, newref = prop(original, 'Reference'), prop(final, 'Reference')
            if oldref in mapping:
                assert newref == mapping[oldref], (project, oldref)
            else:
                assert oldref == newref
            for field in leaves(normalized, 'property'):
                if quoted(field)[0] == 'Reference':
                    normalized = normalized.replace(field, field.replace(json.dumps(newref), json.dumps(oldref), 1), 1)
            if newref is not None:
                normalized = re.sub(r'(\(fp_text\s+reference\s+)"' + re.escape(newref) + '"',
                                    lambda m: m[1] + json.dumps(oldref), normalized)
            oldpath, newpath = child(original, 'path'), child(normalized, 'path')
            if oldpath:
                symbol_id = quoted(oldpath)[0].split('/')[-1]
                if symbol_id in new:
                    symbol, node = new[symbol_id]
                    expected = node['path'] + '/' + symbol_id
                    root_id = '/' + current[0]['uuid']
                    if not quoted(oldpath)[0].startswith(root_id):
                        expected = expected[len(root_id):]
                    assert quoted(newpath)[0] == expected, (project, newref, 'PCB binding')
                normalized = normalized.replace(newpath, oldpath, 1)
            assert normalized == original, (project, oldref, 'PCB geometry/property change')
            restored = restored.replace(final, normalized, 1)
        assert restored == oldpcb, f'{project}: tracks, pads, nets or other PCB data changed'
        result[project] = dict(pages=len(numbers), symbol_units=len(old),
                               pcb_footprints=len(a), result='PASS')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
