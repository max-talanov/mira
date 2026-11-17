"""Compare physical pin partitions and per-component attributes across drawing/annotation changes."""
import argparse,json,gzip,xml.etree.ElementTree as E
from pathlib import Path

def load(path,aliases):
 with (gzip.open(path,'rb') if path.suffix=='.gz' else path.open('rb')) as f:root=E.parse(f)
 defs={(p.get('lib'),p.get('part')):sorted(tuple(sorted(n.attrib.items())) for n in p.findall('pins/pin')) for p in root.findall('libparts/libpart')}
 components={}
 for c in root.findall('components/comp'):
  r=aliases.get(c.get('ref'),c.get('ref'));lib=c.find('libsource');assert r not in components
  components[r]={'value':c.findtext('value'),'footprint':c.findtext('footprint'),'datasheet':c.findtext('datasheet'),'MPN':next((f.text or '' for f in c.findall('fields/field') if f.get('name')=='MPN'),''),'Manufacturer':next((f.text or '' for f in c.findall('fields/field') if f.get('name')=='Manufacturer'),''),'population':sorted(tuple(sorted(x.attrib.items())) for x in c.findall('property') if x.get('name') in ['dnp','exclude_from_bom','exclude_from_board']),'physical_pins':defs[lib.get('lib'),lib.get('part')]}
 groups={};pins=set()
 for net in root.findall('nets/net'):
  group=frozenset((aliases.get(n.get('ref'),n.get('ref')),n.get('pin')) for n in net.findall('node'));assert not group & pins; pins|=group;groups[group]=net.get('name')
 return components,groups,pins

def netclasses(path,aliases):
 with (gzip.open(path,'rb') if path.suffix=='.gz' else path.open('rb')) as f:root=E.parse(f)
 return {frozenset((aliases.get(n.get('ref'),n.get('ref')),n.get('pin')) for n in net.findall('node')):net.get('class','Default') for net in root.findall('nets/net')}

def compare(pr,before,after,mapping):
 aliases={v:k for k,v in mapping.items()};assert len(aliases)==len(mapping)
 a,an,ap=load(before,{});b,bn,bp=load(after,aliases)
 assert netclasses(before,{})==netclasses(after,aliases), 'effective net classes changed'
 changed=[r for r in a.keys()|b.keys() if a.get(r)!=b.get(r)];assert not changed,('component attributes / physical pin definitions',changed[:20],[(r,a.get(r),b.get(r)) for r in changed[:1]])
 assert ap==bp,('pin identities',sorted(ap-bp)[:20], sorted(bp-ap)[:20]);assert an.keys()==bn.keys(),('net partition difference',len(an.keys()-bn.keys()),len(bn.keys()-an.keys()))
 # All externally meaningful, non-hierarchical names retain the same complete physical pin set.
 external={name:g for g,name in an.items() if not name.startswith(('/', 'Net-','unconnected-'))}
 named_after={name:g for g,name in bn.items()}
 # An internal global label may become a local label. Its suffix and partition must still identify it.
 lost=[]
 for name,g in external.items():
  newname=bn[g]
  if newname!=name and not newname.endswith('/'+name):lost.append((name,newname))
 assert not lost,('meaningful net names',lost[:30])
 return dict(project=pr,components=len(a),pins=len(ap),nets=len(an),result='PASS',component_values_MPN_footprints_population_and_physical_pin_definitions='unchanged',electrical_partitions='identical_with_reference_map',meaningful_names='preserved_or_localized_with_same_suffix',effective_net_classes='unchanged')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('project');p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--reference-map',type=Path,default=Path(__file__).with_name('reference-map.json'));a=p.parse_args();print(json.dumps(compare(a.project,a.before,a.after,json.loads(a.reference_map.read_text())[a.project]),indent=2))
if __name__=='__main__':main()
