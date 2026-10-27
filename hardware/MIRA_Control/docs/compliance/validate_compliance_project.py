#!/usr/bin/env python3
"""Read-only, whole-native-project graph audit against explicit design contracts.

Observed final changes never become expectations. Contracts must state each
changed existing endpoint (including its old net), every pin of each new part,
all removed parts, and exact metadata/DNP changes. The complete baseline pin
equivalence graph is edited by those contracts and compared with native KiCad
XML, so an accidental extra connection to an approved net remains detectable.
"""
from pathlib import Path
import argparse, collections, hashlib, importlib.util, json, re, sys, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
COMMON_PATH=Path(__file__).resolve().parent/'native_audit_common.py'
if not COMMON_PATH.is_file():COMMON_PATH=ROOT/'repair/validate_final_project.py'
spec = importlib.util.spec_from_file_location('stage1_audit', COMMON_PATH)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def logical(name):
    if name is None or name in ('NC','NO_CONNECT'):return None
    tail=name.rsplit('/',1)[-1]
    return None if tail.startswith('unconnected-') else tail

def endpoint(s):
    ref,pin=s.rsplit('.',1)
    return ref,pin

def epstr(p):return '.'.join(p)

def field_key(name):
    return {'Reference':'reference','Value':'value','Footprint':'footprint','MPN':'mpn',
        'Manufacturer':'manufacturer','Datasheet':'datasheet','Description':'description'}.get(name,name)

def enrich_native_fields(native,path):
    for comp in ET.parse(path).getroot().findall('components/comp'):
        ref=comp.get('ref');values={'reference':ref,'datasheet':comp.findtext('datasheet') or '',
            'description':comp.findtext('description') or ''}
        for f in comp.findall('fields/field'):values[field_key(f.get('name'))]=f.text or ''
        native['components'][ref].update(values)

def merge_contracts(paths):
    out={'pins':{},'added':{},'removed':set(),'metadata':{},'dnp':{},
         'replaced_refs':set(),'sources':{},'pin_sources':{},'issues':[],'preserved_pin_assertions':{}}
    def put_pin(ep,before,after,origin,new=False):
        value={'from':logical(before),'to':logical(after),'new':new}
        if ep in out['pins'] and out['pins'][ep]!=value:
            out['issues'].append({'type':'conflicting_endpoint_contract','endpoint':ep,'contracts':[out['pins'][ep],value]})
        out['pins'][ep]=value;out['pin_sources'][ep]=origin
    for path in paths:
        data=json.loads(path.read_text());origin=str(path)
        for ref,pins in data.get('modified',{}).items():
            for no,change in pins.items():put_pin(ref+'.'+no,change.get('from'),change.get('to'),origin)
        for ref,part in data.get('added',{}).items():
            if ref in out['added'] and out['added'][ref]!=part:out['issues'].append({'type':'conflicting_added_part','ref':ref})
            out['added'][ref]=part
            for no,net in part.get('pins',{}).items():put_pin(ref+'.'+no,None,net,origin,True)
        out['removed'].update(data.get('removed',[]))
        out['replaced_refs'].update(data.get('replaced_refs',[]))
        for ref,fields in data.get('metadata_changes',{}).items():
            if isinstance(fields.get('from'),dict) and isinstance(fields.get('to'),dict):
                fields={k:{'from':fields['from'].get(k),'to':fields['to'].get(k)} for k in set(fields['from'])|set(fields['to'])}
            for field,change in fields.items():
                key=ref+'.'+field_key(field)
                if key in out['metadata'] and out['metadata'][key]!=change:out['issues'].append({'type':'conflicting_metadata_contract','key':key})
                out['metadata'][key]=change
        for ref,value in data.get('dnp',{}).items():
            out['dnp'][ref]=value if isinstance(value,dict) else {'to':value}
        for ref,pins in data.get('expected_pins',{}).items():
            for no,net in pins.items():out['preserved_pin_assertions'][ref+'.'+no]={'net':logical(net),'source':origin}
        out['sources'][origin]=sha(path)
    return out

def physical_pinsets(index):
    return {r:set().union(*(index['symbol_pins'].get(u['lib_id'],set()) for u in us)) for r,us in index['by_ref'].items()}

