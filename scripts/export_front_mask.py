"""Export a 203 x 17 mm opaque front mask matching the current original wordmark."""
from pathlib import Path
import json
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
layout=json.loads((root/'artwork/lighting_layout.json').read_text())
wordmark=json.loads((root/'artwork/logo/wordmark.json').read_text())
scale=layout['front_wordmark_scale'];front=layout['front']
width,height=front['mask_canvas_mm'];origin=front['mask_origin_x_mm'];top=front['mask_top_z_mm']
def points_text(points):return ' '.join(f'{x:.4f},{y:.4f}' for x,y in points)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" viewBox="0 0 {width} {height}">',
     '<title>NULL CITY front lighting mask</title>',
     '<polygon points="'+points_text([(x-origin,top-z) for x,z in front['mask_outline']])+'" fill="#111118"/>','<g fill="white">']
for glyph in wordmark['polygons']:
    points=[(layout['front_wordmark_left_mm']-origin+x*scale,
             top-layout['front_wordmark_baseline_mm']-(100-y)*scale) for x,y in glyph['points']]
    svg.append('<polygon points="'+points_text(points)+'"/>')
svg+=['</g><g fill="#ff08b2">']
for x in front['slash_x_mm']:
    x-=origin;y=top-front['slash_bottom_z_mm'];w=front['slash_width_mm'];h=front['slash_height_mm'];lean=front['slash_shear_mm']
    svg.append('<polygon points="'+points_text([(x,y),(x+w,y),(x+w+lean,y-h),(x+lean,y-h)])+'"/>')
svg+=['</g></svg>'];text=''.join(svg)
out=root/'artwork/decal';(out/'NC03_front_mask.svg').write_text(text)
with tempfile.TemporaryDirectory(prefix='nc03-front-mask-') as folder:
    html=Path(folder)/'print.html'
    html.write_text(f'<html><head><style>@page{{size:{width}mm {height}mm;margin:0}}html,body{{margin:0;width:{width}mm;height:{height}mm}}svg{{display:block}}</style></head><body>'+text+'</body></html>')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless','--disable-gpu','--no-pdf-header-footer',f'--user-data-dir={folder}/chrome',f'--print-to-pdf={out}/NC03_front_mask.pdf',html.as_uri()],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
