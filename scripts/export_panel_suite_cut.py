"""Plain compound-path import for Bambu Suite, with zero-origin physical bounds."""
from pathlib import Path
import json, math
ROOT=Path(__file__).resolve().parents[1]
c=json.loads((ROOT/'artwork/control_layout.json').read_text())
l=json.loads((ROOT/'artwork/led_layout.json').read_text())
q=4+math.sqrt(2)
points=[(q-1,0),(287-q,0),(286,q-1),(286,177-q),(287-q,176),(q-1,176),(0,177-q),(0,q-1)]
outer='M'+' L'.join(f'{x:.6f} {y:.6f}' for x,y in points)+' Z'
inner=[]
def circle(x,y,r):
 x+=143;y=88-y
 inner.append(f'M{x-r:.6f} {y:.6f} A{r:g} {r:g} 0 1 0 {x+r:.6f} {y:.6f} A{r:g} {r:g} 0 1 0 {x-r:.6f} {y:.6f} Z')
for x,y in c['buttons']:circle(x,y,c['main_button_hole_diameter_mm']/2)
for x,y in c['menu_buttons']:circle(x,y,c['menu_button_hole_diameter_mm']/2)
circle(*c['lever'],12)
m=c['lever_mount']
for dx in (-m['pitch_mm'][0]/2,m['pitch_mm'][0]/2):
 for dy in (-m['pitch_mm'][1]/2,m['pitch_mm'][1]/2):circle(c['lever'][0]+dx,c['lever'][1]+dy,m['clearance_diameter_mm']/2)
for x in (-135,135):
 for y in (-80,80):circle(x,y,1.7)
for led in l['leds']:
 x=led['x']+143-2;y=88-led['y']-2
 inner.append(f'M{x:.6f} {y:.6f} h4 v4 h-4 Z')
assert len(inner)==33
svg='<svg xmlns="http://www.w3.org/2000/svg" width="286mm" height="176mm" viewBox="0 0 286 176"><path id="CUT_ONLY_33_holes_and_perimeter" fill="black" fill-rule="evenodd" d="'+' '.join(inner+[outer])+'"/></svg>'
(ROOT/'artwork/decal/NC03_panel_Suite_basic_cut.svg').write_text(svg)
print('Suite plain path: 34 closed contours, exact 286 x 176 mm, no text/images/strokes/clip-path/transforms')
