#!/usr/bin/env python3
"""MIRA.06 reproducible BOM, exact schematic preservation and land checks.

Run from any directory with Python 3; add --native for KiCad netlist/ERC checks.
This verifies design records, not purchasing, solder quality or socket clearance.
"""
import argparse, collections, csv, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware/MIRA_Control/docs/compliance'))
from native_audit_common import parse_sexp,kids,kid,val
OUT=ROOT/'docs/pcb-preparation/components-assembly'
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def sheets(board):
    base=ROOT/'hardware'/('MIRA_'+board);seen=set()
    def visit(path):
        if path in seen:return
        seen.add(path);tree=parse_sexp(path.read_text())
        yield path,tree
        for sheet in kids(tree,'sheet'):
            props={x[1]:x[2] for x in kids(sheet,'property')}
            yield from visit(path.parent/props['Sheetfile'])
    yield from visit(base/('MIRA_'+board+'.kicad_sch'))
def csvwrite(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--native',action='store_true');a=ap.parse_args()
    (OUT/'validation/summary.json').unlink(missing_ok=True)
    checks={}
    def ck(k,v):
        checks[k]=bool(v)
        if not v:raise AssertionError(k)
    delta=json.loads((OUT/'bom-delta.json').read_text())
    dm={(d['board'],d['ref']):d for d in delta};seen=set();rows=[];counts={}
    expected=json.loads((OUT/'validation/baseline-schematic-hashes.json').read_text())
    for board,total in [('Control',1352),('Power',796)]:
        byref={};sc=0
        for path,tree in sheets(board):
            sc+=1
            # The same corrected THP210 order code is retained in the cached
            # symbol and local library so later instantiation cannot reintroduce it.
            for definition in kids(kid(tree,'lib_symbols') or [],'symbol'):
                if definition[1]=='MIRA_RevA:THP210_MIRA_MAT':
                    prop=next(p for p in kids(definition,'property') if p[1]=='MPN')
                    ck('cached_THP210_order_code',prop[2]=='THP210DR')
                    prop[2]='THP210IDR'
            for symbol in kids(tree,'symbol'):
                pr={x[1]:x[2] for x in kids(symbol,'property')};ref=pr.get('Reference','')
                if not ref or ref.startswith('#'):continue
                row={k:pr.get(k,'') for k in ['Reference','Value','Footprint','Datasheet','MPN','Manufacturer']}
                row.update(board=board,sheet=path.name,lib_id=val(symbol,'lib_id'),in_bom=val(symbol,'in_bom'),dnp=val(symbol,'dnp','no'))
                if ref in byref:
                    ck(board+'_'+ref+'_multiunit_fields',all(row[k]==byref[ref][k] for k in ['MPN','Value','Footprint','Manufacturer']))
                else:byref[ref]=row
                d=dm.get((board,ref))
                if d:
                    ck(board+'_'+ref+'_approved_fields',all(pr.get(k)==v for k,v in d['after'].items()))
                    for p in kids(symbol,'property'):
                        if p[1] in d['before']:p[2]=d['before'][p[1]]
                    seen.add((board,ref))
            rel=str(path.relative_to(ROOT))
            ck(rel+'_all_other_structure_preserved',digest(tree)==expected[rel])
        ck(board+'_component_count',len(byref)==total)
        counts[board]={'sheets':sc,'components':len(byref),'EIA_0201':sum('_0201_' in r['Footprint'] for r in byref.values()),'DNP':sum(r['dnp']=='yes' for r in byref.values()),'EIA_0201_fitted':sum('_0201_' in r['Footprint'] and r['dnp']!='yes' for r in byref.values())}
        rows.extend(byref.values())
    ck('all_112_delta_records_applied',seen==set(dm) and len(dm)==112)
    library_delta=json.loads((OUT/'library-default-delta.json').read_text())
    ck('exact_library_default_changes',all(hashlib.sha256((ROOT/d['path']).read_bytes()).hexdigest()==d['sha256_after'] for d in library_delta))
    missing=[(r['board'],r['Reference']) for r in rows if not r['MPN']]
    ck('only_non_purchased_solder_jumper_has_no_MPN',missing==[('Power','JP301')])
    ck('no_generic_header_MPN',all('generic' not in r['MPN'].lower() for r in rows))
    ck('BSS138N_full_order_code',next(r for r in rows if r['board']=='Control' and r['Reference']=='Q2203')['MPN']=='BSS138NH6327XTSA2')
    ck('844_EIA_0201',sum(x['EIA_0201'] for x in counts.values())==844)
    ck('45_DNP_excluded_from_fitted_purchase_quantity',sum(x['DNP'] for x in counts.values())==45)
    ck('799_fitted_EIA_0201',sum(x['EIA_0201_fitted'] for x in counts.values())==799)
    for r in rows:
        r['procurement']='PCB_FEATURE_NOT_PURCHASED' if r['Reference']=='JP301' and r['board']=='Power' else 'DNP_NOT_PURCHASED' if r['dnp']=='yes' else 'RFQ_REQUIRED_NOT_ORDERED'
    rows.sort(key=lambda r:(r['board'],r['Reference']))
    csvwrite(OUT/'bom-by-reference.csv',rows)
    groups=collections.defaultdict(list)
    for r in rows:groups[(r['MPN'],r['Manufacturer'],r['Value'],r['Footprint'])].append(r)
    grouped=[]
    for (mpn,mfr,v,fp),rs in sorted(groups.items()):
        fitted=sum(r['dnp']!='yes' and r['in_bom']=='yes' for r in rs)
        grouped.append(dict(MPN=mpn,Manufacturer=mfr,Value=v,Footprint=fp,quantity_total_positions=len(rs),quantity_to_fit_and_buy=fitted,quantity_DNP=sum(r['dnp']=='yes' for r in rs),quantity_PCB_feature=sum(r['in_bom']!='yes' for r in rs),references='; '.join(r['board']+':'+r['Reference'] for r in rs),procurement='RFQ_REQUIRED_NOT_ORDERED' if fitted else rs[0]['procurement']))
    csvwrite(OUT/'bom-grouped.csv',grouped)
    fp=ROOT/'hardware/MIRA_Control/libraries/MIRA_RevA.pretty/Samtec_FTSH-105-01-L-DV-K_2x05_P1.27mm_SMD.kicad_mod'
    pads=kids(parse_sexp(fp.read_text()),'pad');pm={p[1]:p for p in pads}
    ck('FTSH_all_10_contacts_including_pin7',set(pm)=={str(n) for n in range(1,11)})
    for n in range(1,11):
        p=pm[str(n)];xy=list(map(float,kid(p,'at')[1:3]));size=list(map(float,kid(p,'size')[1:3]))
        ck('FTSH_'+str(n)+'_SMT_manufacturer_land',p[2:4]==['smd','rect'] and all(abs(a-b)<1e-8 for a,b in zip(xy,[((n-1)//2-2)*1.27,2.4125 if n%2 else -2.4125])) and size==[.74,2.035] and kid(p,'layers')[1:]==['F.Cu','F.Paste','F.Mask'] and kid(p,'drill') is None)
    lib=fp.parent
    pads=kids(parse_sexp((lib/'Wuerth_61300611121_1x06_P2.54mm_Vertical.kicad_mod').read_text()),'pad')
    ck('Wuerth_6_finished_holes_1_10mm',len(pads)==6 and all(p[2]=='thru_hole' and abs(float(val(p,'drill'))-1.1)<1e-8 for p in pads))
    ck('Wuerth_numbering_pitch_preserved',all(kid(p,'at')[1:]==['0',str((int(p[1])-1)*2.54).rstrip('0').rstrip('.')] if int(p[1])>1 else kid(p,'at')[1:]==['0','0'] for p in pads))
    socket=kids(parse_sexp((lib/'ICS-CQFP64-1830-1830-100-1.kicad_mod').read_text()),'pad')
    contacts=[p for p in socket if p[1]]
    ck('socket_64_pressure_contacts_without_paste_or_drill',len(contacts)==64 and {p[1] for p in contacts}=={str(i) for i in range(1,65)} and all(p[2:4]==['smd','circle'] and kid(p,'layers')[1:]==['F.Cu','F.Mask'] and kid(p,'drill') is None and list(map(float,kid(p,'size')[1:]))==[.5,.5] for p in contacts))
    ck('socket_6_nonplated_mechanical_holes',len([p for p in socket if p[2]=='np_thru_hole'])==6)
    erc={}
    if a.native:
        for board in counts:
            path=ROOT/'hardware'/('MIRA_'+board)/('MIRA_'+board+'.kicad_sch')
            xml=OUT/'validation'/(board+'-current.xml');ef=OUT/'validation'/(board+'-erc.json')
            # Export to a fresh temporary path; only publish a complete parsed XML.
            with tempfile.TemporaryDirectory(prefix='mira06-native-') as td:
                exported=Path(td)/(board+'.xml')
                subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(exported),str(path)],check=True)
                ET.parse(exported)
                xml.write_bytes(exported.read_bytes())
            subprocess.run(['kicad-cli','sch','erc','--severity-all','--exit-code-violations','--format','json','-o',str(ef),str(path)],check=True)
            e=json.loads(ef.read_text());erc[board]={'sheets':len(e['sheets']),'violations':sum(len(s['violations']) for s in e['sheets'])}
            ck(board+'_native_ERC_clear',erc[board]['violations']==0 and erc[board]['sheets']==counts[board]['sheets'])
            tree=ET.parse(xml);ck(board+'_native_component_count',len(tree.findall('components/comp'))==counts[board]['components'])
            if board=='Control':
                def pins(p):return sorted((n.get('ref'),n.get('pin'),z.get('name')) for z in ET.parse(p).findall('nets/net') for n in z.findall('node'))
                ck('Control_all_5402_native_pin_rows_unchanged',pins(xml)==pins(ROOT/'docs/pcb-preparation/analog-requirements/validation/control-current.xml') and len(pins(xml))==5402)
    out={'date':'2026-10-30','baseline_github_main':'22bed51bd2580fe7af3857461a78461435fbc19d','checks_passed':len(checks),'checks':checks,'boards':counts,'total_components':len(rows),'grouped_BOM_rows':len(grouped),'changed_component_records':len(delta),'native_checks_run':a.native,'ERC':erc,'procurement_confirmed':False,'assembly_vendor_qualified':False,'socket_manufacturer_drawing_received':False,'manufacturing_release':False}
    (OUT/'validation/summary.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))
if __name__=='__main__':main()
