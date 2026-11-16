"""Combine existing native Suite vector artwork/cut objects in A4 page coordinates.
Review only: use the original PDF for printing and separate cut-only jobs for cutting.
"""
from pathlib import Path
import zipfile,json,uuid,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artwork/decal'
source=OUT/'NC03_panel_A4_artwork_and_cut_REVIEW.lac'
with zipfile.ZipFile(source) as z:data={n:z.read(n) for n in z.namelist()}
m=json.loads(data['2D/2dmodel.json']);c=m['canvas_list'][0];objects=c['obj_list']
cut=next(o for o in objects if o['name']=='CUT_33_holes_and_outer_perimeter')
art=next(o for o in objects if o['type']=='ModelGroup')
s=json.loads(data['Metadata2D/project_settings.json']);settings=s['canvas_settings'][0]
nextid=max(o['obj_id'] for o in objects)+10

def add_object(name,path,color,closed=True):
 global nextid
 oid=nextid;nextid+=3
 objects.append({'type':'PathObject','name':name,'obj_id':oid,'uuid':str(uuid.uuid4()),'flags':['FreeAspectRatio'],'color':color,'is_closed':closed,'path_data':path})
 return oid

def polygon(points):return 'M '+' L '.join(f'{x:.6f} {y:.6f}' for x,y in points)+' Z'
front=ET.parse(OUT/'NC03_front_suite_print.svg').getroot();origin=float(front.get('viewBox').split()[0]);children=[]
def walk(e,fill='black'):
 fill=e.get('fill',fill)
 if e.tag.split('}')[-1]=='polygon':
  pts=[tuple(map(float,p.split(','))) for p in e.get('points').split()];color={'white':'255 255 255 255','#111118':'17 17 24 255','#ff08b2':'255 8 178 255'}[fill]
  oid=add_object('FRONT_ART_REFERENCE',polygon([(x-origin,y) for x,y in pts]),color)
  children.append({'obj_id':oid,'transform':'1 0 0 1 0 0'})
  settings['object_settings'].append({'obj_id':oid,'process_type':'KCPrintThenCut'})
 for child in e:walk(child,fill)
walk(front)
frontartid=nextid;nextid+=3
objects.append({'type':'ModelGroup','name':'FRONT_ART_REFERENCE_disable_before_cutting','obj_id':frontartid,'uuid':str(uuid.uuid4()),'flags':['FreeAspectRatio'],'components':list(reversed(children))})
frontcut=ET.parse(OUT/'NC03_front_suite_cut.svg').getroot();poly=next(iter(frontcut));pts=[tuple(map(float,p.split(','))) for p in poly.get('points').split()]
frontcutid=add_object('CUT_FRONT_outer_perimeter',polygon(pts),'255 0 255 0',False)
settings['object_settings'].append({'obj_id':frontcutid,'process_type':'KCBasicCut'})
c['name']='A4_DECK_AND_FRONT_REVIEW_ONLY'
c['components']=[{'obj_id':cut['obj_id'],'transform':'1 0 0 1 5.5 18'}, {'obj_id':frontcutid,'transform':'1 0 0 1 51.5 4'}, {'obj_id':art['obj_id'],'transform':'1 0 0 1 5.5 18'}, {'obj_id':frontartid,'transform':'1 0 0 1 51.5 4'}]
# Add the two side masks, using the exact four-decal PDF layout.
layout=json.loads((OUT/'NC03_all_decals_A4_layout.json').read_text())
for side_name,placement in zip(['left','right'],layout['placements'][2:]):
    before=len(children);front=ET.parse(OUT/f'NC03_side_{side_name}_print.svg').getroot();origin=0
    walk(front);newchildren=children[before:];gid=nextid;nextid+=3
    objects.append({'type':'ModelGroup','name':f'SIDE_{side_name}_ART_REFERENCE','obj_id':gid,'uuid':str(uuid.uuid4()),'flags':['FreeAspectRatio'],'components':list(reversed(newchildren))})
    poly=next(iter(ET.parse(OUT/f'NC03_side_{side_name}_cut.svg').getroot()));points=[tuple(map(float,p.split(','))) for p in poly.get('points').split()]
    cid=add_object(f'CUT_SIDE_{side_name}',polygon(points),'255 0 255 0',False)
    settings['object_settings'].append({'obj_id':cid,'process_type':'KCBasicCut'})
    transform=f'1 0 0 1 {placement[1]} {placement[2]}'
    c['components'].insert(2,{'obj_id':cid,'transform':transform})
    c['components'].append({'obj_id':gid,'transform':transform})
# Keep deck contour above its art; filled single-outline references behind their art.
c['components'].sort(key=lambda item: 0 if item['obj_id']==cut['obj_id'] else (1 if next(o for o in objects if o['obj_id']==item['obj_id'])['type']=='ModelGroup' else 2))
# No precomputed manufacturing plan: this file is strictly the artwork/cut review scene.
# Suite requires at least one saved batch even for a review scene.
# Retain its reference-only setup; do not submit this review project.
data['2D/2dmodel.json']=json.dumps(m).encode();data['Metadata2D/project_settings.json']=json.dumps(s).encode()
entry=json.loads(data['2D/entry.json']);entry['Title']='NC-03 all decals v1.1 / 2026-11-16 / VECTOR REVIEW ONLY';data['2D/entry.json']=json.dumps(entry).encode()
# Remove obsolete manufacturing previews; keep imported native model/config resources.
for name in list(data):
 pass
path=OUT/'NC03_all_decals_v1.1_REVIEW.lac'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
 for name,value in data.items():z.writestr(name,value)
assert len(c['components'])==8
assert len([o for o in objects if o['name'].startswith('CUT_')])==4
print(path)
# Spacious accessory-only review matches page 2 of the A4 print master.
accessory_positions={'FRONT_ART_REFERENCE_disable_before_cutting':(51.5,35),'CUT_FRONT_outer_perimeter':(51.5,35),'SIDE_left_ART_REFERENCE':(25,90),'CUT_SIDE_left':(25,90),'SIDE_right_ART_REFERENCE':(131,135),'CUT_SIDE_right':(131,135)}
byid={o['obj_id']:o for o in objects};roots=[]
for component in c['components']:
 name=byid[component['obj_id']]['name']
 if name in accessory_positions:
  x,y=accessory_positions[name];roots.append({'obj_id':component['obj_id'],'transform':f'1 0 0 1 {x} {y}'})
c['components']=roots;c['name']='A4_FRONT_SIDES_MARGIN_REVIEW_ONLY'
data['2D/2dmodel.json']=json.dumps(m).encode();entry['Title']='NC-03 front + sides v1.1 / 2026-11-16 / MARGIN REVIEW ONLY';data['2D/entry.json']=json.dumps(entry).encode()
path=OUT/'NC03_front_and_sides_A4_REVIEW.lac'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
 for name,value in data.items():z.writestr(name,value)
print(path)
