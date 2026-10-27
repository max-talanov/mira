#!/usr/bin/env python3
"""Read-only native-netlist audit for the repaired MIRA project.

Typical use after final renumbering:
  python repair/validate_final_project.py \
    --source-netlist repair/research/baseline_reconciled.net.xml \
    --final-netlist repair/research/final.net.xml \
    --manifest repair/renumber_manifest.json \
    --output repair/research/final_validation.json

The supplied XML must come from kicad-cli's *whole-project* kicadxml export.
No schematic, library, PCB, or manifest is ever written. UUID identity takes
precedence over ref-number similarity. Pin graph comparison does not depend on
sheet names, hierarchical paths, automatic net names, or reference numbering.
All changes and any unresolved identity are retained in the JSON for review.
"""
from pathlib import Path
import argparse,collections,json,re,sys,xml.etree.ElementTree as ET

DEFAULT=Path(__file__).resolve().parent

def parse_sexp(s):
    stack=[]; result=None
    for tok in re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',s):
        if tok=='(':
            a=[]
            if stack:stack[-1].append(a)
            stack.append(a)
        elif tok==')':result=stack.pop()
        else:stack[-1].append(json.loads(tok) if tok.startswith('"') else tok)
    return result

def kids(a,key):return [x for x in a if isinstance(x,list) and x and x[0]==key]
def kid(a,key):return next(iter(kids(a,key)),None)
def val(a,key,default=None):
    x=kid(a,key);return x[1] if x and len(x)>1 else default

def schematic_index(project):
    """Index actual instantiated units, including UUIDs and DNP, not lib units."""
    units={};by_ref=collections.defaultdict(list);symbol_pins={}
    for path in sorted(project.glob('*.kicad_sch')):
        tree=parse_sexp(path.read_text())
        lib=kid(tree,'lib_symbols') or []
        for definition in kids(lib,'symbol'):
            pinset=set()
            for section in kids(definition,'symbol'):
                for p in kids(section,'pin'):
                    no=val(p,'number')
                    if no is not None:pinset.add(no)
            symbol_pins[definition[1]]=pinset
        for symbol in kids(tree,'symbol'):
            props={p[1]:p[2] for p in kids(symbol,'property')}
            ref=props.get('Reference','')
            if not ref or ref.startswith('#'):continue
            u={'ref':ref,'uuid':val(symbol,'uuid'),'unit':val(symbol,'unit'),'lib_id':val(symbol,'lib_id'),
               'value':props.get('Value'),'footprint':props.get('Footprint'),'mpn':props.get('MPN'),
               'dnp':val(symbol,'dnp','no')=='yes','file':path.name}
            units[u['uuid']]=u;by_ref[ref].append(u)
    return {'units':units,'by_ref':dict(by_ref),'symbol_pins':symbol_pins}

def load_native(path):
    root=ET.parse(path).getroot();comps={};nets={};pin_net={};duplicates=[]
    for c in root.findall('components/comp'):
        ref=c.get('ref');fields={x.get('name'):x.text or '' for x in c.findall('fields/field')}
        comps[ref]={'ref':ref,'uuids':set((c.findtext('tstamps') or '').split()),
                    'value':c.findtext('value'),'footprint':c.findtext('footprint'),
                    'mpn':fields.get('MPN'),'lib_id':(c.find('libsource').get('lib','')+':'+c.find('libsource').get('part','')) if c.find('libsource') is not None else '',
                    'sheet_path':(c.find('sheetpath').get('tstamps','') if c.find('sheetpath') is not None else '')}
    for n in root.findall('nets/net'):
        name=n.get('name');nodes=set()
        for e in n.findall('node'):
            pin=(e.get('ref'),e.get('pin'));nodes.add(pin)
            if pin in pin_net:duplicates.append({'pin':'.'.join(pin),'nets':[pin_net[pin],name]})
            pin_net[pin]=name
        nets[name]=nodes
    return {'components':comps,'nets':nets,'pin_net':pin_net,'duplicates':duplicates,
            'source':root.findtext('design/source'),'tool':root.findtext('design/tool')}