def embedded_pin_signatures(project):
    """Ignore library names/graphics, retain unit, type, number, name and geometry."""
    by_ref=collections.defaultdict(set);conflicts=[]
    for path in sorted(project.glob('*.kicad_sch')):
        tree=common.parse_sexp(path.read_text());definitions={}
        for definition in common.kids(common.kid(tree,'lib_symbols') or [],'symbol'):
            signature=[]
            for section in common.kids(definition,'symbol'):
                match=re.search(r'_(\d+)_(\d+)$',section[1]);unitstyle=tuple(match.groups()) if match else ('?', '?')
                for pin in common.kids(section,'pin'):
                    signature.append((unitstyle,tuple(pin[:3]),
                        json.dumps(common.kid(pin,'at'),sort_keys=True),
                        json.dumps(common.kid(pin,'length'),sort_keys=True),
                        json.dumps(common.kid(pin,'name'),sort_keys=True),
                        json.dumps(common.kid(pin,'number'),sort_keys=True)))
            definitions[definition[1]]=tuple(sorted(signature))
        for symbol in common.kids(tree,'symbol'):
            props={p[1]:p[2] for p in common.kids(symbol,'property')};ref=props.get('Reference','')
            if ref and not ref.startswith('#'):
                by_ref[ref].add(definitions.get(common.val(symbol,'lib_id'),()))
    for ref,signatures in by_ref.items():
        if len(signatures)>1:conflicts.append({'ref':ref,'definition_variants':len(signatures)})
    return dict(by_ref),conflicts

def footprint_checks(project,index,pinsets):
    result=[];cache={}
    for ref,units in sorted(index['by_ref'].items()):
        fps={u['footprint'] for u in units}
        if fps=={''} or fps=={None}:continue
        entry={'ref':ref,'footprints':sorted(fps)}
        if len(fps)!=1:
            entry.update(pass_=False,error='Inconsistent footprint among physical units');result.append(entry);continue
        fp=next(iter(fps));lib,name=(fp.split(':',1) if ':' in fp else ('',fp))
        if fp not in cache:
            paths=list(project.glob('**/'+lib+'.pretty/'+name+'.kicad_mod'))
            if len(paths)!=1:cache[fp]={'error':'Footprint file not uniquely resolved','paths':[str(p) for p in paths]}
            else:
                t=common.parse_sexp(paths[0].read_text())
                pads={p[1] for p in common.kids(t,'pad') if p[1]}
                models=[]
                for m in common.kids(t,'model'):
                    model=m[1];resolved=project/str(model).replace('${KIPRJMOD}/','')
                    models.append({'path':model,'exists':resolved.is_file(),'sha256':sha(resolved) if resolved.is_file() else None})
                cache[fp]={'file':str(paths[0]),'sha256':sha(paths[0]),'pads':pads,'models':models}
        c=cache[fp]
        if 'error' in c:entry.update(pass_=False,**c)
        else:
            # Some old MCU symbols have documented exposed/thermal pads. This
            # audit reports exact pad identity; exceptions are never hidden.
            entry.update(symbol_pins=sorted(pinsets[ref]),pad_numbers=sorted(c['pads']),
                missing_pads=sorted(pinsets[ref]-c['pads']),extra_pads=sorted(c['pads']-pinsets[ref]),
                models=c['models'],footprint_sha256=c['sha256'])
            entry['pass_']=pinsets[ref]==c['pads'] and all(m['exists'] for m in c['models'])
        entry['pass']=entry.pop('pass_');result.append(entry)
    return result

