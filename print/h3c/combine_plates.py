from pathlib import Path
import zipfile,json,xml.etree.ElementTree as E,uuid
out=Path(__file__).resolve().parent
C='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';P='http://schemas.microsoft.com/3dmanufacturing/production/2015/06';R='http://schemas.openxmlformats.org/package/2006/relationships'
E.register_namespace('',C);E.register_namespace('p',P)
files=['01_lower_tray','02_upper_frame','03_control_panel','04_caps','05_TPU_feet','06_light_diffusers']
names=['01 Lower tray - PLA','02 Upper frame - PLA','03 Control panel - PLA','04 Caps - PLA','05 Feet - TPU','06 Diffusers - translucent PLA']
with zipfile.ZipFile(out/(files[0]+'.3mf')) as z:
 model=E.fromstring(z.read('3D/3dmodel.model'));settings=json.loads(z.read('Metadata/project_settings.config'));types=z.read('[Content_Types].xml');rootrels=z.read('_rels/.rels')
res=model.find('{'+C+'}resources');res.clear();build=model.find('{'+C+'}build');build.clear();build.set('{'+P+'}UUID',str(uuid.uuid4()))
config=E.Element('config');rels=E.Element('Relationships',xmlns=R);entries={}
with zipfile.ZipFile(out/(files[4]+'.3mf')) as z:tsettings=json.loads(z.read('Metadata/project_settings.config'))
with zipfile.ZipFile(out/(files[5]+'.3mf')) as z:dsettings=json.loads(z.read('Metadata/project_settings.config'))
filament=json.loads((out/'tpu.json').read_text())
for k in set(filament)|{'filament_settings_id','filament_ids','filament_colour','filament_is_support','filament_vendor','filament_type'}:
 if isinstance(settings.get(k),list) and isinstance(tsettings.get(k),list):settings[k]=settings[k]+tsettings[k]+dsettings.get(k,settings[k])

for k in ['filament_map_2','filament_nozzle_map','filament_volume_map','filament_diameter_map']:
 if isinstance(settings.get(k),list): settings[k]=settings[k]*3
settings['flush_volumes_matrix']=['0' if a==b else '280' for a in range(3) for b in range(3)]
settings['flush_volumes_vector']=['140']*6
settings['filament_self_index']=['1','1','2','2','3','3']
settings['filament_colour']=['#EEEEEE','#333333','#FAFAFA'];settings['filament_map']=['1','1','1']
# Process, three logical filament overrides, then printer overrides.
base_flags=settings.get('different_settings_to_system',['','',''])
settings['different_settings_to_system']=[base_flags[0],base_flags[1],tsettings.get('different_settings_to_system',['','',''])[1],dsettings.get('different_settings_to_system',['','',''])[1],base_flags[-1]]
settings.update(layer_height='0.28',wall_loops='3',sparse_infill_density='10%',top_shell_layers='4',bottom_shell_layers='4',top_shell_thickness='0.8',bottom_shell_thickness='0',sparse_infill_pattern='gyroid')
for i,(filename,name) in enumerate(zip(files,names)):
 offset=i*100
 with zipfile.ZipFile(out/(filename+'.3mf')) as z:
  m=E.fromstring(z.read('3D/3dmodel.model'));cfg=E.fromstring(z.read('Metadata/model_settings.config'))
  for ob in m.find('{'+C+'}resources'):
   ob.set('id',str(int(ob.get('id'))+offset));ob.set('{'+P+'}UUID',str(uuid.uuid4()))
   for component in ob.iter('{'+C+'}component'):
    component.set('objectid',str(int(component.get('objectid'))+offset));component.set('{'+P+'}UUID',str(uuid.uuid4()))
    old=component.get('{'+P+'}path');new=f'/3D/Objects/p{i+1}_'+Path(old).name
    data=E.fromstring(z.read(old.lstrip('/')))
    for node in data.iter('{'+C+'}object'):node.set('id',str(int(node.get('id'))+offset))
    entries[new.lstrip('/')]=E.tostring(data,encoding='utf-8',xml_declaration=True)
    component.set('{'+P+'}path',new)
    E.SubElement(rels,'Relationship',Target=new,Id=f'rel-{len(rels)+1}',Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
   res.append(ob)
  for item in m.find('{'+C+'}build'):
   item.set('objectid',str(int(item.get('objectid'))+offset));item.set('{'+P+'}UUID',str(uuid.uuid4()))
   t=item.get('transform').split();t[9]=str(float(t[9])+(i%3)*396);t[10]=str(float(t[10])-(i//3)*384);item.set('transform',' '.join(t));build.append(item)
  for obj in cfg.findall('object'):
   obj.set('id',str(int(obj.get('id'))+offset))
   for part in obj.findall('part'):part.set('id',str(int(part.get('id'))+offset))
   for meta in obj.findall('metadata'):
    if meta.get('key')=='extruder':meta.set('value','2' if i==4 else ('3' if i==5 else '1'))
   if i==4:
    for k,v in {'sparse_infill_density':'20%','brim_type':'no_brim','layer_height':'0.20'}.items():E.SubElement(obj,'metadata',key=k,value=v)
   if i==5:
    for k,v in {'sparse_infill_density':'100%','sparse_infill_pattern':'zig-zag','brim_type':'no_brim','layer_height':'0.20','top_shell_layers':'3','bottom_shell_layers':'3'}.items():E.SubElement(obj,'metadata',key=k,value=v)
   if i==3:E.SubElement(obj,'metadata',key='brim_type',value='no_brim')
   config.append(obj)
  plate=cfg.find('plate')
  for meta in list(plate.findall('metadata')):
   k=meta.get('key')
   if k in ['gcode_file','thumbnail_file','thumbnail_no_light_file','top_file','pick_file']:plate.remove(meta)
   elif k=='plater_id':meta.set('value',str(i+1))
   elif k=='plater_name':meta.set('value',name)
   elif k=='filament_maps':meta.set('value','1 1 1')
  for instance in plate.findall('model_instance'):
   for meta in instance.findall('metadata'):
    if meta.get('key')=='object_id':meta.set('value',str(int(meta.get('value'))+offset))
    if meta.get('key')=='identify_id':meta.set('value',str(int(meta.get('value'))+i*1000))
  config.append(plate)
E.SubElement(config,'assemble')
entries.update({'3D/3dmodel.model':E.tostring(model,encoding='utf-8',xml_declaration=True),'3D/_rels/3dmodel.model.rels':E.tostring(rels,encoding='utf-8',xml_declaration=True),'Metadata/model_settings.config':E.tostring(config,encoding='utf-8',xml_declaration=True),'Metadata/project_settings.config':json.dumps(settings),'[Content_Types].xml':types,'_rels/.rels':rootrels})
with zipfile.ZipFile(out/'NC03_H3C_6plates_lighting.3mf','w',zipfile.ZIP_DEFLATED) as z:
 for k,v in entries.items():z.writestr(k,v)
print('Created 6 plates, 20 objects (USB bridges on plate 1; translucent diffusers on plate 6)')
