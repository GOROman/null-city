"""Export a 203 x 17 mm opaque front mask matching the current original wordmark."""
from pathlib import Path
import json
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
layout=json.loads((root/'artwork/lighting_layout.json').read_text())
wordmark=json.loads((root/'artwork/logo/wordmark.json').read_text())
scale=layout['front_wordmark_scale']
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="203mm" height="17mm" viewBox="0 0 203 17">',
     '<title>NULL CITY front lighting mask</title>',
     '<polygon points="4.5,12.5 198.5,12.5 189.3,0 13.7,0" fill="#111118"/>','<g fill="white">']
for glyph in wordmark['polygons']:
    points=[(101.5+layout['front_wordmark_left_mm']+x*scale,
             22-layout['front_wordmark_baseline_mm']-(100-y)*scale) for x,y in glyph['points']]
    svg.append('<polygon points="'+' '.join(f'{x:.4f},{y:.4f}' for x,y in points)+'"/>')
svg+=['</g><g fill="#ff08b2">']
for x in (128.5,132.5,136.5):
    svg.append(f'<polygon points="{x},12 {x+2},12 {x+5},4 {x+3},4"/>')
svg+=['</g></svg>'];text=''.join(svg)
out=root/'artwork/decal';(out/'NC03_front_mask.svg').write_text(text)
with tempfile.TemporaryDirectory(prefix='nc03-front-mask-') as folder:
    html=Path(folder)/'print.html'
    html.write_text('<html><head><style>@page{size:203mm 17mm;margin:0}html,body{margin:0;width:203mm;height:17mm}svg{display:block}</style></head><body>'+text+'</body></html>')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless','--disable-gpu','--no-pdf-header-footer',f'--user-data-dir={folder}/chrome',f'--print-to-pdf={out}/NC03_front_mask.pdf',html.as_uri()],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
