"""Collect portable STEP assets and build explicitly simplified package models.

Requires CadQuery 2.8. KiCad footprint geometry is read, never regenerated here.
"""
from pathlib import Path
import sys,json,re,hashlib,shutil,math
import cadquery as cq
ROOT=Path(__file__).resolve().parents[3]
REPO=ROOT.parents[1]
sys.path.insert(0,str(ROOT/'review/schematic-layout'))
from kicad_sexpr import children,child,leaves,kind,quoted,prop
STATE=Path('/tmp/mira-layout-audit');DEST=ROOT/'libraries/3d';DEST.mkdir(parents=True,exist_ok=True)
STD=Path(sys.argv[1]) if len(sys.argv)>1 else STATE/'squashfs-root/share/kicad/3dmodels'
catalog=json.loads((STATE/'library-before.json').read_text());native=json.loads((STATE/'native-before.json').read_text());records=[];cache={}
BLACK=cq.Color(.09,.1,.12);METAL=cq.Color(.67,.69,.72);GOLD=cq.Color(.78,.58,.16)
def box(x,y,z,sx,sy,sz):return cq.Workplane('XY').box(sx,sy,sz).translate((x,y,z)).val()
def save(assembly,name,meta):
 p=DEST/(name+'.step');assembly.export(str(p));shape=cq.Compound.makeCompound([v for v in cq.importers.importStep(str(p)).vals() if v.Faces()]);bb=shape.BoundingBox();assert shape.isValid(),name
 meta.update(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bounds_mm=[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax],solid_count=len(shape.Solids()),valid=True)
 return meta

def contacts(a,pads,z=.06,height=.12):
 seen=set()
 for pad in pads:
  if not pad['number']:continue
  x,y=pad['xy'];key=(pad['number'],x,y)
  if key in seen:continue
  seen.add(key);sx,sy=pad['size'];sx=min(sx,.6);sy=min(sy,.6)
  a.add(box(x,-y,z,max(.08,sx*.7),max(.08,sy*.7),height),name='terminal_'+str(len(seen)),color=METAL)

def dim_package(name,entry,body,source,quality='dimensioned_simplified',center=(0,0),stand=.08):
 sx,sy,h=body;x,y=center;a=cq.Assembly(name=name);a.add(box(x,-y,stand+(h-stand)/2,sx,sy,h-stand),name='body',color=BLACK);contacts(a,entry['pads'])
 first=next((p for p in entry['pads'] if p['number'] in ['1','A1']),None)
 if first:
  px,py=first['xy'];px=max(x-sx/2+.15,min(x+sx/2-.15,px));py=max(y-sy/2+.15,min(y+sy/2-.15,py))
  marker=cq.Workplane('XY').circle(min(.3,sx/10,sy/10)).extrude(.015).translate((px,-py,h-.015)).val();a.add(marker,name='pin1_marker',color=GOLD)
 return save(a,name,dict(kind=quality,source=source,body_mm=body,center_xy_mm=list(center),terminal_geometry='Illustrative metal at documented footprint contact centers; not a tolerance model.',verified=False))

def bga(name,entry,size,height,ball,stand,source):
 a=cq.Assembly(name=name);a.add(box(0,0,(height+stand)/2,size,size,height-stand),name='body',color=BLACK)
 for pad in entry['pads']:
  x,y=pad['xy'];a.add(cq.Workplane('XY').sphere(ball/2).translate((x,-y,ball/2)).val(),name='ball_'+pad['number'],color=METAL)
 corner=min(entry['pads'],key=lambda p:sum(p['xy']));x,y=corner['xy'];a.add(box(x,-y,height-.01,.45,.45,.02),name='A1_mark',color=GOLD)
 return save(a,name,dict(kind='dimensioned_simplified',source=source,body_mm=[size,size,height],terminal_geometry=f'{len(entry["pads"])} balls at exact named grid centers; nominal ball diameter {ball} mm.',verified=True))

def wrl(source):
 key=str(source.resolve())
 if key in cache:return cache[key]
 text=source.read_text();a=cq.Assembly(name=source.stem)
 # Existing MIRA VRML models use explicit per-box transforms in 0.1 inch units.
 matches=re.findall(r'Transform\s*\{\s*translation\s+([-\d.eE]+)\s+([-\d.eE]+)\s+([-\d.eE]+).*?geometry\s+Box\s*\{\s*size\s+([-\d.eE]+)\s+([-\d.eE]+)\s+([-\d.eE]+)',text,re.S)
 assert matches,source
 for i,m in enumerate(matches):
  x,y,z,sx,sy,sz=[float(v)*2.54 for v in m];a.add(box(x,y,z,sx,sy,sz),name='envelope_'+str(i),color=BLACK if i==0 else GOLD)
 name=source.stem+'_converted';meta=save(a,name,dict(kind='existing_envelope_converted',source=str(source.relative_to(REPO)),original_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),verified=False,terminal_geometry='Existing approximate VRML geometry preserved, conversion is not manufacturer verification.'))
 cache[key]=meta;return meta

