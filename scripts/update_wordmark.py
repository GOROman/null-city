"""Build the original angular NULL CITY wordmark as font-independent SVG geometry."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
glyphs=json.loads((root/'fonts/null-font/brand-glyphs.json').read_text())
polygons=[];cursor=22
for ch in 'NULL CITY':
 if ch==' ':cursor+=28;continue
 g=glyphs[ch]
 # Original outlines with a 12-degree forward lean, baked into the geometry.
 import math
 points=[[round(cursor+x-math.tan(math.radians(12))*y,4),y] for x,y in g['points']]
 polygons.append({'character':ch,'points':points});cursor+=g['width']+10
width=round(cursor-10,4)
data={'name':'NULL CITY angular wordmark','height':100,'width':width,'polygons':polygons,'note':'Original geometric lettering. Outlines are independent of installed fonts.'}
(root/'artwork/logo/wordmark.json').write_text(json.dumps(data,indent=2)+'\n')
paths=''.join('<polygon points="'+' '.join(f'{x},{y}' for x,y in p['points'])+'"/>' for p in polygons)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 100" width="{width}" height="100"><title>NULL CITY</title><g fill="#ffffff">{paths}</g></svg>\n'
(root/'artwork/logo/null-city.svg').write_text(svg)
p=root/'artwork/panel.svg';s=p.read_text()
s=re.sub(r'<text x="725" y="758"[^>]*>NULL CITY</text>','',s)
s=re.sub(r'<text x="1180" y="92"[^>]*>1 PLAY</text>','',s)
# Keep the main mark inside the existing lower artwork band.
mark=f'<svg id="null-city-wordmark" x="710" y="657" width="650" height="105" viewBox="0 0 {width} 100"><g fill="#ff08b2" filter="url(#glow)">{paths}</g><g fill="#fff">{paths}</g></svg>'
if 'id="null-city-wordmark"' in s:s=re.sub(r'<svg id="null-city-wordmark".*?</svg>',mark,s,flags=re.S)
else:s=s.replace('<text x="841"',mark+'<text x="841"')
p.write_text(s)
print('Generated font-independent wordmark and removed 1 PLAY')
