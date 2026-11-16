"""Run before/after DRC in isolated projects with identical original settings."""
from pathlib import Path
import subprocess,concurrent.futures,json,collections,shutil,sys
P=Path(__file__).resolve().parent;root=P.parents[3];base=root/'hardware/MIRA_RevC';sha='439da953af8e23b70ae902847f65b4afd8eb2a95'
cli=sys.argv[1]
def run(n,stage):
 work=Path('/tmp/mira-fx23-drc')/stage/f'MIRA_{n}';work.mkdir(parents=True,exist_ok=True)
 source=base/f'MIRA_{n}'
 if not (work/'libraries').exists():(work/'libraries').symlink_to(source/'libraries',target_is_directory=True)
 if (source/'fp-lib-table').exists():shutil.copy2(source/'fp-lib-table',work/'fp-lib-table')
 for f in source.iterdir():
  if f.suffix in ['.kicad_pro','.kicad_dru','.kicad_pcb']:
   data=((P/'day1'/f.name).read_bytes() if (P/'day1'/f.name).exists() else f.read_bytes()) if stage=='before' else f.read_bytes()
   (work/f.name).write_bytes(data)
 report=P/f'{n}-{stage}-drc.json'
 res=subprocess.run([cli,'pcb','drc','--format','json','-o',str(report),str(work/f'MIRA_{n}.kicad_pcb')],capture_output=True,text=True)
 if res.returncode:raise RuntimeError(res.stderr)
 return n,stage,res.stdout
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for r in pool.map(lambda t:run(*t),[(n,s) for n in ['Control','Power','Crossbar'] for s in ['before','after']]):print(r)
summary={}
for n in ['Control','Power','Crossbar']:
 summary[n]={}
 for stage in ['before','after']:
  d=json.loads((P/f'{n}-{stage}-drc.json').read_text());summary[n][stage]={'violations_by_type':dict(collections.Counter(v['type'] for v in d['violations'])),'reported_unconnected':len(d['unconnected_items']),'ignored_checks':d['ignored_checks']}
 assert summary[n]['before']['ignored_checks']==summary[n]['after']['ignored_checks']
(P/'drc-summary.json').write_text(json.dumps(summary,indent=2))
