"""One A4 sheet: full-scale deck and front logo, with matching vector cut paths."""
from pathlib import Path
import subprocess,tempfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artwork/decal';NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
def nested(name,x,y,w,h):
 n=ET.fromstring((OUT/name).read_text());n.attrib.update({'x':str(x),'y':str(y),'width':str(w),'height':str(h)});return ET.tostring(n,encoding='unicode')
header=f'<svg xmlns="{NS}" width="297mm" height="210mm" viewBox="0 0 297 210">'
art=header+nested('NC03_panel_A4_print.svg',5.5,21,286,176)+nested('NC03_front_suite_print.svg',51.5,5,194,12.5)+'</svg>'
cut=header+nested('NC03_panel_A4_cut.svg',5.5,21,286,176)+nested('NC03_front_suite_cut.svg',51.5,5,194,12.5)+'</svg>'
(OUT/'NC03_deck_and_front_A4.svg').write_text(art)
(OUT/'NC03_deck_and_front_A4_cut.svg').write_text(cut)
# Guide uses magenta lines in the same page coordinates.
guide_root=ET.fromstring(cut)
for n in guide_root.iter():
 if n.tag.split('}')[-1] in ['path','circle','rect','polygon','g']:
  n.set('fill','none');n.set('stroke','#ff00ff');n.set('stroke-width','0.12')
guide=art.removesuffix('</svg>')+''.join(ET.tostring(n,encoding='unicode') for n in guide_root)+'</svg>'
for name,body in [('NC03_deck_and_front_A4.pdf',art),('NC03_deck_and_front_A4_cut_guide.pdf',guide)]:
 with tempfile.TemporaryDirectory(prefix='nc03-combined-a4-') as folder:
  html=Path(folder)/'print.html';html.write_text('<html><head><style>@page{size:A4 landscape;margin:0}html,body{margin:0;width:297mm;height:210mm}body>svg{display:block}</style></head><body>'+body+'</body></html>')
  subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless','--disable-gpu','--no-pdf-header-footer',f'--user-data-dir={folder}/chrome',f'--print-to-pdf={OUT/name}',html.as_uri()],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print('Deck: (5.5,21), 286x176 mm; front: (51.5,5), 194x12.5 mm; gap 3.5 mm; no scaling')
