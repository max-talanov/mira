"""Write per-instance audit tables, keeping absent schematic parts explicit."""
from pathlib import Path
import sys,json,csv,gzip,collections,math,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'review/layout-audit';STATE=Path('/tmp/mira-layout-audit')
sys.path.insert(0,str(ROOT/'review/schematic-layout'));from kicad_sexpr import *
boards=json.loads((STATE/'native-after.json').read_text());before=json.loads((STATE/'native-before.json').read_text());packages={(p['project'],p['footprint']):p for p in json.loads((OUT/'model-catalog.json').read_text())['packages']};checks={(p['project'],p['footprint']):p for p in json.loads((OUT/'footprint-checks.json').read_text())};modelmeta={p['model']['file']:p['model'] for p in packages.values() if p['model'].get('file')}
def inside(point,poly):
 x,y=point;odd=False
 for i,(x1,y1) in enumerate(poly):
  x2,y2=poly[i-1]
  if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1:odd=not odd
 return odd
rows=[];summary={}
for pr,board in boards.items():
 components={c.get('ref'):c for c in ET.parse(STATE/(pr+'-after.xml')).findall('components/comp')};byuuid={c.findtext('tstamps'):c for c in components.values()};matched=set();old={f['uuid']:f for f in before[pr]['footprints']};blocks={uuid(f):f for f in leaves((ROOT/pr/(pr+'.kicad_pcb')).read_text(),'footprint')};stats=collections.Counter()
 expected_groups={frozenset((p.get('ref'),p.get('pin')) for p in n.findall('node')) for n in ET.parse(STATE/(pr+'-after.xml')).findall('nets/net')}
 actual=collections.defaultdict(set)
 for f in board['footprints']:
  for pad in f['pads']:
   if pad['number'] and pad['net']:actual[pad['net']].add((f['ref'],pad['number']))
 for f in board['footprints']:
  comp=byuuid.get(f['path'].split('/')[-1]);comp=components.get(f['ref']) if comp is None else comp
  fields={quoted(x)[0]:quoted(x)[1] for x in leaves(blocks[f['uuid']],'property')};identity='matched_by_UUID_or_reference' if comp is not None else 'PCB_only';notes=[]
  if comp is not None:
   ref=comp.get('ref');matched.add(ref);sf=comp.findtext('footprint','');sv=comp.findtext('value','');attrs={x.get('name'):x.text or '' for x in comp.findall('fields/field')}
   if f['value']==sv:fields.update(attrs)
   elif f['ref']!='J10003':notes.append('PCB value '+f['value']+' differs from schematic '+sv+'; resolve CH48 ECO before replacement.');identity='value_mismatch'
   if f['footprint']!=sf:notes.append('PCB '+f['footprint']+' differs from schematic '+sf+'; confirm pin mapping and perform targeted footprint ECO.');identity='footprint_mismatch'
  else:ref='';sf='';sv='';notes.append('Resolve whether this PCB-only part is retained or obsolete in CH48 before moving/removing it.')
  placed=any(inside(f['xy'],p) for p in board['outlines']);position='placed' if placed else 'awaiting_placement';stats['pcb_positions']+=1;stats['awaiting_placement']+=not placed
  if not placed:notes.append('Place '+f['ref']+' with its current functional/parked group; group coordinates are preserved.')
  fixture=checks.get((pr,f['footprint']));fpok=bool(fixture and fixture['geometry_verified']);feature=not f['footprint'] or 'TestPoint_Pad' in f['footprint'] or 'SolderJumper' in f['footprint']
  if not f['footprint']:
   fpok=all(not p['number'] and abs(p['drill'][0]-2.2)<1e-5 for p in f['pads']);fpstatus='mechanical_hole_nominal_2p2mm'
  else:fpstatus='verified_land_geometry' if fpok else 'manufacturer_variant_review'
  if not fpok:notes.append('Check exact '+(fields.get('MPN') or f['value'])+' package drawing, pin1, land dimensions and mask/paste; see footprint-checks.json for the recorded source/gap.')
  mm=[modelmeta.get(Path(m['path']).name,{}) for m in f['models']];mverified=bool(mm) and all(m.get('verified',False) for m in mm)
  exists=all(Path(m['path'].replace('${KIPRJMOD}',str(ROOT/pr))).exists() for m in f['models'])
  if feature and not f['models']:modelstatus='no_separate_housing'
  elif mverified:modelstatus='verified_standard_or_dimensioned_package'
  elif f['models']:modelstatus='simplified_or_provisional'
  else:modelstatus='missing'
  if modelstatus=='simplified_or_provisional':notes.append('Confirm '+f['ref']+' exact body/height/contacts using manufacturer STEP or drawing; assigned '+','.join(Path(m['path']).name for m in f['models'])+' is explicitly simplified/provisional.')
  if not fields.get('MPN') and not feature:notes.append('Provide full orderable MPN for '+f['ref']+' ('+f['value']+') to qualify the exact package/height variant; geometry check alone is not procurement approval.')
  pinsets=[frozenset(actual[p['net']]) for p in f['pads'] if p['number'] and p['net']];pinmap='matches_complete_schematic_pin_groups' if comp is not None and all(x in expected_groups for x in pinsets) else 'baseline_ECO_or_schematic_link_review'
  if pinmap!='matches_complete_schematic_pin_groups' and not feature:notes.append('Reconcile the listed PCB/schematic pin groups; no pin or pad number was changed by this 3D task.')
  stats['verified_footprints']+=fpok;stats['verified_3d']+=mverified;stats['model_assigned']+=bool(f['models']);stats['pcb_features']+=feature;stats['pcb_only']+=comp is None;stats['dnp']+=f['dnp']
  src='; '.join(fixture['sources']) if fixture else 'Nominal stack/mechanical intent';quality='; '.join(m.get('kind','provisional_hardware') for m in mm)
  rows.append(dict(project=pr,reference=f['ref'],original_reference=old[f['uuid']]['ref'],presence=identity,schematic_reference=ref,value=f['value'],MPN=fields.get('MPN',''),schematic_value=sv,footprint=f['footprint'],schematic_footprint=sf,footprint_status=fpstatus,footprint_verified=fpok,library_pad_geometry_matches=old[f['uuid']].get('library_geometry_match',True),pin_mapping_status=pinmap,placement_status=position,side=f['side'],rotation_deg=f['angle'],x_mm=f['xy'][0],y_mm=f['xy'][1],DNP=f['dnp'],excluded_BOM=f['excluded_bom'],model_status=modelstatus,model_verified=mverified,model_paths='; '.join(m['path'] for m in f['models']),model_paths_resolve=exists,model_quality=quality,model_source='; '.join(m.get('source','Nominal unselected hardware') for m in mm),footprint_source=src,footprint_uuid=f['uuid'],next_action=' '.join(notes)))
 for ref in sorted(components.keys()-matched):
  c=components[ref];fields={x.get('name'):x.text or '' for x in c.findall('fields/field')};fid=c.findtext('footprint','');pc=packages.get((pr,fid));fixture=checks.get((pr,fid));model=pc['model'] if pc else {};dnp=any(x.get('name')=='dnp' for x in c.findall('property'));stats['schematic_only']+=1
  action='Transfer '+ref+' into the PCB during the CH48 ECO and place with its functional group; do not scatter it as a separate ungrouped part.'
  if pr=='MIRA_Crossbar' and ref=='U10001':action='Resolve U10001 versus trial J10003: reuse one socket footprint/UUID and transfer the approved 64-pin map; do not create a second socket body.'
  rows.append(dict(project=pr,reference=ref,original_reference=ref,presence='schematic_only',schematic_reference=ref,value=c.findtext('value',''),MPN=fields.get('MPN',''),schematic_value=c.findtext('value',''),footprint=fid,schematic_footprint=fid,footprint_status='library_only_'+('verified_land_geometry' if fixture and fixture['geometry_verified'] else 'manufacturer_variant_review'),footprint_verified=False,library_pad_geometry_matches='',pin_mapping_status='no_PCB_instance',placement_status='not_on_PCB',side='',rotation_deg='',x_mm='',y_mm='',DNP=dnp,excluded_BOM=False,model_status='library_ready' if model.get('file') else 'no_PCB_instance',model_verified=False,model_paths='${KIPRJMOD}/../libraries/3d/'+model['file'] if model.get('file') else '',model_paths_resolve=bool(model.get('file')),model_quality=model.get('kind',''),model_source=model.get('source',''),footprint_source='; '.join(fixture['sources']) if fixture else '',footprint_uuid='',next_action=action))
 stats['inventory_rows']=stats['pcb_positions']+stats['schematic_only'];stats['awaiting_total']=stats['awaiting_placement']+stats['schematic_only'];summary[pr]=dict(stats)
for name,subset in [('components.csv',rows),('pcb-components.csv',[r for r in rows if r['presence']!='schematic_only']),('schematic-only.csv',[r for r in rows if r['presence']=='schematic_only']),('open-questions.csv',[r for r in rows if r['next_action']])]:
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(subset)
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for label,obj,folder in [('native-before',before,'baseline'),('native-after',boards,'checks')]:
 (OUT/folder/(label+'.json.gz')).write_bytes(gzip.compress(json.dumps(obj,separators=(',',':')).encode(),mtime=0))
print(json.dumps(summary,indent=2))
