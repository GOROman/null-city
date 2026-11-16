"""Lay out the existing front wordmark at actual size on A4 photo paper."""
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artwork/decal'
source = (OUT / 'NC03_front_mask.svg').read_text()
node = ET.fromstring(source)
width = float(node.attrib['width'].removesuffix('mm'))
height = float(node.attrib['height'].removesuffix('mm'))
assert width == 203 and height == 17
# A4 landscape gives generous non-borderless printer margins.
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210">',
         '<rect width="297" height="210" fill="white"/>',
         '<g font-family="sans-serif" fill="#222"><text x="25" y="22" font-size="5">NULL CITY / FRONT DECAL</text>',
         '<text x="25" y="30" font-size="3.5">A4 landscape - Actual size / 100% - No fit to page</text>',
         '<text x="25" y="37" font-size="3.5">Cut size: 194 x 12.5 mm / Canvas: 203 x 17 mm</text></g>']
for y in (52, 89, 126):
    nested = source.replace('width="203mm"', 'width="203"').replace('height="17mm"', 'height="17"').replace('<svg ', f'<svg x="47" y="{y}" ', 1)
    parts.append(nested)
    parts.append(f'<polygon points="51.5,{y+12.5} 245.5,{y+12.5} 236.3,{y} 60.7,{y}" fill="none" stroke="#777" stroke-width="0.15" stroke-dasharray="1 1"/>')
parts += ['<path d="M47 174H147 M47 171V177 M147 171V177" fill="none" stroke="black" stroke-width="0.25"/>',
          '<text x="80" y="183" font-size="3.5" font-family="sans-serif">100 mm scale check</text>',
          '<text x="25" y="197" font-size="3" font-family="sans-serif">GOROman / null-city / CC BY 4.0 - Ordinary photo paper is opaque; cut letters for light transmission.</text>', '</svg>']
svg = ''.join(parts)
(OUT / 'NC03_front_decal_A4.svg').write_text(svg)
with tempfile.TemporaryDirectory(prefix='nc03-front-a4-') as folder:
    html = Path(folder) / 'print.html'
    html.write_text('<html><head><style>@page{size:A4 landscape;margin:0}html,body{margin:0;width:297mm;height:210mm}svg{display:block}</style></head><body>' + svg + '</body></html>')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--headless', '--disable-gpu', '--no-pdf-header-footer', f'--user-data-dir={folder}/chrome', f'--print-to-pdf={OUT}/NC03_front_decal_A4.pdf', html.as_uri()], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(OUT / 'NC03_front_decal_A4.pdf')