def copy_step(source,source_hint=''):
 key=str(source.resolve())
 if key in cache:return cache[key]
 sha=hashlib.sha256(source.read_bytes()).hexdigest();name=source.stem
 if (DEST/source.name).exists() and hashlib.sha256((DEST/source.name).read_bytes()).hexdigest()!=sha:name+='_'+sha[:8]
 p=DEST/(name+'.step');shutil.copy2(source,p)
 shape=cq.Compound.makeCompound([v for v in cq.importers.importStep(str(p)).vals() if v.Faces()]);b=shape.BoundingBox()
 quality='provisional_existing' if any(t in source.stem.lower() for t in ['approx','envelope','usermodel','drawing_model']) else 'standard_package'
 meta=dict(file=p.name,sha256=sha,source=source_hint or (str(source.relative_to(REPO)) if source.is_relative_to(REPO) else 'KiCad 10.0.5 bundled kicad-packages3D/'+str(source.relative_to(STD))),kind=quality,verified=quality=='standard_package',bounds_mm=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],solid_count=len(shape.Solids()),valid=shape.isValid())
 assert meta['valid'],source
 cache[key]=meta;return meta

# Missing or unresolved custom packages. Every estimate is explicit in the manifest.
special={
 'FCA169_10x10_P0.75_review':lambda e:bga('Infineon_FCA169_10x10_0p75_simplified',e,10,1.2,.3,.2,'sources/Infineon-FX20.pdf p82, drawing 002-32511 C'),
 'Xilinx_CLG484_CLG485':lambda e:bga('AMD_CLG484_19x19_0p8_simplified',e,19,1.47,.5,.4,'sources/AMD-UG865.pdf, CLG484 figure 4-3; nominal height 1.47, max 1.60 mm'),
 'RHA0040C_DAC81416':lambda e:dim_package('TI_RHA0040C_simplified',e,[6,6,1.0],'sources/TI-DAC81416.pdf, RHA0040C 4219053/B'),
 'TI_DMX0003A':lambda e:dim_package('TI_DMX0003A_simplified',e,[.6,1,.4],'sources/TI-ESD122.pdf, DMX0003A 4223338/A',stand=.01),
 'ECS_ECX-2236':lambda e:dim_package('ECS_ECX2236_simplified',e,[2.5,2,.55],'sources/ECS-ECX2236.pdf, package drawing and Fig.2'),
 'SO6_4Pin_Toshiba_11-4M1S':lambda e:dim_package('Toshiba_11_4M1S_simplified',e,[3.7,4.55,2.2],'https://toshiba.semicon-storage.com/info/TLP172GM_datasheet_en_20230525.pdf?did=36716&prodName=TLP172GM, 11-4M1S Rev11 p10'),
 'TI_DDA0008B':lambda e:dim_package('TI_DDA0008B_simplified',e,[3.9,4.9,1.7],'sources/TI-LMR36520.pdf, DDA0008B package drawing'),
 'WSON-8_2x2mm_P0.5mm_EP0.9x1.6mm':lambda e:dim_package('TI_DSG0008A_simplified',e,[2,2,.8],'sources/TI-TMUX2821.pdf, DSG0008A 4218900/E'),
 'Texas_RTE0016D_WQFN-16-1EP_3x3mm_P0.5mm_EP0.8x0.8mm':lambda e:dim_package('TI_RTE0016D_simplified',e,[3,3,.8],'sources/TI-DAC80508.pdf, RTE0016D 4219118/A'),
 'Texas_DGN0008D_VSSOP-8-1EP_3x3mm_P0.65mm_EP2x2.94mm_Mask1.57x1.89mm':lambda e:dim_package('TI_DGN0008D_simplified',e,[3,3,1.1],'TI TPS7A4901 datasheet DGN0008D drawing; land pattern already documented in local footprint'),
 'LFCSP-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm':lambda e:dim_package('ADI_CP32_7_simplified',e,[5,5,.75],'AD4696 datasheet CP-32-7; verify thermal pad/process against exact ordering code'),
}

