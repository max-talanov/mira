"""ERC and fresh XML exports from complete isolated copies of the CURRENT projects."""
import shutil,subprocess,concurrent.futures,sys,json
from pathlib import Path
from interface_spec import BASE,OUT
cli=sys.argv[1]
def run(n):
 src=BASE/f'MIRA_{n}';dst=Path('/tmp/mira-fx23-after')/f'MIRA_{n}';dst.mkdir(parents=True,exist_ok=True)
 for f in src.iterdir():
  if f.is_file():shutil.copy2(f,dst/f.name)
 if not (dst/'libraries').exists():(dst/'libraries').symlink_to(src/'libraries',target_is_directory=True)
 export=OUT/'netlists'/('control.xml' if n=='Control' else 'module.xml')
 cmds=[['sch','export','netlist','--format','kicadxml','-o',str(export),str(dst/f'MIRA_{n}.kicad_sch')],['sch','erc','--format','json','-o',str(OUT/f'{n}-after-erc.json'),str(dst/f'MIRA_{n}.kicad_sch')]]
 for args in cmds:
  r=subprocess.run([cli]+args,capture_output=True,text=True);assert r.returncode==0,(args,r.stderr);print(r.stdout.strip())
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:list(e.map(run,['Control','Crossbar']))