REF_RE=re.compile(r'^[A-Z]+\d+$')
def load_refmap(path):
    """Accept a plain old:new map, common named maps, or old/new row records."""
    if path is None:return {},[]
    data=json.loads(path.read_text());out={};conflicts=[]
    old_keys=('old','old_ref','original_ref','source_ref','from','before','reference_before')
    new_keys=('new','new_ref','final_ref','target_ref','to','after','reference_after')
    def add(a,b):
        if not isinstance(a,str) or not isinstance(b,str) or not REF_RE.fullmatch(a) or not REF_RE.fullmatch(b):return
        if a in out and out[a]!=b:conflicts.append({'old':a,'new':[out[a],b]})
        else:out[a]=b
    def visit(obj):
        if isinstance(obj,dict):
            for a,b in obj.items():add(a,b)
            old=next((obj[k] for k in old_keys if k in obj),None)
            new=next((obj[k] for k in new_keys if k in obj),None)
            add(old,new)
            for v in obj.values():
                if isinstance(v,(dict,list)):visit(v)
        elif isinstance(obj,list):
            for x in obj:visit(x)
    visit(data);return out,conflicts

def component_identity(source,final,source_sch,final_sch,manifest,reassignments=()):
    uuid_old={};issues=[];mapping={};reasons={}
    for old,c in source['components'].items():
        uuids=c['uuids']|{x['uuid'] for x in source_sch['by_ref'].get(old,[])}
        for u in uuids:uuid_old.setdefault(u,set()).add(old)
    used=set()
    for new,c in final['components'].items():
        uuids=c['uuids']|{x['uuid'] for x in final_sch['by_ref'].get(new,[])}
        candidates=set().union(*(uuid_old.get(u,set()) for u in uuids)) if uuids else set()
        if len(candidates)==1:
            old=next(iter(candidates))
            if old in used:issues.append({'type':'duplicate_physical_identity','old':old,'new':new});continue
            mapping[old]=new;used.add(old);reasons[old]='stable unit UUID'
        elif len(candidates)>1:
            manifest_choices=[old for old in candidates if manifest.get(old)==new]
            authorized=any(candidates==set(group) for group in reassignments)
            if authorized and len(manifest_choices)==1:
                old=manifest_choices[0];mapping[old]=new;used.add(old);reasons[old]='documented unit reassignment; manifest disambiguates UUIDs '+','.join(sorted(candidates))
            else:issues.append({'type':'ambiguous_UUID_identity','new':new,'old_candidates':sorted(candidates)})
    for old,new in manifest.items():
        if old not in source['components'] or new not in final['components']:continue
        if old in mapping and mapping[old]!=new:issues.append({'type':'manifest_UUID_disagreement','old':old,'by_UUID':mapping[old],'by_manifest':new})
        elif old not in mapping and new not in mapping.values():mapping[old]=new;reasons[old]='manifest (replaced symbol UUID)'
    # Before renumbering, or explicitly unchanged refs, replacement UUIDs can be resolved.
    for old in source['components']:
        if old not in mapping and old in final['components'] and old not in mapping.values() and (not manifest or manifest.get(old,old)==old):
            mapping[old]=old;reasons[old]='unchanged reference fallback; inspect replacement'
    return mapping,reasons,issues

def oldpin(s):
    a,b=s.rsplit('.',1);return a,b

