"""Vector A3 delivery sheets with bleed/crop marks and versioned A4 proof."""
from pathlib import Path
import datetime,subprocess,tempfile,xml.etree.ElementTree as E
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artwork/decal';NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)
VERSION='v1.1';DATE='2026-11-16';FONT=TTFont(ROOT/'fonts/null-font/NULLFont-Regular.ttf');GLYPHS=FONT.getGlyphSet();CMAP=FONT.getBestCmap()
def label(x,y,text,size=2.5):
 result=[];s=size/FONT['head'].unitsPerEm
 for ch in text.upper():
  glyph=GLYPHS[CMAP[ord(ch)]];pen=SVGPathPen(GLYPHS);glyph.draw(TransformPen(pen,(s,0,0,-s,x,y)))
  if pen.getCommands():result.append(f'<path d="{pen.getCommands()}" fill="#333333"/>')
  x+=glyph.width*s
 return ''.join(result)
def nested(name,x,y,w,h):
 n=E.parse(OUT/name).getroot();n.attrib.update(x=str(x),y=str(y),width=str(w),height=str(h));return E.tostring(n,encoding='unicode')
def pdf(name,body,page):
 with tempfile.TemporaryDirectory(prefix='nc03-prepress-') as folder:
  html=Path(folder)/'print.html';html.write_text(f'<html><head><style>@page{{size:{page};margin:0}}html,body{{margin:0}}body>svg{{display:block}}</style></head><body>'+body+'</body></html>')
  subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless','--disable-gpu','--no-pdf-header-footer',f'--user-data-dir={folder}/chrome',f'--print-to-pdf={OUT/name}',html.as_uri()],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
# Exact ISO page boxes, correcting Chromium's fractional paper-size rounding.
raw_pdf=pdf
def pdf(name,body,page):
 raw_pdf(name,body,page)
 from pypdf import PdfReader,PdfWriter,Transformation
 from pypdf.generic import RectangleObject
 target=OUT/name;reader=PdfReader(target);writer=PdfWriter();w,h=(420,297) if page.startswith('A3') else (297,210)
 for page_in in reader.pages:
  p=writer.add_page(page_in)
  dy=h*72/25.4-float(p.mediabox.height)
  p.add_transformation(Transformation().translate(0,dy));p.mediabox=RectangleObject([0,0,w*72/25.4,h*72/25.4])
 writer.add_metadata({'/Title':f'NULL CITY NC-03 DECAL {VERSION} {DATE}'})
 with target.open('wb') as stream:writer.write(stream)
import json
layout=json.loads((OUT/'NC03_all_decals_A4_layout.json').read_text());w,h=layout['side_mask_mm']
items=[('DECK','NC03_panel_A4_print.svg','NC03_panel_A4_cut.svg',67,69,286,176),('FRONT','NC03_front_suite_print.svg','NC03_front_suite_cut.svg',113,36,194,12.5),('LEFT','NC03_side_left_print.svg','NC03_side_left_cut.svg',45,270,w,h),('RIGHT','NC03_side_right_print.svg','NC03_side_right_cut.svg',235,270,w,h)]
head=f'<svg xmlns="{NS}" width="420mm" height="297mm" viewBox="0 0 420 297">'
body=label(18,13,'NULL CITY / NC-03 / DECAL ARTWORK',4)+label(18,20,'A3 LANDSCAPE / ACTUAL SIZE 100% / BLEED 3 MM / RGB VECTOR MASTER',2.3)
cuts=[]
for title,art,cut,x,y,w,h in items:
 # Bleed backing deliberately continues the dark base color beyond the trim shape.
 body+=f'<rect x="{x-3}" y="{y-3}" width="{w+6}" height="{h+6}" fill="#111118"/>'+nested(art,x,y,w,h)
 marks=[]
 for xx,d in [(x,-1),(x+w,1)]:
  for yy,e in [(y,-1),(y+h,1)]:
   marks.append(f'M{xx+d*3} {yy} h{d*4} M{xx} {yy+e*3} v{e*4}')
 body+='<path d="'+' '.join(marks)+'" fill="none" stroke="black" stroke-width="0.15"/>'
 body+=label(x,y-9,f'{title} / {w:.2f} X {h:.2f} MM',2.0)
 cuts.append(nested(cut,x,y,w,h))
footer=f'NULL CITY / NC-03 DECAL {VERSION} / {DATE} / GOROMAN / A3 / 1 OF 1'
body+=label(18,289,footer,2.4)+label(18,293,'TRIM AT CONTOUR / CROP MARKS ARE NOT CUTTER REGISTRATION MARKS / NO SCALE TO FIT',1.8)
art=head+body+'</svg>';(OUT/'NC03_all_decals_A3_prepress.svg').write_text(art);pdf('NC03_all_decals_A3_prepress.pdf',art,'A3 landscape')
cut=head+''.join(cuts)+'</svg>';(OUT/'NC03_all_decals_A3_cut.svg').write_text(cut)
guide=E.fromstring(cut)
for n in guide.iter():
 if n.tag.split('}')[-1] in ['path','polygon','circle','rect','g']:n.attrib.update(fill='none',stroke='#ff00ff',**{'stroke-width':'0.12'})
