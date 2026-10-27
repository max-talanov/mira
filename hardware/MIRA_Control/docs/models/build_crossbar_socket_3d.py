"""Illustrative socket model. Exact XY contact/NPTH layout; estimated casing/Z."""
from pathlib import Path
import json,re,math
import cadquery as cq

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'libraries/MIRA_RevA.3dshapes'
OUT.mkdir(exist_ok=True)
NAME='ICS-CQFP64-1830-1830-100-1'
FP=ROOT/'libraries/MIRA_RevA.pretty'/f'{NAME}.kicad_mod'
text=FP.read_text()
contacts=[]
for p,x,y in re.findall(r'\(pad "(\d+)" smd circle \(at ([-.\d]+) ([-.\d]+)\)',text):
    contacts.append((int(p),float(x),-float(y)))
assert len(contacts)==64
# KiCad footprint +Y is down in plan view; STEP uses ordinary right-handed XY.
mounts=[(x,y,2.1) for x in (-17,17) for y in (-19,19)]
locators=[(-17,-12,2.0),(17,12,1.5)]
allholes=mounts+locators

def rounded(w,l,h,r,z=0):
    return cq.Workplane('XY').box(w,l,h,centered=(True,True,False)).edges('|Z').fillet(r).translate((0,0,z))

def cylinder(x,y,z,r,h):
    return cq.Workplane('XY').center(x,y).circle(r).extrude(h).translate((0,0,z))

def pierced(shape,holes,z=-1,depth=20):
    for x,y,d in holes:shape=shape.cut(cylinder(x,y,z,d/2,depth))
    return shape

GOLD=cq.Color(0.72,0.57,0.31)
LIDGOLD=cq.Color(0.80,0.68,0.43)
CREAM=cq.Color(0.89,0.87,0.78)
SILVER=cq.Color(0.64,0.66,0.67)
DARK=cq.Color(0.10,0.10,0.105)

# All dimensions in Z, opening sizes and latch details are estimates from photos.
base=rounded(40,50,1.5,2,0.5)
base=base.cut(rounded(24,24,4,0.6,-1))
base=pierced(base,allholes)
frame=rounded(40,50,7.5,2,2)
frame=frame.cut(rounded(31,35,12,1.5,0))
frame=pierced(frame,allholes)
for x,y,d in mounts:frame=frame.cut(cylinder(x,y,7.3,1.9,4))

guide=rounded(30.6,34.6,2.8,1.2,2)
guide=guide.cut(rounded(18.6,18.6,1.8,0.4,3.2))
for p,x,y in contacts:guide=guide.cut(cylinder(x,y,1.5,0.29,5))

pins=[]
for p,x,y in contacts:
    rod=cylinder(x,y,0,0.16,5.0)
    foot=cylinder(x,y,0,0.23,0.22)
    tip=cylinder(x,y,4.9,0.23,0.25)
    pins.append(rod.union(foot).union(tip).val())

# Hinge is opposite the OPEN side: KiCad +Y => CAD -Y.
hinge=cq.Workplane('YZ').center(-21.5,9.4).circle(1.45).extrude(29).translate((-14.5,0,0))
supports=[]
for x in (-14,14):
    s=cq.Workplane('XY').box(3.5,4,4.0,centered=(True,True,False)).translate((x,-21.5,5.8))
    supports.append(s.val())

lid=rounded(29.8,31.8,2.4,1.5,8.4)
lid=lid.cut(cylinder(0,0,7.0,8.3,6))
rim=cylinder(0,0,10.2,9.1,0.8).cut(cylinder(0,0,9.8,8.3,2))
press=rounded(27.5,29.5,1.5,1.1,6.9).cut(cylinder(0,0,6.4,7.6,3))
lidarms=[]
for x in (-10.5,10.5):
    arm=cq.Workplane('XY').box(3.4,6.5,2.2,centered=(True,True,False)).translate((x,-18.4,8.4))
    lidarms.append(arm.val())

# Approximate lever protrusion inferred from the gold socket photograph.
latch=cq.Workplane('XY').box(18,10,2,centered=(True,True,False)).edges('|Z').fillet(0.9).translate((0,25.0,8.1))
latch=latch.cut(cq.Workplane('XY').box(14,5.5,5,centered=(True,True,False)).translate((0,24.0,7)))
grip=cq.Workplane('XY').box(18,3.5,1.1,centered=(True,True,False)).edges('|Z').fillet(0.6).translate((0,29.2,10.1))
latchbar=cq.Workplane('YZ').center(22.0,10.4).circle(0.8).extrude(20).translate((-10,0,0))

screwheads=[]
for x,y,d in mounts:
    head=cylinder(x,y,7.4,1.7,0.9)
    slot=cq.Workplane('XY').box(2.6,0.35,1.2,centered=(True,True,False)).translate((x,y,7.8))
    screwheads.append(head.cut(slot).val())

def make_assembly(opened=False):
    assy=cq.Assembly(name='ICS_CQFP64_APPROX_visual_'+('open' if opened else 'closed'))
    parts=[('base',base,CREAM),('metal_frame',frame,GOLD),('contact_guide',guide,CREAM),
           ('hinge',hinge,SILVER),('hinge_supports',cq.Compound.makeCompound(supports),GOLD),
           ('contacts_illustrative',cq.Compound.makeCompound(pins),LIDGOLD),
           ('fastener_heads_illustrative',cq.Compound.makeCompound(screwheads),SILVER),
           ('latch',latch,GOLD),('latch_grip',grip,DARK),('latch_bar',latchbar,SILVER)]
    for name,obj,col in parts:assy.add(obj,name=name,color=col)
    for name,obj,col in [('lid',lid,LIDGOLD),('window_rim',rim,GOLD),('pressure_insert',press,CREAM),('lid_arms',cq.Compound.makeCompound(lidarms),GOLD)]:
        if opened:
            # 105 degrees is illustrative only; NOT a certified lid sweep.
            obj=obj.rotate((0,-21.5,9.4),(1,-21.5,9.4),105)
        assy.add(obj,name=name,color=col)
    return assy

records={}
for opened in (False,True):
    suffix='_APPROX_OPEN' if opened else '_APPROX'
    assy=make_assembly(opened)
    step=OUT/f'{NAME}{suffix}.step'
    assy.export(str(step),exportType='STEP')
    obj=cq.importers.importStep(str(step))
    assert all(x.isValid() for x in obj.vals()),step
    bb=obj.val().BoundingBox()
    records[step.name]={'bbox_mm':{'xmin':bb.xmin,'xmax':bb.xmax,'ymin':bb.ymin,'ymax':bb.ymax,'zmin':bb.zmin,'zmax':bb.zmax},'valid':True,'solid_count':len(obj.solids().vals())}

records['model_status']='APPROXIMATE VISUAL MODEL; not a manufacturer drawing or clearance gauge'
records['exact_from_footprint']=['64 contact center coordinates','six hole center coordinates and diameters','source outline 40 x 50 mm R2']
records['estimated']=['casing dimensions beyond source outline','all heights','contact internal geometry','window diameter','hinge and latch geometry','105-degree open position','lid sweep','screwheads']
records['contact_xy_max_error_mm']=0.0
records['cad_convention']='PCB top at Z=0; CAD Y = - footprint Y; linked closed model offset/rotation zero; scale 1'
(ROOT/'docs/crossbar_socket_source/3D_MODEL_CHECKS.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=2))
