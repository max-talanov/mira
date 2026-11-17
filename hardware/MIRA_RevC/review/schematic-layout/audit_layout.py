"""Validate native page numbers, physical package identity and PCB preservation.

Use --baseline with the three pre-edit project directories and --reference-map
with the mapping from that baseline's references to the current drawing.
"""
import argparse,json,re,collections,hashlib
from pathlib import Path
from kicad_sexpr import child,children,leaves,kind,quoted,prop,uuid,walk

def canonical(s):
 # Whitespace outside strings is insignificant; preserve every numeric token and string.
 return re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]',s)
def board_normalize(s):
 for f in leaves(s,'footprint'):
  nf=f;pp=next((x for x in leaves(f,'property') if quoted(x)[0]=='Reference'),None)
  if pp:nf=nf.replace(pp,pp.replace('"'+quoted(pp)[1]+'"','"REFERENCE"',1))
  else:
   pp=next((x for x in leaves(f,'fp_text') if re.match(r'\(fp_text\s+reference\b',x)),None)
   if pp:nf=nf.replace(pp,pp.replace('"'+quoted(pp)[0]+'"','"REFERENCE"',1))
  p=child(nf,'path')
  if p:nf=nf.replace(p,'(path "SCHEMATIC_PATH")')
  s=s.replace(f,nf,1)
 return canonical(s)
def check(root,baseline,maps):
 result={};pages=json.loads((root/'review/schematic-layout/pages.json').read_text())
 for pr in maps:
  project=root/pr;original=baseline/pr;mapping=maps[pr];tree=walk(project/(pr+'.kicad_sch'));before={};after={};first={};paths={}
  for p in original.glob('*.kicad_sch'):
   for z in leaves(p.read_text(),'symbol'):before[uuid(z)]=z
  for e in tree:
   for z in leaves(e['text'],'symbol'):
    u=uuid(z);assert u not in after,(pr,'duplicate UUID',u);after[u]=z;r=prop(z,'Reference');first.setdefault(r,int(next(p['page'] for p in pages[pr] if p['path']==e['path'])));paths[u]=e['path']+'/'+u
  assert before.keys()<=after.keys(),(pr,'lost symbol UUIDs',before.keys()-after.keys())
  for uid,z in before.items():
   nz=after[uid];assert prop(nz,'Reference')==mapping.get(prop(z,'Reference'),prop(z,'Reference')),(pr,'reference',uid)
   for field in ['Value','Footprint','MPN','Manufacturer','Datasheet']:assert prop(z,field)==prop(nz,field),(pr,prop(z,'Reference'),field)
   for field in ['in_bom','on_board','dnp']:assert child(z,field)==child(nz,field),(pr,prop(z,'Reference'),field)
  for r,page in first.items():
   assert re.fullmatch(r'[^\d]+'+str(page)+r'\d{2}',r),(pr,'reference/page',r,page)
  packages={}
  multi={'OPA4192','OPA4323','MAX313','TMUX6112','TLV3202'}
  for e in tree:
   libs={quoted(x)[0]:x for x in leaves(child(e['text'],'lib_symbols'),'symbol')} if child(e['text'],'lib_symbols') else {}
   for z in leaves(e['text'],'symbol'):
    lid=quoted(child(z,'lib_id'))[0]
    if not lid.startswith('MIRA_Readable:') or lid.split(':')[-1] not in multi:continue
    r=prop(z,'Reference');unit=int(re.search(r'\d+',child(z,'unit'))[0]);lib=libs[lid];parts=leaves(lib,'symbol');expected_units={int(quoted(u)[0].split('_')[-2]) for u in parts};physical={quoted(child(p,'number'))[0] for u in parts for p in leaves(u,'pin')}
    entry=packages.setdefault(r,{'units':[],'pins':collections.Counter(),'expected':expected_units,'physical':physical,'footprint':prop(z,'Footprint'),'value':prop(z,'Value')});entry['units'].append(unit)
    assert entry['footprint']==prop(z,'Footprint') and entry['value']==prop(z,'Value'),(pr,r,'inconsistent package units')
    for u in parts:
     if int(quoted(u)[0].split('_')[-2])==unit:
      entry['pins'].update(quoted(child(p,'number'))[0] for p in leaves(u,'pin'))
  for r,pkg in packages.items():
   assert set(pkg['units'])==pkg['expected'] and len(pkg['units'])==len(pkg['expected']),(pr,r,'missing/duplicate units')
   assert set(pkg['pins'])==pkg['physical'] and all(v==1 for v in pkg['pins'].values()),(pr,r,'missing/duplicate physical pin')
  expected=list(range(100,(len(tree)+1)*100,100));assert [p['page'] for p in pages[pr]]==expected
  assert re.search(r'\(page "100"\)',child(tree[0]['text'],'sheet_instances'))
  for e,p in zip(tree,pages[pr]):
   assert str(e['file'].relative_to(root))==p['file'];assert e['path']==p['path']
   if e['depth']:assert int(e['page'])==p['page']
  b=original/(pr+'.kicad_pcb');a=project/(pr+'.kicad_pcb');assert board_normalize(b.read_text())==board_normalize(a.read_text()),(pr,'PCB geometry/net/model changed')
  # Every previously linked footprint remains linked to the same symbol UUID at its new hierarchy path.
  for f in leaves(a.read_text(),'footprint'):
   path=child(f,'path')
   if path:
    p=quoted(path)[0];uid=p.split('/')[-1]
    if uid in before:assert p==paths[uid],(pr,'PCB link',uid,p,paths[uid])
  assert (original/(pr+'.kicad_pro')).read_bytes()==(project/(pr+'.kicad_pro')).read_bytes(),(pr,'ERC/project settings changed')
  result[pr]={'result':'PASS','pages':len(tree),'original_symbol_instances':len(before),'final_symbol_instances':len(after),'multi_unit_packages_verified':len(packages),'original_UUIDs_preserved':True,'values_MPN_footprints_population_preserved':True,'PCB_geometry_pads_nets_routes_models_preserved':True,'PCB_changes':'reference text / schematic path only','project_preferences_and_ERC_rules':'unchanged'}
 return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--reference-map',type=Path,default=Path(__file__).with_name('readability-reference-map.json'));a=p.parse_args();print(json.dumps(check(a.root,a.baseline,json.loads(a.reference_map.read_text())),indent=2))
if __name__=='__main__':main()
