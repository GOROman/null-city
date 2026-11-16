"""Actual blade paths matching the printed compact A4 sheet; excludes all artwork.
No automatic paper registration: align the physical sheet before running.
Requires fonttools. Cutting pressure remains provisional until a physical test.
"""
from pathlib import Path
import json,zipfile,uuid,xml.etree.ElementTree as ET
from fontTools.svgLib.path import parse_path
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artwork/decal'
layout=json.loads((OUT/'NC03_all_decals_A4_layout.json').read_text());svgpen=SVGPathPen(None)
# Source is one compound deck contour: 33 inner apertures followed by its perimeter.
panel=ET.parse(OUT/'NC03_panel_Suite_basic_cut.svg').getroot();d=next(iter(panel)).get('d');parse_path(d,TransformPen(svgpen,(1,0,0,1,5.5,18)))
for name,placement in zip(['NC03_front_suite_cut.svg','NC03_side_left_cut.svg','NC03_side_right_cut.svg'],layout['placements'][1:]):
 root=ET.parse(OUT/name).getroot();polygon=next(iter(root));points=[tuple(map(float,p.split(','))) for p in polygon.get('points').split()]
 d='M'+' L'.join(f'{x} {y}' for x,y in points)+' Z';parse_path(d,TransformPen(svgpen,(1,0,0,1,placement[1],placement[2])))
svgpath=svgpen.getCommands()
class NativePen(BasePen):
 def __init__(self):super().__init__(None);self.commands=[];self.contours=0;self.closed=0
 def _moveTo(self,p):self.contours+=1;self.commands.append(f'M {p[0]:.6f} {p[1]:.6f}')
 def _lineTo(self,p):self.commands.append(f'L {p[0]:.6f} {p[1]:.6f}')
 def _curveToOne(self,c1,c2,end):self.commands.append('C '+' '.join(f'{x:.6f} {y:.6f}' for x,y in [end,c1,c2]))
 def _closePath(self):self.closed+=1;self.commands.append('Z')
 def _endPath(self):raise ValueError('Open cutting path')
pen=NativePen();parse_path(svgpath,pen);assert pen.contours==pen.closed==37
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210"><path fill="black" fill-rule="evenodd" d="{svgpath}"/></svg>'
(OUT/'NC03_all_decals_A4_CUT_ONLY.svg').write_text(svg)
with zipfile.ZipFile(OUT/'NC03_panel_A4_basic_cut.lac') as z:data={n:z.read(n) for n in z.namelist()}
m=json.loads(data['2D/2dmodel.json']);c=m['canvas_list'][0];obj=c['obj_list'][0];oid=obj['obj_id'];obj.update(name='CUT_ONLY_A4_37_closed_contours',path_data=' '.join(pen.commands),is_closed=True,color='0 0 0 255')
c['name']='A4_PRINTED_ALL4_CUT_ONLY';c['components']=[{'obj_id':oid,'transform':'1 0 0 1 0 0'}]
s=json.loads(data['Metadata2D/project_settings.json']);cs=s['canvas_settings'][0];cs['object_settings']=[{'obj_id':oid,'process_type':'KCBasicCut'}]
for batch in cs['making_batch_list']:
 for plate in batch['making_plate_list']:plate['components']=[{'obj_id':oid,'transform':'1 0 0 1 0 0'}]
entry=json.loads(data['2D/entry.json']);entry['Title']='NC-03 PRINTED A4 ALL4 - CUT ONLY - ALIGN PAPER FIRST'
data['2D/entry.json']=json.dumps(entry).encode();data['2D/2dmodel.json']=json.dumps(m).encode();data['Metadata2D/project_settings.json']=json.dumps(s).encode()
with zipfile.ZipFile(OUT/'NC03_all_decals_A4_CUT_ONLY_NOMINAL.lac','w',zipfile.ZIP_DEFLATED) as z:
 for name,value in data.items():z.writestr(name,value)
report={'matching_print_master':'NC03_all_decals_A4_versioned.pdf','contours':37,'inner_holes':33,'outer_perimeters':4,'artwork_objects':0,'paper_mm':[297,210],'paper_thickness_mm':.27,'automatic_registration_marks':False,'physical_alignment_verified':False,'pressure_verified':False}
(OUT/'NC03_all_decals_A4_cut_validation.json').write_text(json.dumps(report,indent=2))
print('PASS: 37 closed paths; no artwork; original printed A4 placements retained. Physical alignment/test required.')