def expectations(journal_dir):
    """Exact pin contract, extracted from structured journals plus explicit adapters
    for journals whose pin descriptions are prose. Unknown journals are listed.
    """
    names=['interface_intentional_changes.json','logic_intentional_changes.json','digital_intentional_changes.json','dac_matrix_repairs.json','adc_changes.json']
    js={name:json.loads((journal_dir/name).read_text()) for name in names}
    pin={};why={};added=set();removed=set();modified=set();dnp={};same=[];metadata_allowed=set()
    def expect(endpoint,net,origin):
        if endpoint in pin and pin[endpoint]!=net:raise ValueError('Conflicting expected pin '+endpoint)
        pin[endpoint]=net;why[endpoint]=origin
    for endpoint,net in js[names[0]]['expected_pin_nets'].items():expect(endpoint,net,names[0])
    added.update(js[names[0]]['added_refs'])
    logic=js[names[1]]
    for category in ['changed_components','added_components']:
        for ref,c in logic[category].items():
            (added if category=='added_components' else modified).add(ref)
            for no,net in c.get('pins',{}).items():expect(ref+'.'+no,net,names[1])
            for no,v in c.get('changed_pins',{}).items():expect(ref+'.'+no,v['to'],names[1])
    removed.update(r for r in logic['removed_components'] if not r.startswith('#'))
    digital={
      'U101.122':'FPGA_DONE_MCU','U101.123':'FPGA_INIT_N_MCU','R308.2':'MCU_QSPI_IO2','J301.9':'MCU_SD_CD_N','R324.2':'MCU_SD_CD_N',
      'U1302.9':'FPGA_DONE','U1302.8':'FPGA_DONE_MCU','U1302.12':'FPGA_INIT_N','U1302.11':'FPGA_INIT_N_MCU','U1302.14':'SYS3V3','C1308.1':'SYS3V3',
      'R1104.2':'USB_VBUS_DIV','R1105.2':'USB_VBUS_DIV','U1109.1':None,'U1109.2':'USB_VBUS_DIV','U1109.3':'GND','U1109.4':'FT_VBUS_DET','U1109.5':'IO3V3',
      'C1133.1':'IO3V3','C1133.2':'GND','R1115.1':'FT_VBUS_DET','R1115.2':'GND'}
    for e,n in digital.items():expect(e,n,names[2])
    added.update(['U1109','C1133','R1115'])
    for c in js[names[2]]['intentional_component_changes']:metadata_allowed.update(c['refs'])
    dac={
      'U2202.11':'BL_DAC6','U2202.6':'BL_DAC7','U1806.5':'PROG_P15','U1806.2':'PROG_N15','U3102.7':'P15','C3105.1':'P15',
      'U3102.2':'MAT_CC_FB','C3104.1':'MAT_CC_FB','U2603.11':'MAT_WRITE_PULSE','U2603.12':'MAT_CC_SENSE','U2603.13':'MAT_CC_FB','U2603.14':'MAT_CC_GATE_RAW',
      'U2604.6':'MAT_CC_GATE_RAW','U2604.8':'MAT_WRITE_PULSE','U3103.2':'MAT_WRITE_PULSE','U3103.4':'MAT_NOT_WRITE_PULSE','Q3102.1':'MAT_NOT_WRITE_PULSE'}
    for e,n in dac.items():expect(e,n,names[3])
    for change in js[names[3]].get('intentional_net_changes',[]):
        endpoint=change.get('node','');net=change.get('after','')
        if re.fullmatch(r'[A-Z]+[0-9]+\.[A-Z0-9]+',endpoint) and re.fullmatch(r'[A-Z][A-Z0-9_]*',net):expect(endpoint,net,names[3])
    # R3103.1/U2604.7 is intentionally unnamed, so test the physical pin group.
    same.append(['R3103.1','U2604.7']);modified.update(['R3103','U2604','U1806']);removed.add('U1803')
    metadata_allowed.add('C3105')
    for c in js[names[3]].get('intentional_assembly_changes',[]):dnp[c['ref']]=c['after_dnp']
    adc={
      'U2903.7':'MAT_CC_SENSE_BUF','U2903.12':'MAT_ILIM_SENSE_BUF',
      'U2904.1':'MAT_CC_SENSE_BUF','U2904.2':'MAT_CC_SENSE_BUF','U2904.3':'MAT_CC_SENSE','U2904.4':'N15','U2904.5':'MAT_ILIM_SENSE','U2904.6':'MAT_ILIM_SENSE_BUF','U2904.7':'MAT_ILIM_SENSE_BUF','U2904.8':'P15',
      'U3001.2':'MAT_REF_PRE12','U3003.2':'MAT_MONITOR_BUF','U3003.3':'MAT_MONITOR_RAW','U3003.4':'N15','U3003.6':'MAT_MONITOR_BUF','U3003.7':'P15',
      'U3004.1':'FDA_N','U3004.2':'MAT_ADC_CM','U3004.3':'ANA5','U3004.4':'FDA_OP','U3004.5':'FDA_ON','U3004.6':'GND','U3004.7':'ANA5','U3004.8':'FDA_P',
      'R3003.1':'GND','R3003.2':'FDA_P','R3004.1':'FDA_P','R3004.2':'FDA_ON','R3005.1':'MAT_MONITOR_BUF','R3005.2':'FDA_N','R3006.1':'FDA_N','R3006.2':'FDA_OP',
      'R3007.1':'FDA_OP','R3007.2':'MAT_ADC_INP','R3010.1':'FDA_ON','R3010.2':'MAT_ADC_INN','C3007.1':'MAT_ADC_INP','C3007.2':'MAT_ADC_INN','U3005.4':'MAT_ADC_INN','C3004.1':'P15',
      'U3007.1':'MAT_REF_PRE12','U3007.2':'P15','U3007.3':'GND','R3011.1':'MAT_REF_PRE12','R3011.2':'GND'}
    for ref,net in [('C2918','P15'),('C2919','N15'),('C3014','ANA5'),('C3015','N15'),('C3016','P15'),('C3017','N15'),('C3018','MAT_REF_PRE12'),('C3019','MAT_REF_PRE12')]:
        adc[ref+'.1']=net;adc[ref+'.2']='GND'
    for e,n in adc.items():expect(e,n,names[4])
    for e,n in {'J2801.40':'MAT_ADAPTER_CASE','J2801.48':'MAT_ADAPTER_VSUB','J2801.47':None,'U3204.1':'MAT_TRIP','U3204.2':'IO3V3','U3204.3':None,'U3204.4':'GND','U3204.5':'MAT_FAULT_Q','U3204.6':'MAT_FAULT_CLEAR_N','U3204.7':'IO3V3','U3204.8':'IO3V3','U2002.1':'MAT_SPI_LATCH','U2002.3':None,'U2002.4':'GND','U2002.5':'MAT_IMAGE_ARMED','U2002.6':'MAT_ALLOWED','U2002.7':'IO3V3','U2002.8':'IO3V3','U3102.3':'MAT_ILIM_SENSE','U3102.4':'GND','U3102.6':'MAT_CC_GATE_RAW','Q3101.1':'MAT_CC_GATE','Q3101.2':'MAT_CC_SENSE','Q3101.3':'MAT_WRITE_RETURN'}.items():expect(e,n,'Independent critical preserved/updated contract')
    added.update(js[names[4]]['added_refs']);removed.update(js[names[4]]['removed_refs']);metadata_allowed.update(js[names[4]]['modified_components'])
    modified.update(e.rsplit('.',1)[0] for e in pin);metadata_allowed.update(modified)
    reassignments=[]
    for item in js[names[3]].get('added_instances',[]):
        match=re.match(r'([A-Z]+[0-9]+) unit',item.get('replaces',''))
        if match:reassignments.append([match.group(1),item['ref']])
    return {'unit_reassignments':reassignments,'pins':pin,'pin_sources':why,'same_net_groups':same,'added':added,'removed':removed,'modified':modified,'metadata_allowed':metadata_allowed,'dnp':dnp,'journals':names}

