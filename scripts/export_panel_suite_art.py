"""Make a vector-only Suite preview: flatten gradients into 160 color bands.
Requires fonttools and skia-pathops. The original PDF remains the print master.
"""
from pathlib import Path
import xml.etree.ElementTree as E, math
import pathops
from fontTools.svgLib.path import parse_path
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
R=Path(__file__).resolve().parents[1];N='{http://www.w3.org/2000/svg}'
r=E.parse(R/'artwork/decal/NC03_panel_A4_print.svg').getroot()
out=[]
def path(d):
 p=pathops.Path();parse_path(d,p.getPen());return p
def poly(points):return path('M'+' L'.join(f'{x} {y}' for x,y in points)+' Z')
q=4+math.sqrt(2);clip=poly([(q*5,5),((288-q)*5,5),(1435,q*5),(1435,(178-q)*5),((288-q)*5,885),(q*5,885),(5,(178-q)*5),(5,q*5)])
def inter(a,b):return pathops.op(a,b,pathops.PathOp.INTERSECTION)
def emit(p,color,opacity=1):
 try:p=inter(p,clip)
 except pathops.PathOpsError:return
 pen=SVGPathPen(None);p.draw(TransformPen(pen,(.2,0,0,.2,-1,-1)));d=pen.getCommands()
 if d:out.append(f'<path d="{d}" fill="{color}" opacity="{opacity:g}"/>')
grads={g.attrib['id']:g for g in r.iter(N+'linearGradient')}
def draw(p,fill,opacity):
 if fill.startswith('url(#') and fill[5:-1] in grads:
  g=grads[fill[5:-1]];b=p.bounds;x0,y0,x1,y1=b;dx=float(g.get('x2','1'))*(x1-x0);dy=float(g.get('y2','0'))*(y1-y0);length=math.hypot(dx,dy);ux,uy=dx/length,dy/length;nx,ny=-uy,ux
  stops=[]
  for s in g:
   off=float(s.get('offset','0'));co=s.get('stop-color').lstrip('#');stops.append((off,tuple(int(co[i:i+2],16) for i in (0,2,4))))
  for i in range(-160,321):
   a=i/160;b=(i+1)/160;t=min(1,max(0,(a+b)/2));k=next((j for j in range(len(stops)-1) if stops[j][0]<=t<=stops[j+1][0]),len(stops)-2);v=(t-stops[k][0])/(stops[k+1][0]-stops[k][0]);color='#'+''.join(f'{round(c+(d-c)*v):02x}' for c,d in zip(stops[k][1],stops[k+1][1]));quad=poly([(x0+ux*z*length+nx*w,y0+uy*z*length+ny*w) for z,w in [(a,-3000),(b,-3000),(b,3000),(a,3000)]])
   emit(inter(p,quad),color,opacity)
 elif fill=='url(#dots)':
  x0,y0,x1,y1=p.bounds
  for x in range(math.floor(x0/12)*12+5,math.ceil(x1/12)*12,12):
   for y in range(math.floor(y0/12)*12+5,math.ceil(y1/12)*12,12):
    dot=path(f'M{x-2} {y} a2 2 0 1 0 4 0 a2 2 0 1 0 -4 0 Z');emit(inter(dot,p),'#8d42bb',opacity)
 elif fill!='none':emit(p,fill,opacity)
def visit(e,transform=(1,0,0,1,0,0),style=None):
 style=dict(style or {});style.update({k:v for k,v in e.attrib.items() if k in ['fill','opacity']});tag=e.tag.split('}')[-1]
 if tag in ['defs','clipPath']:return
 if tag=='svg' and e is not r:
  x,y,w,h=[float(e.get(k,'0')) for k in ['x','y','width','height']];vx,vy,vw,vh=map(float,e.get('viewBox').split());s=min(w/vw,h/vh);transform=(s,0,0,s,x+(w-vw*s)/2-vx*s,y+(h-vh*s)/2-vy*s)
 d=None
 if tag=='path':d=e.get('d')
 elif tag=='polygon':d='M'+e.get('points').replace(' ', ' L')+' Z'
 elif tag=='rect':
  x=float(e.get('x','0'));y=float(e.get('y','0'));w=float(e.get('width'));h=float(e.get('height'));d=f'M{x} {y} h{w} v{h} h{-w} Z'
 if d:
  p=pathops.Path();parse_path(d,TransformPen(p.getPen(),transform));draw(p,style.get('fill','black'),float(style.get('opacity',1)))
 for child in e:visit(child,transform,style)
visit(r)
# Stroke embellishments remain optional preview-only; original print PDF is authoritative.
s='<svg xmlns="http://www.w3.org/2000/svg" width="286mm" height="176mm" viewBox="0 0 286 176">'+''.join(out)+'</svg>'
(R/'artwork/decal/NC03_panel_Suite_vector_art.svg').write_text(s)
print(len(out),'vector paths')
