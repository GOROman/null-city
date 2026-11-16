"""Generate full deck blade paths, A4 tiled/A3 PDFs, and Suite print artwork."""
from pathlib import Path
import json
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artwork/decal'
c=json.loads((ROOT/'artwork/control_layout.json').read_text())
l=json.loads((ROOT/'artwork/led_layout.json').read_text())
art=(ROOT/'artwork/panel.svg').read_text()
outer='M5 0 H283 L288 5 V173 L283 178 H5 L0 173 V5 Z'
svghead='<svg xmlns="http://www.w3.org/2000/svg" width="288mm" height="178mm" viewBox="0 0 288 178">'
inner=[]
def circle(x,y,r):
    inner.append(f'<circle cx="{x+144:g}" cy="{89-y:g}" r="{r:g}"/>')
for x,y in c['buttons']: circle(x,y,c['main_button_hole_diameter_mm']/2)
for x,y in c['menu_buttons']: circle(x,y,c['menu_button_hole_diameter_mm']/2)
circle(*c['lever'],12)
m=c['lever_mount']
for dx in (-m['pitch_mm'][0]/2,m['pitch_mm'][0]/2):
    for dy in (-m['pitch_mm'][1]/2,m['pitch_mm'][1]/2):
        circle(c['lever'][0]+dx,c['lever'][1]+dy,m['clearance_diameter_mm']/2)
for x in (-135,135):
    for y in (-80,80): circle(x,y,1.7)
for led in l['leds']:
    size=l['aperture_size_mm']
    inner.append(f'<rect x="{led["x"]+144-size/2:g}" y="{89-led["y"]-size/2:g}" width="{size:g}" height="{size:g}"/>')
assert len(inner)==33
# A 1 mm geometric inset, preserving 45-degree corner offsets and all hole centers.
import math
q=5+math.sqrt(2)-1
outer=f'M{q:g} 1 H{288-q:g} L287 {q:g} V{178-q:g} L{288-q:g} 177 H{q:g} L1 {178-q:g} V{q:g} Z'
for name,paths in [('cut', ''.join(inner)+f'<path d="{outer}"/>'),('inner_cut',''.join(inner))]:
    head='<svg xmlns="http://www.w3.org/2000/svg" width="286mm" height="176mm" viewBox="1 1 286 176">'
    (OUT/f'NC03_panel_A4_{name}.svg').write_text(head+'<g fill="none" stroke="black" stroke-width="0.01">'+paths+'</g></svg>')
# Outline all legends with the project's own NULL FONT. No embedded text or bitmaps.
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
root=ET.fromstring(art)
fonts={style:TTFont(ROOT/f'fonts/null-font/NULLFont-{style}.ttf') for style in ('Regular','Italic')}
def outline_text(node,inherited):
    attrs=dict(inherited);attrs.update(node.attrib)
    if node.tag==f'{{{NS}}}text':
        size=float(attrs.get('font-size','32'));tracking=float(attrs.get('letter-spacing',0))
        font=fonts['Italic' if attrs.get('font-style')=='italic' else 'Regular']
        glyphs=font.getGlyphSet();cmap=font.getBestCmap();scale=size/font['head'].unitsPerEm
        spans=[(node.text or '',attrs.get('fill','white'))]+[(child.text or '',child.attrib.get('fill',attrs.get('fill','white'))) for child in node]
        spans=[(t.replace('\u3000',' '),color) for t,color in spans]
        def advance(t):return sum(glyphs[cmap[ord(ch)]].width*scale+tracking for ch in t)
        total=sum(advance(t) for t,_ in spans)
        x=float(attrs['x'])-(total/2 if attrs.get('text-anchor')=='middle' else 0);y=float(attrs['y'])
        group=ET.Element(f'{{{NS}}}g')
        for text,color in spans:
            for ch in text:
                glyph=glyphs[cmap[ord(ch)]];pen=SVGPathPen(glyphs)
                glyph.draw(TransformPen(pen,(scale,0,0,-scale,x,y)))
                if pen.getCommands():ET.SubElement(group,f'{{{NS}}}path',{'d':pen.getCommands(),'fill':color})
                x+=glyph.width*scale+tracking
        return group
    # Remove SVG blur filter instead of flattening it into a bitmap in the PDF.
    node.attrib.pop('filter',None)
    for i,child in enumerate(list(node)):
        if child.tag==f'{{{NS}}}filter':node.remove(child)
        else:node.remove(child);node.insert(i,outline_text(child,attrs))
    return node
root=outline_text(root,{})
root.set('width','286mm');root.set('height','176mm');root.set('viewBox','5 5 1430 880')
# Clip to the inset perimeter in the original artwork coordinate system.
clip=ET.SubElement(root.find(f'{{{NS}}}defs'),f'{{{NS}}}clipPath',{'id':'a4-inset'})
pts=[(q,1),(288-q,1),(287,q),(287,178-q),(288-q,177),(q,177),(1,178-q),(1,q)]
ET.SubElement(clip,f'{{{NS}}}polygon',{'points':' '.join(f'{x*5:g},{y*5:g}' for x,y in pts)})
group=ET.Element(f'{{{NS}}}g',{'clip-path':'url(#a4-inset)'})
for child in list(root):
    if child.tag!=f'{{{NS}}}defs':root.remove(child);group.append(child)
root.append(group)
assert not root.findall(f'.//{{{NS}}}text') and not root.findall(f'.//{{{NS}}}image')
vector=ET.tostring(root,encoding='unicode')
(OUT/'NC03_panel_A4_print.svg').write_text(vector)
# Parent uses mm as viewBox units, so child physical sizes are unitless here.
nested=vector.replace('width="286mm"','x="5.5" y="17" width="286"',1).replace('height="176mm"','height="176"',1)
page='<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210">'+nested+'</svg>'
# Separate guide PDF for manual cutting, retaining the clean print PDF for appearance.
cutpaths=''.join(inner)+f'<path d="{outer}"/>'
guide=page.replace('</svg></svg>','</svg><svg x="5.5" y="17" width="286" height="176" viewBox="1 1 286 176"><g fill="none" stroke="#ff00ff" stroke-width="0.12">'+cutpaths+'</g></svg></svg>')
chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
for name,body in [('NC03_panel_decal_A4.pdf',page),('NC03_panel_decal_A4_cut_guide.pdf',guide)]:
    with tempfile.TemporaryDirectory(prefix='nc03-panel-a4-') as folder:
        html=Path(folder)/'print.html';html.write_text('<html><head><style>@page{size:A4 landscape;margin:0}html,body{margin:0;width:297mm;height:210mm}body>svg{display:block}</style></head><body>'+body+'</body></html>')
        subprocess.run([chrome,'--headless','--disable-gpu','--no-pdf-header-footer',f'--user-data-dir={folder}/chrome',f'--print-to-pdf={OUT/name}',html.as_uri()],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print('A4 landscape single sheet: 286 x 176 mm inset artwork; 33 holes at original coordinates; outlined NULL FONT')