def logical_name(name,reverse):
    if name is None:return None
    tail=name.rsplit('/',1)[-1]
    if tail.startswith('unconnected-'):return None
    # Automatic names are compared only for diagnostics; electrical groups use UUID identity.
    return re.sub(r'(?<![A-Za-z0-9])([A-Z]+[0-9]+)(?=[A-Z]?-|[A-Z]?\)|[^A-Za-z0-9]|$)',lambda m:reverse.get(m.group(1),m.group(1)),tail)

def pinstr(p):return p[0]+'.'+p[1]
def output_pin(p,forward):return forward.get(p[0],p[0])+'.'+p[1]

def validate(args):
    source=load_native(args.source_netlist);final=load_native(args.final_netlist)
    ss=schematic_index(args.source_project);fs=schematic_index(args.working_project)
    manifest,manifest_issues=load_refmap(args.manifest)
    exp=expectations(args.journals)
    forward,reasons,identity_issues=component_identity(source,final,ss,fs,manifest,exp['unit_reassignments']);reverse={v:k for k,v in forward.items()}
    # New components are mapped by manifest as well, even though they lack a source UUID.
    for old in exp['added']:
        new=manifest.get(old,old)
        if new in final['components'] and new not in reverse:reverse[new]=old;forward[old]=new;reasons[old]='documented added component via manifest/reference'
    def normpin(p):return reverse.get(p[0],'NEW::'+p[0]),p[1]
    fn={name:{normpin(p) for p in pins} for name,pins in final['nets'].items()}
    fp={normpin(p):n for p,n in final['pin_net'].items()}
    critical=[]
    for endpoint,want in exp['pins'].items():
        p=oldpin(endpoint);actual=logical_name(fp.get(p),reverse)
        present=forward.get(p[0],p[0]) in final['components']
        passed=present and actual==want
        critical.append({'old_pin':endpoint,'final_pin':output_pin(p,forward),'expected_net':want,'actual_net':fp.get(p),'pass':passed,'source':exp['pin_sources'][endpoint]})
    for group in exp['same_net_groups']:
        names=[fp.get(oldpin(e)) for e in group]
        critical.append({'same_net':group,'actual_nets':names,'pass':bool(names[0]) and len(set(names))==1,'source':'dac_matrix_repairs.json'})
    oldrefs=set(source['components']);final_oldrefs=set(reverse.values())
    added_actual=set(final['components'])-set(reverse)
    documented_added_present={old for old in exp['added'] if old in forward and forward[old] in final['components']}
    removed_actual=oldrefs-{old for old in oldrefs if old in forward}
    component_delta={
      'documented_added_present':sorted(documented_added_present),
      'missing_documented_added':sorted(exp['added']-documented_added_present),
      'undocumented_added':sorted(added_actual),
      'documented_removed':sorted(removed_actual & exp['removed']),
      'unexpected_removed':sorted(removed_actual-exp['removed']),
      'expected_removed_still_present':sorted(r for r in exp['removed'] if r in forward)}
    allowed={oldpin(e) for e in exp['pins']}
    allowed.update(oldpin(e) for group in exp['same_net_groups'] for e in group)
    # A nonpolar resistor pad exchange is electrically equivalent, but never silent.
    passive_swaps=[]
    for ref in oldrefs & set(forward):
        if not ref.startswith('R'):continue
        new=forward[ref];a=source['components'][ref];b=final['components'][new]
        if (a['value'],a['footprint'])!=(b['value'],b['footprint']):continue
        p1,p2=(ref,'1'),(ref,'2')
        before=[logical_name(source['pin_net'].get(p),{}) for p in (p1,p2)]
        after=[logical_name(fp.get(p),reverse) for p in (p1,p2)]
        if before[0]!=before[1] and before==after[::-1]:
            passive_swaps.append({'old_ref':ref,'final_ref':new,'before':before,'after':after});allowed.update((p1,p2))
    # Build a COMPLETE expected pin graph from source, then apply only the exact
    # documented endpoint edits. This catches an extra connection to an approved
    # net even if that net happens to retain the expected textual name.
    assigned={p:('source',name) for p,name in source['pin_net'].items() if p[0] not in exp['removed']}
    name_keys=collections.defaultdict(set)
    for name in source['nets']:
        if logical_name(name,{}) is not None:name_keys[logical_name(name,{})].add(('source',name))
    ambiguous_expected=[]
    def target(name,p):
        if name is None:return ('NC',p)
        candidates=name_keys.get(name,set())
        if len(candidates)>1:
            ambiguous_expected.append({'pin':pinstr(p),'name':name,'candidates':sorted(str(x) for x in candidates)})
        return next(iter(candidates)) if len(candidates)==1 else ('approved_named',name)
    for endpoint,want in exp['pins'].items():
        p=oldpin(endpoint);assigned[p]=target(want,p)
    for idx,group in enumerate(exp['same_net_groups']):
        for endpoint in group:assigned[oldpin(endpoint)]=('approved_same',idx)
    for item in passive_swaps:
        for no,name in zip(('1','2'),item['after']):
            p=(item['old_ref'],no);assigned[p]=target(name,p)
    # A pin absent from the source native export is expected isolated unless an
    # approved contract explicitly connects it. Baseline lib-ID conflicts remain
    # visible, rather than being silently excused by the comparison.
    for p in fp:
        if p[0] not in exp['removed']:assigned.setdefault(p,('isolated',p))
    expected_groups=collections.defaultdict(set)
    for p,key in assigned.items():expected_groups[key].add(p)
    old_pin_group={p:frozenset(ps) for ps in expected_groups.values() for p in ps}
    new_pin_group={p:frozenset(ps) for ps in fn.values() for p in ps}
    differences={};label_only=[]
    for p in set(old_pin_group)|set(new_pin_group):
        before=old_pin_group.get(p,frozenset({p}));after=new_pin_group.get(p,frozenset({p}))
        if before!=after:
            key=(before,after)
            differences[key]={'expected_pins':sorted(map(pinstr,before)),'actual_pins':sorted(map(pinstr,after)),
                              'original_source_nets':sorted({source['pin_net'].get(x,'<added/absent>') for x in before}),
                              'actual_final_nets':sorted({fp.get(x,'<absent>') for x in after})}
        elif p in source['pin_net'] and p in fp and p not in allowed:
            a=source['pin_net'][p];b=fp[p]
            if logical_name(a,{})!=logical_name(b,reverse) and not any(z in a or z in b for z in ['Net-(','unconnected-']):
                label_only.append({'pin':pinstr(p),'before':a,'after':b})
    uncovered_added_pins=[pinstr(p) for p in fp if p[0] in exp['added'] and pinstr(p) not in exp['pins']]
    metadata=[];dnp_checks=[]
    for old,new in forward.items():
        if old not in oldrefs:continue
        a=source['components'][old];b=final['components'][new]
        for key in ['value','footprint','mpn']:
            if a.get(key)!=b.get(key):metadata.append({'old_ref':old,'final_ref':new,'field':key,'before':a.get(key),'after':b.get(key),'component_documented':old in exp['metadata_allowed']})
        ad={u['dnp'] for u in ss['by_ref'].get(old,[])};bd={u['dnp'] for u in fs['by_ref'].get(new,[])}
        if ad!=bd:metadata.append({'old_ref':old,'final_ref':new,'field':'dnp','before':sorted(ad),'after':sorted(bd),'component_documented':old in exp['dnp']})
    for old,want in exp['dnp'].items():
        new=forward.get(old,manifest.get(old,old));actual={u['dnp'] for u in fs['by_ref'].get(new,[])}
        dnp_checks.append({'old_ref':old,'final_ref':new,'expected':want,'actual':sorted(actual),'pass':actual=={want}})
    # Footprint pad numbers versus all pin numbers of the selected embedded symbol.
    fp_checks=[]
    targets=exp['added']|{r for r in exp['modified'] if r.startswith('U')}|{'U1301','U1302','U1806'}
    for old in sorted(targets):
        new=forward.get(old,manifest.get(old,old));units=fs['by_ref'].get(new,[])
        if not units:fp_checks.append({'old_ref':old,'final_ref':new,'pass':False,'error':'No instantiated symbol'});continue
        footprints={u['footprint'] for u in units};pin_numbers=set().union(*(fs['symbol_pins'].get(u['lib_id'],set()) for u in units))
        if len(footprints)!=1:fp_checks.append({'old_ref':old,'final_ref':new,'pass':False,'error':'Multiple physical footprints','footprints':sorted(footprints)});continue
        footprint=next(iter(footprints));lib,name=(footprint.split(':',1) if ':' in footprint else ('',footprint))
        candidates=list(args.working_project.glob('**/'+lib+'.pretty/'+name+'.kicad_mod'))
        if len(candidates)!=1:fp_checks.append({'old_ref':old,'final_ref':new,'footprint':footprint,'pass':False,'error':'Footprint file not uniquely resolved','candidates':[str(c) for c in candidates]});continue
        tree=parse_sexp(candidates[0].read_text());pads={p[1] for p in kids(tree,'pad') if p[1]}
        fp_checks.append({'old_ref':old,'final_ref':new,'footprint':footprint,'symbol_pins':sorted(pin_numbers),'pad_numbers':sorted(pads),'missing_pads':sorted(pin_numbers-pads),'extra_pads':sorted(pads-pin_numbers),'pass':pads==pin_numbers})
    failures=[x for x in critical if not x['pass']]
    unexpected_metadata=[x for x in metadata if not x['component_documented']]
    counts={'critical_checks':len(critical),'critical_failures':len(failures),'unexpected_connection_groups':len(differences),'label_only_changes':len(label_only),'undocumented_metadata_changes':len(unexpected_metadata),'footprint_failures':sum(not x['pass'] for x in fp_checks),'DNP_failures':sum(not x['pass'] for x in dnp_checks),'identity_issues':len(identity_issues)+len(manifest_issues),'ambiguous_expected_nets':len(ambiguous_expected),'uncovered_added_pins':len(uncovered_added_pins)}
    component_fail=any(component_delta[k] for k in ['missing_documented_added','undocumented_added','unexpected_removed','expected_removed_still_present'])
    status='PASS' if not any(v for k,v in counts.items() if k not in ['critical_checks','label_only_changes']) and not component_fail else 'REVIEW_REQUIRED'
    return {'status':status,'counts':counts,'inputs':{'source_project':str(args.source_project),'working_project':str(args.working_project),'source_netlist':str(args.source_netlist),'final_netlist':str(args.final_netlist),'manifest':str(args.manifest) if args.manifest else None,'journals':exp['journals']},
      'method':'Physical identity uses stable unit UUIDs, then explicit manifest. Connection comparison uses equivalence classes of physical pins, independent of sheet paths and net names. A complete expected graph starts from source and applies exact documented endpoint edits, added pins and removed components. Any extra connection to an approved net remains detectable. Exact named-net checks provide an independent critical contract. Passive resistor pad swaps are reported separately.',
      'reference_identity':[{ 'old_ref':old,'final_ref':new,'basis':reasons[old]} for old,new in sorted(forward.items())],
      'identity_issues':identity_issues,'manifest_issues':manifest_issues,'ambiguous_expected_nets':ambiguous_expected,'uncovered_added_pins':uncovered_added_pins,'duplicate_native_pin_nodes':{'source':source['duplicates'],'final':final['duplicates']},
      'component_changes':component_delta,'critical_pin_assertions':critical,'unexpected_connection_groups':list(differences.values()),'label_only_changes':label_only,'benign_nonpolar_resistor_pad_swaps':passive_swaps,
      'metadata_changes':metadata,'DNP_assertions':dnp_checks,'footprint_pad_assertions':fp_checks,
      'limitations':['Whole-project native baseline must use the same embedded-library namespace reconciliation as final. Original lib-ID collisions can otherwise create missing-pin artifacts; those are not automatically suppressed.','Pad-number equality checks pin-to-pad identity, not footprint mechanical dimensions or PCB layout quality.','Metadata changes on a documented component remain visible for human review; component_documented is not proof of every field value.','This script verifies static connectivity, not analog settling, transient safety, HDL, firmware, or timing.']}

def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--source-project',type=Path,default=DEFAULT/'source/MIRA_Control')
    ap.add_argument('--working-project',type=Path,default=DEFAULT/'working/MIRA_Control')
    ap.add_argument('--source-netlist',type=Path,required=True)
    ap.add_argument('--final-netlist',type=Path,required=True)
    ap.add_argument('--manifest',type=Path)
    ap.add_argument('--journals',type=Path,default=DEFAULT/'patches')
    ap.add_argument('--output',type=Path,default=DEFAULT/'research/final_validation.json')
    args=ap.parse_args();result=validate(args);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'counts':result['counts'],'output':str(args.output)},ensure_ascii=False,indent=2))
    return 0 if result['status']=='PASS' else 2
if __name__=='__main__':sys.exit(main())
