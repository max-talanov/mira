"""Available KiCad checks in isolated copies; preserve all working .pro user preferences."""
import sys,shutil,subprocess,concurrent.futures,json,collections
from pathlib import Path
from trial_spec import *
CLI=sys.argv[1]
def run(task):
 n,stage=task;src=BASE/f'MIRA_{n}';dst=Path('/tmp/mira-socket-trial-checks')/stage/f'MIRA_{n}';dst.mkdir(parents=True,exist_ok=True)
 for f in src.iterdir():
  if f.is_file():
   b=OUT/'before'/f.name
   shutil.copy2(b if stage=='before' and b.exists() else f,dst/f.name)
 if not (dst/'libraries').exists():(dst/'libraries').symlink_to(src/'libraries',target_is_directory=True)
 commands=[('drc',[CLI,'pcb','drc','--format','json','-o',str(OUT/f'{n}-{stage}-drc.json'),str(dst/f'MIRA_{n}.kicad_pcb')])]
 if n!='Power':
  commands += [('erc',[CLI,'sch','erc','--format','json','-o',str(OUT/f'{n}-{stage}-erc.json'),str(dst/f'MIRA_{n}.kicad_sch')])]
  if stage=='after':commands += [('netlist',[CLI,'sch','export','netlist','--format','kicadxml','-o',str(OUT/('control.xml' if n=='Control' else 'module.xml')),str(dst/f'MIRA_{n}.kicad_sch')])]
 for tag,cmd in commands:
  r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,(cmd,r.stderr);print(n,stage,tag,r.stdout.strip(),flush=True)
if __name__=='__main__':
 all_tasks=[(n,stage) for n in ['Control','Crossbar','Power'] for stage in ['before','after']]
 tasks=[t for t in all_tasks if t[1]=='after'] if '--after-only' in sys.argv else all_tasks
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:list(e.map(run,tasks))
 summary={}
 for n,stage in all_tasks:
  d=json.loads((OUT/f'{n}-{stage}-drc.json').read_text());summary[n+'-'+stage]={'drc':dict(collections.Counter(v['type'] for v in d['violations'])),'unconnected_reported':len(d['unconnected_items']),'ignored':d['ignored_checks']}
  if n!='Power':
   d=json.loads((OUT/f'{n}-{stage}-erc.json').read_text());summary[n+'-'+stage]['erc']=dict(collections.Counter(v['type'] for s in d['sheets'] for v in s['violations']))
 (OUT/'checks-summary.json').write_text(json.dumps(summary,indent=2))