check=head+body+''.join(E.tostring(n,encoding='unicode') for n in guide)+'</svg>'
pdf('NC03_all_decals_A3_cut_guide.pdf',check,'A3 landscape')
a4=(OUT/'NC03_all_decals_A4.svg').read_text();a4=a4.removesuffix('</svg>')+label(5.5,206.1,f'NC-03 DECAL {VERSION} / {DATE} / A4 / 100%',1.6)+'</svg>'
(OUT/'NC03_all_decals_A4_versioned.svg').write_text(a4);pdf('NC03_all_decals_A4_versioned.pdf',a4,'A4 landscape')
print('A3: four original-scale decals, 3 mm bleed backing, crop marks, outlined version/date footer. A4 versioned proof retained.')

# Spacious A4 accessory sheet: each part has its own clear crop-mark area.
accessories=[('FRONT','NC03_front_suite_print.svg','NC03_front_suite_cut.svg',51.5,35,194,12.5),('LEFT','NC03_side_left_print.svg','NC03_side_left_cut.svg',25,90,*layout['side_mask_mm']),('RIGHT','NC03_side_right_print.svg','NC03_side_right_cut.svg',131,135,*layout['side_mask_mm'])]
access_body=label(18,15,'NULL CITY / FRONT + SIDES / A4',3.5)
for title,artname,cutname,x,y,w,h in accessories:
 access_body+=f'<rect x="{x-3}" y="{y-3}" width="{w+6}" height="{h+6}" fill="#111118"/>'+nested(artname,x,y,w,h)
 marks=[]
 for xx,d in [(x,-1),(x+w,1)]:
  for yy,e in [(y,-1),(y+h,1)]:marks.append(f'M{xx+d*3} {yy} h{d*4} M{xx} {yy+e*3} v{e*4}')
 access_body+='<path d="'+' '.join(marks)+'" fill="none" stroke="black" stroke-width="0.15"/>'+label(x,y-10,f'{title} / {w:.2f} X {h:.2f} MM',2.3)
access_body+=label(18,190,f'NC-03 DECAL {VERSION} / {DATE} / FRONT + SIDES / A4 / 100%',2.3)+label(18,196,'3 MM BLEED / CUT AT SHAPED CONTOUR / CROP MARKS ARE NOT SUITE REGISTRATION',1.8)
access_sheet=f'<svg xmlns="{NS}" width="297mm" height="210mm" viewBox="0 0 297 210">'+access_body+'</svg>'
(OUT/'NC03_front_and_sides_A4_prepress.svg').write_text(access_sheet)
pdf('NC03_front_and_sides_A4_prepress.pdf',access_sheet,'A4 landscape')
access_cut=f'<svg xmlns="{NS}" width="297mm" height="210mm" viewBox="0 0 297 210">'+''.join(nested(cutname,x,y,w,h) for _,_,cutname,x,y,w,h in accessories)+'</svg>'
(OUT/'NC03_front_and_sides_A4_cut.svg').write_text(access_cut)
access_guides=E.fromstring(access_cut)
for n in access_guides.iter():
 if n.tag.split('}')[-1] in ['path','polygon','circle','rect','g']:n.attrib.update(fill='none',stroke='#ff00ff',**{'stroke-width':'0.12'})
access_guide=access_sheet.removesuffix('</svg>')+''.join(E.tostring(n,encoding='unicode') for n in access_guides)+'</svg>'
pdf('NC03_front_and_sides_A4_cut_guide.pdf',access_guide,'A4 landscape')

deck_page=f'<svg xmlns="{NS}" width="297mm" height="210mm" viewBox="0 0 297 210">'+nested('NC03_panel_A4_print.svg',5.5,17,286,176)+label(12,205,f'NC-03 DECAL {VERSION} / {DATE} / DECK / A4 / 100%',2.0)+'</svg>'
pdf('NC03_panel_decal_A4_versioned.pdf',deck_page,'A4 landscape')

# Keep the deck itself on one A4 sheet; accessories get their own page.
from pypdf import PdfReader,PdfWriter
writer=PdfWriter()
for name in ['NC03_panel_decal_A4_versioned.pdf','NC03_front_and_sides_A4_prepress.pdf']:
 writer.add_page(PdfReader(OUT/name).pages[0])
writer.add_metadata({'/Title':f'NULL CITY NC-03 DECALS {VERSION} {DATE} - A4 2 SHEETS'})
with (OUT/'NC03_decals_A4_2sheets.pdf').open('wb') as stream:writer.write(stream)
