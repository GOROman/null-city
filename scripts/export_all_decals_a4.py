"""A4 vector sheet for deck, front, and two side diffuser masks."""
from pathlib import Path
import json,math,xml.etree.ElementTree as E,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artwork/decal';NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)
side=json.loads((ROOT/'artwork/lighting_layout.json').read_text())['side'];a=math.radians(side['slope_degrees'])
p=[(y/math.cos(a)+math.sin(a)*d,-math.cos(a)*d) for y,d in side['lens_front']]
# Inset 0.5 mm perpendicular to all four lens edges, leaving an illuminated rim.
area=sum(p[i][0]*p[(i+1)%4][1]-p[(i+1)%4][0]*p[i][1] for i in range(4));sign=1 if area>0 else -1
lines=[]
for i in range(4):
 x,y=p[i];u,v=p[(i+1)%4];dx,dy=u-x,v-y;n=(-sign*dy/math.hypot(dx,dy),sign*dx/math.hypot(dx,dy));lines.append((x+n[0]*.5,y+n[1]*.5,dx,dy))
pts=[]
for i in range(4):
 x,y,dx,dy=lines[i-1];u,v,ex,ey=lines[i];t=((u-x)*ey-(v-y)*ex)/(dx*ey-dy*ex);pts.append((x+t*dx,y+t*dy))
x0=min(x for x,y in pts);y0=min(y for x,y in pts);pts=[(x-x0,y-y0) for x,y in pts];w=max(x for x,y in pts);h=max(y for x,y in pts)
word=json.loads((ROOT/'artwork/logo/wordmark.json').read_text());scale=.06;logo_w=word['width']*scale+15;left=(w-logo_w)/2;top=(h-6)/2
for side_name in ['left','right']:
 shape=[(w-x,y) if side_name=='left' else (x,y) for x,y in pts]
 poly=' '.join(f'{x:.6f},{y:.6f}' for x,y in shape)
 head=f'<svg xmlns="{NS}" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">'
 body=f'<polygon points="{poly}" fill="#111118"/>'
 for g in word['polygons']:
  xy=' '.join(f'{left+x*scale:.6f},{top+y*scale:.6f}' for x,y in g['points']);body+=f'<polygon points="{xy}" fill="white"/>'
 for i in range(3):
  x=left+word['width']*scale+4+i*3.5;y=top+6;body+=f'<polygon points="{x},{y} {x+1.6},{y} {x+3},{top} {x+1.4},{top}" fill="#ff08b2"/>'
 (OUT/f'NC03_side_{side_name}_print.svg').write_text(head+body+'</svg>')
 (OUT/f'NC03_side_{side_name}_cut.svg').write_text(head+f'<polygon points="{poly}" fill="none" stroke="black" stroke-width="0.01"/></svg>')
def nested(name,x,y,width,height):
 n=E.parse(OUT/name).getroot();n.attrib.update(x=str(x),y=str(y),width=str(width),height=str(height));return E.tostring(n,encoding='unicode')
placements=[('NC03_panel_A4_print.svg',5.5,18,286,176),('NC03_front_suite_print.svg',51.5,4,194,12.5),('NC03_side_left_print.svg',5.5,195,w,h),('NC03_side_right_print.svg',291.5-w,195,w,h)]
head=f'<svg xmlns="{NS}" width="297mm" height="210mm" viewBox="0 0 297 210">'
art=head+''.join(nested(*p) for p in placements)+'</svg>'
cutnames=['NC03_panel_A4_cut.svg','NC03_front_suite_cut.svg','NC03_side_left_cut.svg','NC03_side_right_cut.svg']
cut=head+''.join(nested(name,*p[1:]) for name,p in zip(cutnames,placements))+'</svg>'
(OUT/'NC03_all_decals_A4.svg').write_text(art);(OUT/'NC03_all_decals_A4_cut.svg').write_text(cut)
(OUT/'NC03_all_decals_A4_layout.json').write_text(json.dumps({'side_mask_mm':[w,h],'side_inset_mm':.5,'side_rotation_degrees':side['slope_degrees'],'placements':placements},indent=2))
for name,body in [('NC03_all_decals_A4.pdf',art)]:
 with tempfile.TemporaryDirectory(prefix='nc03-all-decals-') as folder:
  html=Path(folder)/'print.html';html.write_text('<html><head><style>@page{size:A4 landscape;margin:0}html,body{margin:0;width:297mm;height:210mm}body>svg{display:block}</style></head><body>'+body+'</body></html>')
  subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless','--disable-gpu','--no-pdf-header-footer',f'--user-data-dir={folder}/chrome',f'--print-to-pdf={OUT/name}',html.as_uri()],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
assert 195+h<206.6 and 2*w+2<286
print('Four decals on one A4; each side mask',w,h,'mm')
