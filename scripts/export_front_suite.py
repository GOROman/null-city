"""Export tight, shared-coordinate front decal artwork and blade contours for Suite."""
from pathlib import Path
import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artwork/decal'
layout = json.loads((ROOT / 'artwork/lighting_layout.json').read_text())['front']
outline = [(x-layout['mask_origin_x_mm'], layout['mask_top_z_mm']-z) for x,z in layout['mask_outline']]
x0,y0 = min(p[0] for p in outline), min(p[1] for p in outline)
w,h = max(p[0] for p in outline)-x0, max(p[1] for p in outline)-y0
points = ' '.join(f'{x-x0:.4f},{y-y0:.4f}' for x,y in outline)
source = ET.fromstring((OUT/'NC03_front_mask.svg').read_text())
# No text/fonts, references, transforms or nested SVGs in importable artwork.
children = ''.join(ET.tostring(child, encoding='unicode') for child in source if child.tag.split('}')[-1] != 'title')
children = children.replace('ns0:', '').replace(':ns0', '')
header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}mm" height="{h:g}mm" viewBox="{x0:g} {y0:g} {w:g} {h:g}">'
art = header + children + '</svg>'
(OUT/'NC03_front_suite_print.svg').write_text(art)
cut = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}mm" height="{h:g}mm" viewBox="0 0 {w:g} {h:g}"><polygon id="outer-cut" points="{points}" fill="none" stroke="#000000" stroke-width="0.01"/></svg>'
(OUT/'NC03_front_suite_cut.svg').write_text(cut)
# Transparent raster flattens the lettering so Print Then Cut traces only the outer silhouette.
# 20 pixels/mm (~508 dpi), exact aspect ratio. Suite dimensions must be set explicitly.
with tempfile.TemporaryDirectory(prefix='nc03-suite-decal-') as folder:
    html = Path(folder)/'image.html'
    html.write_text(f'<html><head><style>html,body{{margin:0;background:transparent;overflow:hidden}}svg{{display:block;width:{w*20:g}px;height:{h*20:g}px}}</style></head><body>{art}</body></html>')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless','--disable-gpu','--hide-scrollbars','--default-background-color=00000000','--force-device-scale-factor=1',f'--user-data-dir={folder}/chrome',f'--screenshot={OUT}/NC03_front_suite_print.png',f'--window-size={int(w*20)},{int(h*20)}',html.as_uri()],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print(f'Suite artwork and closed outer contour: {w:g} x {h:g} mm')