def cincon(e):
 a=cq.Assembly(name='Cincon_ECB40W18_no_bus');a.add(box(7.62,-22.86,6.35,25.4,50.8,12.7),name='body',color=BLACK)
 for pad in e['pads']:
  if not pad['number']:continue
  x,y=pad['xy'];a.add(cq.Workplane('XY').circle(.5).extrude(4.8).translate((x,-y,-4.8)).val(),name='pin_'+pad['number'],color=GOLD)
 return save(a,'Cincon_ECB40W18_no_bus_simplified',dict(kind='dimensioned_simplified',source='sources/Cincon-ECB40W18.pdf p10, no-bus bottom view; six pins only',verified=True,body_mm=[25.4,50.8,12.7],height_tolerance_mm=.5,terminal_geometry='1.0 mm nominal round pins, length 4.8; footprint top-side view, bottom drawing rotated and reflected explicitly.'))
special['Cincon_ECB40W18_no_bus']=cincon

def hirose(e):
 is_s='80S' in e['footprint'];sx,sy,h=(36,10.5,5.8) if is_s else (33.7,6.6,6.85)
 return dim_package('Hirose_FX23L_80'+('S_SV' if is_s else 'P_SV8')+'_ENVELOPE',e,[sx,sy,h],'../layout/sources/'+('FX23L-80S-0.5SV_CL05732304700_2d.pdf' if is_s else 'FX23L-80P-0.5SV8_CL05732004300_2d.pdf')+'; manufacturer STEP URL recorded, download returned HTTP403',quality='dimensioned_connector_envelope',stand=.25)
special['Hirose_FX23L-80S-0.5SV']=hirose;special['Hirose_FX23L-80P-0.5SV8']=hirose

def ftsh(e):
 # All ten pins, including pin 7, are present. Exact -K shroud cannot be inferred from generic FTSH.
 return dim_package('Samtec_FTSH105_K_ENVELOPE',e,[7.62,5.08,5.56],'sources/Samtec-FTSH-body.pdf; nominal header + 3.05 mm mating post. Exact -K shroud envelope needs approved manufacturer STEP.',quality='provisional_connector_envelope',stand=.15)
special['Samtec_FTSH-105-01-L-DV-K_2x05_P1.27mm_SMD']=ftsh

for entry in catalog:
 pr=entry['project'];name=entry['footprint'].split(':')[1];s=(STATE/'original'/entry['file']).read_text();old=leaves(s,'model');meta=None;transform=None
 if name.startswith('TestPoint_Pad_') or name.startswith('SolderJumper-'):
  meta=dict(kind='pcb_copper_feature',verified=False,file=None,source='No purchased physical housing; board copper represents this feature.')
 elif name in special:
  if name not in cache:cache[name]=special[name](entry)
  meta=cache[name];transform=dict(offset=[0,0,0],scale=[1,1,1],rotation=[0,0,0])
 elif old:
  path=quoted(old[0])[0];source=Path(path.replace('${KIPRJMOD}',str(ROOT/pr)).replace('${KICAD10_3DMODEL_DIR}',str(STD)))
  if not source.exists():raise FileNotFoundError((entry['footprint'],source))
  meta=wrl(source) if source.suffix.lower()=='.wrl' else copy_step(source)
  def vector(tag):
   x=child(old[0],tag);return [float(z) for z in re.findall(r'[-\d.]+',child(x,'xyz'))] if x else None
  transform=dict(offset=vector('offset') or [0,0,0],scale=vector('scale') or [1,1,1],rotation=vector('rotate') or [0,0,0])
 else:raise ValueError('Unclassified housing '+entry['footprint'])
 records.append(dict(project=pr,footprint=entry['footprint'],library=entry['file'],model=meta,transform=transform))
 print(pr,name,meta['kind'],flush=True)
# Mechanical models attach to existing footprint features only, with provisional procurement status.
for name,height,outer,inner in [('M2_SPACER_8mm_PROVISIONAL',8,4,2.2),('KEY_D2_14mm_PROVISIONAL',14,2,0),('M2_SCREW_HEAD_PROVISIONAL',2,3.8,0)]:
 a=cq.Assembly(name=name);wp=cq.Workplane('XY').circle(outer/2)
 if inner:wp=wp.circle(inner/2)
 a.add(wp.extrude(height).val(),name='body',color=METAL);cache[name]=save(a,name,dict(kind='provisional_hardware',source='Nominal stack intent only; exact fastener/pin MPN, holder and tolerances are not selected.',verified=False))
(STATE/'model-assignments.json').write_text(json.dumps(records,indent=2)+'\n');(ROOT/'review/layout-audit/model-catalog.json').write_text(json.dumps(dict(packages=records,hardware={n:v for n,v in cache.items() if isinstance(n,str) and 'PROVISIONAL' in n}),indent=2)+'\n')
print('Complete packages',len(records),flush=True)