def validate(args):
    old=common.load_native(args.baseline_net);new=common.load_native(args.final_net)
    enrich_native_fields(old,args.baseline_net);enrich_native_fields(new,args.final_net)
    oi=common.schematic_index(args.baseline);ni=common.schematic_index(args.working)
    opins=physical_pinsets(oi);npins=physical_pinsets(ni)
    osig,oconflicts=embedded_pin_signatures(args.baseline)
    nsig,nconflicts=embedded_pin_signatures(args.working)
    c=merge_contracts(args.contract);issues=list(c['issues']);assertions=[]
    oldrefs=set(old['components']);newrefs=set(new['components'])
    component_delta={'expected_added':sorted(c['added']),'actual_added':sorted(newrefs-oldrefs),
       'expected_removed':sorted(c['removed']),'actual_removed':sorted(oldrefs-newrefs)}
    for kind,actual,expected in [('added',newrefs-oldrefs,set(c['added'])),('removed',oldrefs-newrefs,c['removed'])]:
        if actual!=expected:issues.append({'type':'component_delta_'+kind,'unexpected':sorted(actual-expected),'missing':sorted(expected-actual)})
    for ep,contract in sorted(c['pins'].items()):
        p=endpoint(ep);before=logical(old['pin_net'].get(p));after=logical(new['pin_net'].get(p))
        pin_exists=p[0] in npins and p[1] in npins[p[0]]
        before_ok=contract['new'] or before==contract['from']
        if not contract['new'] and p[0] not in oldrefs:before_ok=False
        after_ok=pin_exists and after==contract['to']
        assertions.append({'endpoint':ep,'expected_before':contract['from'],'actual_before':before,
            'expected_after':contract['to'],'actual_after':after,'pin_exists':pin_exists,
            'pass':before_ok and after_ok,'contract':c['pin_sources'][ep]})
    for ep,ct in sorted(c['preserved_pin_assertions'].items()):
        p=endpoint(ep);after=logical(new['pin_net'].get(p));exists=p[0] in npins and p[1] in npins[p[0]]
        assertions.append({'endpoint':ep,'expected_after':ct['net'],'actual_after':after,'pin_exists':exists,
            'pass':exists and after==ct['net'],'contract':ct['source'],'kind':'Full preserved/changed component pin contract'})
    # Start with every physical baseline pin, including deliberate NC pins.
    assigned={}
    named=collections.defaultdict(set)
    for name,pins in old['nets'].items():
        if logical(name) is not None:named[logical(name)].add(('baseline',name))
        for p in pins:
            if p[0] not in c['removed']:assigned[p]=('baseline',name)
    for ref,pins in opins.items():
        if ref not in c['removed']:
            for no in pins:assigned.setdefault((ref,no),('isolated',(ref,no)))
    def target(name,p):
        if name is None:return ('isolated',p)
        keys=named.get(name,set())
        if len(keys)>1:issues.append({'type':'ambiguous_target_net','endpoint':epstr(p),'name':name,'candidates':sorted(str(k) for k in keys)})
        return next(iter(keys)) if len(keys)==1 else ('new_named',name)
    for ep,x in c['pins'].items():
        p=endpoint(ep);assigned[p]=target(x['to'],p)
    # Unlisted new physical pins are explicit validation failures, even if NC.
    uncovered=[]
    for ref,part in c['added'].items():
        if ref not in npins:continue
        for no in npins[ref]:
            if ref+'.'+no not in c['pins']:uncovered.append(ref+'.'+no)
        for no in part.get('pins',{}):
            if no not in npins[ref]:issues.append({'type':'contract_pin_not_in_symbol','endpoint':ref+'.'+no})
    expected=collections.defaultdict(set)
    for p,k in assigned.items():expected[k].add(p)
    egroup={p:frozenset(ps) for ps in expected.values() for p in ps}
    actualgroups=list(new['nets'].values())
    actual={p:frozenset(ps) for ps in actualgroups for p in ps}
    for ref,pins in npins.items():
        for no in pins:actual.setdefault((ref,no),frozenset({(ref,no)}))
    differences={}
    for p in set(egroup)|set(actual):
        a=egroup.get(p,frozenset({p}));b=actual.get(p,frozenset({p}))
        if a!=b:
            differences[(a,b)]={'expected_pins':sorted(map(epstr,a)),'actual_pins':sorted(map(epstr,b)),
                 'actual_nets':sorted({new['pin_net'].get(q,'<NC>') for q in b})}
    metadata=[]
    for ref in sorted(oldrefs&newrefs):
        a=old['components'][ref];b=new['components'][ref]
        fields=set(('value','footprint','mpn','lib_id','datasheet','manufacturer','description'))
        fields.update(k.split('.',1)[1] for k in c['metadata'] if k.split('.',1)[0]==ref)
        for field in sorted(fields):
            if a.get(field)!=b.get(field):
                contract=c['metadata'].get(ref+'.'+field)
                # Library canonical suffixes/nicknames may change while the
                # physical pin definition remains exactly equal; report below.
                if field=='lib_id' and osig.get(ref)==nsig.get(ref) and contract is None:
                    passed=True;reason='Library identifier only; unit/type/number/name/geometry signatures equal'
                else:
                    passed=contract is not None and contract.get('from')==a.get(field) and contract.get('to')==b.get(field)
                    reason='Exact field contract' if passed else 'Missing or incorrect exact field contract'
                metadata.append({'ref':ref,'field':field,'before':a.get(field),'after':b.get(field),'pass':passed,'reason':reason})
            elif ref+'.'+field in c['metadata']:
                contract=c['metadata'][ref+'.'+field]
                metadata.append({'ref':ref,'field':field,'before':a.get(field),'after':b.get(field),
                    'pass':contract.get('from')==a.get(field) and contract.get('to')==b.get(field),'reason':'Explicit unchanged metadata contract'})
    for ref,part in sorted(c['added'].items()):
        if ref not in new['components']:continue
        for field in ('value','footprint','mpn','manufacturer','datasheet','description'):
            if field in part:
                value=new['components'][ref].get(field)
                metadata.append({'ref':ref,'field':field,'before':None,'after':value,'expected':part[field],'pass':value==part[field],'reason':'New physical part exact metadata'})
    dnp=[]
    for ref in sorted(oldrefs|newrefs):
        a={u['dnp'] for u in oi['by_ref'].get(ref,[])};b={u['dnp'] for u in ni['by_ref'].get(ref,[])}
        if ref in oldrefs&newrefs and a!=b:
            contract=c['dnp'].get(ref,{})
            passed=a=={contract.get('from')} and b=={contract.get('to')}
            dnp.append({'ref':ref,'before':sorted(a),'after':sorted(b),'pass':passed})
    # UUID replacement is not inferred from ref equality. Unit moves and physical
    # source redesign must be declared by their author.
    identity=[]
    for ref in sorted(oldrefs&newrefs):
        before={u['uuid'] for u in oi['by_ref'].get(ref,[])};after={u['uuid'] for u in ni['by_ref'].get(ref,[])}
        if before!=after:identity.append({'ref':ref,'before':sorted(before),'after':sorted(after),'pass':ref in c['replaced_refs']})
    refs=[]
    shared={'U100','U500'}
    for ref,units in sorted(ni['by_ref'].items()):
        m=re.fullmatch(r'[A-Z]+(\d+)',ref)
        if not m:refs.append({'ref':ref,'pass':False,'reason':'Unexpected reference format'});continue
        number=int(m.group(1));pages=sorted({int(u['file'].split('_',1)[0]) for u in units if re.match(r'^\d+_',u['file'])})
        owner=(number//100)*100
        good=100<=owner<=2200 and (ref in shared or owner in pages)
        # A physical multi-unit analog switch can be shared between sheets;
        # its owner must still contain at least one unit.
        refs.append({'ref':ref,'owner':owner,'sheets':pages,'shared_units':len(units)>1,'pass':good})
    leaf_names=sorted(p.name for p in args.working.glob('*.kicad_sch') if re.match(r'^\d+_',p.name))
    leaf_numbers=[int(n.split('_',1)[0]) for n in leaf_names]
    sheet_order={'numbers':sorted(leaf_numbers),'expected':list(range(100,2300,100)),
        'pass':sorted(leaf_numbers)==list(range(100,2300,100)),
        'names_uppercase_underscore':all(re.fullmatch(r'\d+_[A-Z0-9_]+\.kicad_sch',n) for n in leaf_names)}
    native_sheets=[]
    for sheet in ET.parse(args.final_net).getroot().findall('design/sheet'):
        source=sheet.findtext('title_block/source') or ''
        native_sheets.append({'page':int(sheet.get('number')),'source':source,'name':sheet.get('name')})
    native_leaves=[int(s['source'].split('_',1)[0]) for s in sorted(native_sheets,key=lambda s:s['page']) if re.match(r'^\d+_',s['source'])]
    sheet_order['native_leaf_order']=native_leaves
    sheet_order['native_pages']=native_sheets
    sheet_order['native_order_pass']=native_leaves==list(range(100,2300,100))
    fp=footprint_checks(args.working,ni,npins)
    preserved=[]
    asset_manifest=args.asset_baseline_manifest or (args.baseline/'BASELINE_ASSET_SHA256.json')
    if asset_manifest.is_file():
        entries=json.loads(asset_manifest.read_text())
        for rel,expected_sha in sorted(entries.items()):
            newpath=args.working/rel
            preserved.append({'path':rel,'baseline_sha256':expected_sha,
                'final_sha256':sha(newpath) if newpath.is_file() else None,
                'pass':newpath.is_file() and sha(newpath)==expected_sha})
    for oldpath in sorted(args.baseline.rglob('*')):
        if asset_manifest.is_file():break
        if not oldpath.is_file():continue
        rel=oldpath.relative_to(args.baseline)
        if oldpath.suffix not in ('.kicad_pcb','.kicad_mod','.step','.stp'):continue
        newpath=args.working/rel
        preserved.append({'path':str(rel),'baseline_sha256':sha(oldpath),'final_sha256':sha(newpath) if newpath.is_file() else None,
             'pass':newpath.is_file() and sha(oldpath)==sha(newpath)})
    # Explicit standalone FPGA comparison of all 484 package balls.
    fpga=[]
    for no in sorted(opins.get('U500',set())|npins.get('U500',set())):
        p=('U500',no);a=logical(old['pin_net'].get(p));b=logical(new['pin_net'].get(p));ct=c['pins'].get('U500.'+no)
        fpga.append({'pin':no,'before':a,'after':b,'contracted':ct is not None,'pass':a==b if ct is None else a==ct['from'] and b==ct['to']})
    counts={'contract_pin_assertions':len(assertions),'failed_contract_pins':sum(not x['pass'] for x in assertions),
      'unexpected_physical_connection_groups':len(differences),'contract_issues':len(issues),'uncovered_added_pins':len(uncovered),
      'unexpected_metadata':sum(not x['pass'] for x in metadata),'unapproved_DNP_changes':sum(not x['pass'] for x in dnp),
      'undeclared_UUID_replacements':sum(not x['pass'] for x in identity),'reference_owner_failures':sum(not x['pass'] for x in refs),
      'footprint_pad_or_model_failures':sum(not x['pass'] for x in fp),'preserved_asset_failures':sum(not x['pass'] for x in preserved),
      'FPGA_pin_failures':sum(not x['pass'] for x in fpga),'baseline_duplicate_pin_nodes':len(old['duplicates']),'final_duplicate_pin_nodes':len(new['duplicates'])}
    counts['final_embedded_definition_conflicts']=len(nconflicts)
    fail=any(v for k,v in counts.items() if k!='contract_pin_assertions') or not sheet_order['pass'] or not sheet_order['names_uppercase_underscore'] or not sheet_order['native_order_pass']
    return {'status':'REVIEW_REQUIRED' if fail else 'PASS','counts':counts,'inputs':{'baseline_project':str(args.baseline),'working_project':str(args.working),'baseline_xml_sha256':sha(args.baseline_net),'final_xml_sha256':sha(args.final_net),'contract_sha256':c['sources'],
      'baseline_schematic_sha256':{p.name:sha(p) for p in sorted(args.baseline.glob('*.kicad_sch'))},
      'final_schematic_sha256':{p.name:sha(p) for p in sorted(args.working.glob('*.kicad_sch'))}},
      'method':__doc__,'component_delta':component_delta,'contract_issues':issues,'pin_contract_assertions':assertions,
      'unexpected_connection_groups':list(differences.values()),'uncovered_added_pins':uncovered,
      'metadata_changes':metadata,'DNP_changes':dnp,'unit_UUID_changes':identity,'reference_ownership':refs,'sheet_sequence':sheet_order,
      'native_inventory':{'baseline_physical_components':len(oldrefs),'final_physical_components':len(newrefs),'baseline_physical_pins':sum(map(len,opins.values())),'final_physical_pins':sum(map(len,npins.values())),'baseline_nets':len(old['nets']),'final_nets':len(new['nets']),'FPGA_package_pins_checked':len(fpga)},
      'embedded_definition_conflicts':{'baseline':oconflicts,'final':nconflicts},
      'footprint_pad_and_model_assertions':fp,'preserved_PCB_footprint_STEP_bytes':preserved,'FPGA_all_package_pins':fpga,
      'limits':['Static native schematic graph verification does not prove analog transient behavior, bench safety, firmware/HDL behavior, PCB routing, or timing.','Symbol pad-number equality and STEP existence do not certify mechanical dimensions or assembly compatibility.','Library-ID-only changes are accepted only with equal physical pin sets; independent library reconciliation must also confirm pin names, types, and positions.']}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--baseline',type=Path,default=ROOT/'compliance/baseline/MIRA_Control')
    ap.add_argument('--working',type=Path,default=ROOT/'compliance/working/MIRA_Control')
    ap.add_argument('--baseline-net',type=Path,default=ROOT/'compliance/validation/BASELINE.net.xml')
    ap.add_argument('--final-net',type=Path,required=True)
    ap.add_argument('--contract',type=Path,action='append',default=[])
    ap.add_argument('--asset-baseline-manifest',type=Path,help='Optional path→SHA256 manifest of original PCB/footprint/STEP assets for compact baseline reproduction')
    ap.add_argument('--output',type=Path,default=ROOT/'compliance/validation/FINAL_CONNECTION_VALIDATION.json')
    args=ap.parse_args();result=validate(args);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'counts':result['counts'],'output':str(args.output)},ensure_ascii=False,indent=2))
    return 0 if result['status']=='PASS' else 2
if __name__=='__main__':sys.exit(main())
