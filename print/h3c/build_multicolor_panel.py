"""One assembled deck, three co-printed color volumes; no separate assembly pieces (MIT)."""
from pathlib import Path
import json,struct,zipfile,uuid,xml.etree.ElementTree as E,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'print/h3c'
C='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';P='http://schemas.microsoft.com/3dmanufacturing/production/2015/06';R='http://schemas.openxmlformats.org/package/2006/relationships'
E.register_namespace('',C);E.register_namespace('p',P)
def tag(n):return '{'+C+'}'+n
def uid(n):return str(uuid.uuid5(uuid.NAMESPACE_URL,'https://github.com/GOROman/null-city/multicolor/'+n))
with zipfile.ZipFile(OUT/'03_control_panel_fast.3mf') as z:
 settings=json.loads(z.read('Metadata/project_settings.config'));types=z.read('[Content_Types].xml');rootrels=z.read('_rels/.rels')
pla=json.loads((OUT/'pla.json').read_text())
for key in set(pla)|{'filament_settings_id','filament_ids','filament_colour','filament_is_support','filament_vendor','filament_type'}:
 if isinstance(settings.get(key),list):settings[key]*=3
for key in ['filament_map','filament_map_2','filament_nozzle_map','filament_volume_map','filament_diameter_map']:
 if isinstance(settings.get(key),list):settings[key]=settings[key][:1]*3
flags=settings.get('different_settings_to_system',['','',''])
process=set(filter(None,flags[0].split(';')))|{'layer_height','enable_prime_tower','prime_tower_width','top_shell_layers','bottom_shell_layers','wall_loops','sparse_infill_density','brim_width'}
settings['different_settings_to_system']=[';'.join(sorted(process)),flags[1],flags[1],flags[1],flags[-1]]
settings.update(layer_height='0.20',initial_layer_print_height='0.20',wall_loops='3',top_shell_layers='3',bottom_shell_layers='3',sparse_infill_density='5%',top_shell_thickness='0.6',enable_prime_tower='1',prime_tower_width='30')
settings['filament_colour']=['#007CBF','#FFFFFF','#ED229D'];settings['filament_self_index']=['1','1','2','2','3','3']
settings['flush_volumes_matrix']=['0' if a==b else '280' for a in range(3) for b in range(3)];settings['flush_volumes_vector']=['140']*6
model=E.Element(tag('model'),unit='millimeter',attrib={'{http://www.w3.org/XML/1998/namespace}lang':'en-US','requiredextensions':'p'})
E.SubElement(model,tag('metadata'),name='Application').text='BambuStudio-02.09.01.70';E.SubElement(model,tag('metadata'),name='BambuStudio:3mfVersion').text='1'
res=E.SubElement(model,tag('resources'));obj=E.SubElement(res,tag('object'),id='4',type='model',attrib={'{'+P+'}UUID':uid('object')});components=E.SubElement(obj,tag('components'))
build=E.SubElement(model,tag('build'),attrib={'{'+P+'}UUID':uid('build')});E.SubElement(build,tag('item'),objectid='4',printable='1',transform='1 0 0 0 1 0 0 0 1 165 160 0',attrib={'{'+P+'}UUID':uid('item')})
rels=E.Element('Relationships',xmlns=R);config=E.Element('config');co=E.SubElement(config,'object',id='4');E.SubElement(co,'metadata',key='name',value='NC03 ONE-PIECE surface-color deck');E.SubElement(co,'metadata',key='extruder',value='1')
entries={}
for i,name in enumerate(['base','white','magenta'],1):
 raw=(OUT/'panel_color_meshes'/f'{name}.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0];verts=[];faces=[];indices={}
 for f in range(n):
  values=struct.unpack_from('<12fH',raw,84+f*50);tri=[]
  for k in range(3):
   v=tuple(round(a,6) for a in values[3+3*k:6+3*k]);key=indices.setdefault(v,len(indices))
   if key==len(verts):verts.append(v)
   tri.append(key)
  faces.append(tri)
 m=E.Element(tag('model'),unit='millimeter');rr=E.SubElement(m,tag('resources'));o=E.SubElement(rr,tag('object'),id=str(i),type='model');mesh=E.SubElement(o,tag('mesh'));vs=E.SubElement(mesh,tag('vertices'));ts=E.SubElement(mesh,tag('triangles'))
 for x,y,z in verts:E.SubElement(vs,tag('vertex'),x=str(x),y=str(y),z=str(z))
 for a,b,c in faces:E.SubElement(ts,tag('triangle'),v1=str(a),v2=str(b),v3=str(c))
 path=f'/3D/Objects/panel_{name}.model';entries[path[1:]]=E.tostring(m,encoding='utf-8',xml_declaration=True)
 E.SubElement(components,tag('component'),objectid=str(i),transform='1 0 0 0 1 0 0 0 1 0 0 0',attrib={'{'+P+'}path':path,'{'+P+'}UUID':uid(name)})
 E.SubElement(rels,'Relationship',Target=path,Id=f'rel-{i}',Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
 part=E.SubElement(co,'part',id=str(i),subtype='normal_part',uuid=uid(name))
 for key,value in [('name',f'PRINT-IN-PLACE {name}'),('extruder',str(i)),('matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'),('source_file',f'{name}.stl'),('source_object_id','0'),('source_volume_id','0'),('source_offset_x','0'),('source_offset_y','0'),('source_offset_z','0')]:E.SubElement(part,'metadata',key=key,value=value)
 E.SubElement(part,'mesh_stat',face_count=str(n),edges_fixed='0',degenerate_facets='0',facets_removed='0',facets_reversed='0',backwards_edges='0')
plate=E.SubElement(config,'plate')
for k,v in [('plater_id','1'),('plater_name','ONE-PIECE / blue + white + magenta'),('locked','false'),('filament_map_mode','Auto For Flush'),('filament_maps','1 1 1'),('filament_volume_maps','0 0 0')]:E.SubElement(plate,'metadata',key=k,value=v)
mi=E.SubElement(plate,'model_instance')
for k,v in [('object_id','4'),('instance_id','0'),('identify_id','1')]:E.SubElement(mi,'metadata',key=k,value=v)
E.SubElement(config,'assemble')
entries.update({'[Content_Types].xml':types,'_rels/.rels':rootrels,'3D/3dmodel.model':E.tostring(model,encoding='utf-8',xml_declaration=True),'3D/_rels/3dmodel.model.rels':E.tostring(rels,encoding='utf-8',xml_declaration=True),'Metadata/model_settings.config':E.tostring(config,encoding='utf-8',xml_declaration=True),'Metadata/project_settings.config':json.dumps(settings).encode()})
project=OUT/'03_control_panel_multicolor.3mf'
with zipfile.ZipFile(project,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for n,b in entries.items():z.writestr(n,b)
cmd=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--arrange','1','--slice','0','--export-3mf',str(OUT/'03_control_panel_multicolor_sliced.3mf'),str(project)]
with (OUT/'03_control_panel_multicolor_slice.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,cwd=ROOT)
print('Saved one assembled object / three near-surface colors',project)
