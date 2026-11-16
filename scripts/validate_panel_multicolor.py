"""Check shared-origin colored print volumes, recess depth and native 3MF color-layer schedule."""
from pathlib import Path
import json,struct,zipfile,xml.etree.ElementTree as E,math
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'print/h3c';C='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}';P='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
cfg=json.loads((ROOT/'artwork/led_layout.json').read_text())
def bounds(points):return [[min(v[i] for v in points),max(v[i] for v in points)] for i in range(3)]
def stlpoints(path):
 data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
 return [struct.unpack_from('<3f',data,84+50*i+12+12*j) for i in range(n) for j in range(3)]
original={name:bounds(stlpoints(OUT/'panel_color_meshes'/f'{name}.stl')) for name in ['base','white','magenta']}
for color in ['white','magenta']:
 assert abs(original[color][2][0]-2.8)<1e-4 and abs(original[color][2][1]-3.4)<1e-4
assert original['base'][2]==[0,4]
path=OUT/'03_control_panel_multicolor_sliced.3mf'
with zipfile.ZipFile(path) as z:
 assert z.testzip() is None
 model=E.fromstring(z.read('3D/3dmodel.model'));build=model.find(C+'build');assert len(build)==1,'One assembled deck only'
 components=list(model.find(C+'resources').iter(C+'component'));assert len(components)==3
 def transform(point,t):
  x,y,z=point;return [x*t[i]+y*t[3+i]+z*t[6+i]+t[9+i] for i in range(3)]
 for name,component in zip(['base','white','magenta'],components):
  m=E.fromstring(z.read(component.get(P+'path').lstrip('/')));ob=next(o for o in m.find(C+'resources') if o.get('id')==component.get('objectid'))
  verts=[tuple(float(v.get(k)) for k in ['x','y','z']) for v in ob.find(C+'mesh').find(C+'vertices')]
  t=list(map(float,component.get('transform','1 0 0 0 1 0 0 0 1 0 0 0').split()));actual=bounds([transform(v,t) for v in verts])
  for a,b in zip(actual,original[name]):assert max(abs(a[i]-b[i]) for i in range(2))<1e-3,(name,actual,original[name])
 info=E.fromstring(z.read('Metadata/slice_info.config'));plate=info.find('plate');meta={m.get('key'):m.get('value') for m in plate.findall('metadata')}
 assert meta['outside']=='false' and meta['support_used']=='false'
 assert len(plate.findall('filament'))==3 and all(float(f.get('used_g'))>0 for f in plate.findall('filament'))
 schedule=plate.find('layer_filament_lists')
 assert schedule is not None
 for layers in schedule:
  if len(layers.get('filament_list').split())>1:assert layers.get('layer_ranges')=='14 16',E.tostring(layers)
 s=json.loads(z.read('Metadata/project_settings.config'));assert s['filament_colour']==['#007CBF','#FFFFFF','#ED229D']
 assert s['enable_prime_tower']=='1' and s['layer_height']=='0.2'
 report={'aperture':'4 x 4 mm square','pixel_seat':'9.5 mm PCB pocket / 5.6 mm LED package relief','logo_recess_mm':.6,'one_assembled_object':True,'color_volumes':3,'color_layer_range_zero_based':[14,16],'total_layers':20,'prediction_seconds':int(meta['prediction']),'weight_g':float(meta['weight']),'shared_origin_preserved':True,'physical_fit':'not tested'}
 (OUT/'panel_multicolor_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
