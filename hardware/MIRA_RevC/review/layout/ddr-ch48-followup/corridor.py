from pathlib import Path
import csv
import html
import math
import sys

import pcbnew as k


def point(v):
    return (k.ToMM(v.x), k.ToMM(v.y))

Y=167.75
b=k.LoadBoard(sys.argv[1])
def xs_at_y(poly):
    xs=[]
    for a,c in zip(poly,poly[1:]+poly[:1]):
        if a[1]==c[1]==Y:xs.extend((a[0],c[0]))
        elif min(a[1],c[1])<=Y<=max(a[1],c[1]) and a[1]!=c[1]:
            xs.append(a[0]+(c[0]-a[0])*(Y-a[1])/(c[1]-a[1]))
    return (min(xs),max(xs)) if xs else None
def shape(pad):
    poly=k.SHAPE_POLY_SET()
    pad.TransformShapeToPolygon(poly,k.B_Cu,0,k.FromMM(.001),k.ERROR_OUTSIDE)
    return [[point(poly.COutline(i).CPoint(j)) for j in range(poly.COutline(i).PointCount())] for i in range(poly.OutlineCount())]
obs=[]
polys=[]
for f in b.GetFootprints():
    for p in f.Pads():
        if p.IsOnLayer(k.B_Cu):
            for s in shape(p):
                name=f'{f.GetReference()}.{p.GetNumber()}'
                polys.append((s,name,p.GetNetname()))
                span=xs_at_y(s)
                if span:obs.append((*span,name,p.GetNetname()))
tracks=[t for t in b.GetTracks() if t.IsOnLayer(k.B_Cu)]
samples=[]
for t in tracks:
 a,c=point(t.GetStart()),point(t.GetEnd())
 n=t.GetNetname()
 if isinstance(t,k.PCB_VIA) or t.GetLayer()!=k.B_Cu or n not in ('CH1','CH30','CH31'):continue
 if min(a[1],c[1])<=Y<max(a[1],c[1]) and a[1]!=c[1]:
    x=a[0]+(c[0]-a[0])*(Y-a[1])/(c[1]-a[1])
    own=[o for o in obs if o[0]<=x<=o[1] and o[3]==n]
    left=max((o for o in obs if o[1]<x and o[3]!=n),key=lambda o:o[1])
    right=min((o for o in obs if o[0]>x and o[3]!=n),key=lambda o:o[0])
    span=right[0]-left[1]; half=.1*math.dist(a,c)/abs(a[1]-c[1])
    samples.append((n,x,' '.join(o[2] for o in own),left[2],right[2],span,max(0,x-half-left[1]-.2),max(0,right[0]-x-half-.2)))
dest=Path(sys.argv[2])
with (dest/'corridor-recheck.csv').open('w') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['net','X_mm','same_net_pad','left_blocking_pad','right_blocking_pad','unlike_pad_span_mm','left_residual_after_track_and_0.20_mm','right_residual_after_track_and_0.20_mm'])
 for n,x,own,l,r,s,wl,wr in sorted(samples):w.writerow([n,round(x,3),own,l,r,round(s,3),round(wl,3),round(wr,3)])
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="560" viewBox="0 0 1440 560">','<rect width="1440" height="560" fill="#142435"/>','<text x="30" y="40" fill="#eef" font-size="22">Control B.Cu · Y = 167.75 mm</text>']
for idx,(lo,hi,net,col) in enumerate(((59.5,67,'CH1','#5fedb6'),(134.7,142.2,'CH31','#ffe07d'))):
  xoff=22+idx*714; scale=90;Y0=165.2
  def q(xy):return xoff+scale*(xy[0]-lo),75+scale*(xy[1]-Y0)
  name='p'+str(idx)
  svg.append(f'<clipPath id="{name}"><rect x="{xoff}" y="75" width="675" height="415"/></clipPath><g clip-path="url(#{name})">')
  for poly,ref,n in polys:
   if not any(lo-.5<x<hi+.5 and 164.8<y<170 for x,y in poly):continue
   svg.append('<polygon fill="'+('#38aa9b' if n==net else '#667b92')+'" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in map(q,poly))+'"/>')
   if xs_at_y(poly):
    x,y=q(poly[0]);svg.append(f'<text x="{x:.1f}" y="{y-4:.1f}" fill="#eee" font-size="10">{html.escape(ref)}</text>')
  for t in tracks:
    if isinstance(t,k.PCB_VIA):
      x,y=q(point(t.GetPosition()))
      if xoff<x<xoff+675 and 75<y<490:
       svg.append(f'<circle cx="{x}" cy="{y}" r="{scale*k.ToMM(t.GetWidth(k.B_Cu))/2}" fill="#94a5b8" /><circle cx="{x}" cy="{y}" r="{scale*k.ToMM(t.GetDrillValue())/2}" fill="#213243" />')
      continue
    a,c=map(q,(point(t.GetStart()),point(t.GetEnd())))
    svg.append(f'<path d="M{a[0]:.2f},{a[1]:.2f} L{c[0]:.2f},{c[1]:.2f}" stroke="{col if t.GetNetname()==net else "#dc86ff" if idx==1 and t.GetNetname()=="CH30" else "#7992aa"}" stroke-width="{scale*k.ToMM(t.GetWidth()):.1f}" fill="none" stroke-linecap="round"/>')
  svg.append(f'<path d="M{xoff},{q((lo,Y))[1]} h675" stroke="#fafafa" stroke-width="2" stroke-dasharray="8,6"/></g>')
  svg.append(f'<text x="{xoff}" y="520" fill="{col}" font-size="20">{net} · X = {lo}–{hi} mm</text>')
svg.append('</svg>')
(dest/'ch1-ch31.svg').write_text('\n'.join(svg)+'\n')
