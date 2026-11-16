"""Export the current Blender assembly as a PBR GLB with a scrub-able assembly animation.

Run: blender -b NULL_CITY_NC03.blend --python-exit-code 1 -P scripts/export_web_model.py
"""
from pathlib import Path
import bpy
import hashlib
import json
import struct
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
out=root/'web/public/model';out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
scene.render.fps=24;scene.frame_start=1;scene.frame_end=25
geometry=[o for o in scene.objects if o.type in ('MESH','CURVE','FONT') and o.name!='STUDIO_floor']
assert len([o for o in geometry if o.name.startswith('PRINT_')])==20

def displacement(name):
    if 'upper_frame' in name:return (0,0,32)
    if name.startswith('PRINT_USB_bridge'):return (0,0,13)
    if name.startswith('PRINT_TPU'):return (0,0,-12)
    if name=='PRINT_light_front_diffuser' or name.startswith(('VISUAL_front_mask','VISUAL_NULL_CITY_wordmark','VISUAL_front_slash')):return (0,-22,0)
    if name=='PRINT_light_left_diffuser':return (-22,0,0)
    if name=='PRINT_light_right_diffuser':return (22,0,0)
    if 'control_panel' in name or name.startswith(('VISUAL_LED','VISUAL_switch','VISUAL_menu','VISUAL_shaft','VISUAL_dust','VISUAL_purple','VISUAL_M3','PRINT_button','PRINT_menu')):return (0,0,70)
    return (0,0,0)

bpy.ops.object.select_all(action='DESELECT')
for obj in geometry:
    obj.select_set(True)
    start=obj.location.copy();delta=Vector(displacement(obj.name))
    if delta.length:
        obj.location=start;obj.keyframe_insert(data_path='location',frame=1)
        obj.location=start+delta;obj.keyframe_insert(data_path='location',frame=25)
    obj['part_name']=obj.name
scene.frame_set(1)
bpy.context.view_layer.update()
path=out/'nc03.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,
    export_apply=True,export_yup=True,export_extras=True,export_animations=True,
    export_animation_mode='SCENE',export_frame_range=True,export_frame_step=1,
    export_bake_animation=True,export_copyright='Copyright 2026 GOROman; CC BY 4.0. See https://github.com/GOROman/null-city/blob/main/LICENSE')
# A stable public animation name keeps the viewer independent of Blender's scene naming.
raw=path.read_bytes();length,kind=struct.unpack_from('<II',raw,12)
assert kind==0x4E4F534A
doc=json.loads(raw[20:20+length])
assert doc.get('animations'),'Missing assembly movement'
merged={'name':'Assembly','channels':[],'samplers':[]}
for animation in doc['animations']:
    offset=len(merged['samplers']);merged['samplers'].extend(animation['samplers'])
    for channel in animation['channels']:
        channel['sampler']+=offset;merged['channels'].append(channel)
doc['animations']=[merged]
# Blender's exporter leaves mesh and translation values in mm; one root converts both to glTF meters.
for scene_doc in doc['scenes']:
    index=len(doc['nodes']);doc['nodes'].append({'name':'NULL_CITY_meters','scale':[.001,.001,.001],'children':scene_doc['nodes']})
    scene_doc['nodes']=[index]
# Milk-white diffuser at rest; the separate pink emissive channel represents LEDs.
for material in doc.get('materials',[]):
    if material.get('name')=='Backlit translucent PLA illustration':
        material['pbrMetallicRoughness']['baseColorFactor']=[.82,.84,.88,1]
doc['asset']['extras']={'project':'NULL CITY NC-03','units':'meters','lighting':'illustration; hardware validation pending'}
data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4)
rest=raw[20+length:]
path.write_bytes(struct.pack('<III',0x46546C67,2,20+len(data)+len(rest))+struct.pack('<II',len(data),0x4E4F534A)+data+rest)
inputs=['NULL_CITY_NC03.blend','NULL_CITY_NC03.py','artwork/lighting_layout.json',
        'artwork/control_layout.json','artwork/led_layout.json','artwork/logo/wordmark.json',
        'artwork/panel.png','scripts/panel_features.py','artwork/usb_relief.json','scripts/usb_relief.py','scripts/export_web_model.py']
manifest={'name':'NULL CITY NC-03','license':'CC-BY-4.0','geometry_count':len(geometry),
          'print_part_count':20,'dimensions_mm':[300,190,55],
          'inputs':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in inputs},
          'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Exported',len(geometry),'objects;',path.stat().st_size,'bytes; PBR materials and Assembly animation')
