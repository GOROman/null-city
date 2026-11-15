"""Generate full-size deck artwork and cut guides from the shared control layout."""
from pathlib import Path
import json,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
controls=json.loads((root/'artwork/control_layout.json').read_text())
leds=json.loads((root/'artwork/led_layout.json').read_text())
art=(root/'artwork/panel.svg').read_text()
out=root/'artwork/decal';out.mkdir(exist_ok=True)
holes=[(*p,15.2) for p in controls['buttons']]+[(*p,6.2) for p in controls['menu_buttons']]+[(*controls['lever'],12)]
mount=controls.get('lever_mount')
if mount:
 holes += [(controls['lever'][0]+dx,controls['lever'][1]+dy,mount['clearance_diameter_mm']/2) for dx in (-mount['pitch_mm'][0]/2,mount['pitch_mm'][0]/2) for dy in (-mount['pitch_mm'][1]/2,mount['pitch_mm'][1]/2)]
holes += [(x,y,1.7) for x in (-135,135) for y in (-80,80)]
def circle(x,y,r):return f'<circle cx="{(x+144)*5}" cy="{(89-y)*5}" r="{r*5}"/>'
for guide in (False,True):
 name='NC03_decal_cut_guide' if guide else 'NC03_decal_print'
 svg=art
 if guide:
  cuts='<path d="M25 0 H1415 L1440 25 V865 L1415 890 H25 L0 865 V25 Z"/>'+''.join(circle(*h) for h in holes)
  marks=''.join(circle(l['x'],l['y'],leds['hole_diameter_mm']/2) for l in leds['leds'])
  svg=svg.replace('</svg>','<g id="cut-guides" fill="none" stroke="#ff00ff" stroke-width="1.5" stroke-dasharray="8 4">'+cuts+'</g><g id="led-cut-guides" fill="none" stroke="#ff00ff" stroke-width="1.5" stroke-dasharray="4 2">'+marks+'</g></svg>')
 (out/(name+'.svg')).write_text(svg)
 with tempfile.TemporaryDirectory(prefix='nc03-decal-') as folder:
  html=Path(folder)/'print.html'
  html.write_text('<html><head><style>@page{size:288mm 178mm;margin:0}html,body{margin:0;padding:0;width:288mm;height:178mm}svg{display:block;width:288mm;height:178mm}</style></head><body>'+svg+'</body></html>')
  subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless','--disable-gpu','--no-pdf-header-footer',f'--user-data-dir={folder}/chrome',f'--print-to-pdf={out}/{name}.pdf',html.as_uri()],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 print(name)
