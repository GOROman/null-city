"""Build the original angular NULL CITY wordmark as font-independent SVG geometry."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
glyphs={
'N':{'width':76,'points':[[0,100],[0,0],[19,0],[57,64],[57,0],[76,0],[76,100],[57,100],[19,36],[19,100]]},
'U':{'width':76,'points':[[0,0],[19,0],[19,74],[26,81],[50,81],[57,74],[57,0],[76,0],[76,80],[56,100],[20,100],[0,80]]},
'L':{'width':64,'points':[[0,0],[19,0],[19,80],[64,80],[64,92],[56,100],[0,100]]},
'C':{'width':76,'points':[[20,0],[76,0],[76,19],[29,19],[19,29],[19,71],[29,81],[76,81],[76,100],[20,100],[0,80],[0,20]]},
'I':{'width':22,'points':[[0,0],[22,0],[22,100],[0,100]]},
'T':{'width':76,'points':[[0,0],[76,0],[76,19],[47,19],[47,100],[29,100],[29,19],[0,19]]},
'Y':{'width':80,'points':[[0,0],[21,0],[40,34],[59,0],[80,0],[50,54],[50,100],[30,100],[30,54]]}}
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
