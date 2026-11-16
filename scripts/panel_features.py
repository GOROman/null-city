"""Square serial-LED seats and recessed, co-printed wordmark; original geometry, MIT."""
from pathlib import Path
import json,bpy,bmesh

def prism(name,points,z0,z1,material=None):
 n=len(points);v=[(x,y,z) for z in (z0,z1) for x,y in points]
 # Normalize winding before building a closed, concave polygon extrusion.
 area=sum(points[i][0]*points[(i+1)%n][1]-points[(i+1)%n][0]*points[i][1] for i in range(n))
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 if area<0:faces=[tuple(reversed(f)) for f in faces]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],faces);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
 if material:mesh.materials.append(material)
 return obj

def join(objects,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name=name
 return objects[0]

def add_features(panel,root,cube,cut,boolean,navy,white,pink,led_material):
 root=Path(root);cfg=json.loads((root/'artwork/led_layout.json').read_text());logo=cfg['surface_logo']
 for led in cfg['leds']:
  x,y=led['x'],led['y'];hole=cfg['aperture_size_mm'];seat=cfg['module_seat']
  cut(panel,cube('Square LED aperture '+led['name'],(x,y,45),(hole,hole,12)))
  # PCB registration pocket and deeper clearance for the 5050 LED package.
  cut(panel,cube('LED PCB seat '+led['name'],(x,y,43+seat['pcb_recess_depth_mm']/2-.1),(seat['pcb_size_mm'],seat['pcb_size_mm'],seat['pcb_recess_depth_mm']+.2)))
  cut(panel,cube('LED package relief '+led['name'],(x,y,43+seat['package_recess_depth_mm']/2-.1),(seat['package_size_mm'],seat['package_size_mm'],seat['package_recess_depth_mm']+.2)))
  # A light-window illustration; the electrical LED sits below, in the rear seat.
  cube('VISUAL_LED_'+led['name'],(x,y,46.9),(hole-.3,hole-.3,.15),led_material)
  cube('VISUAL_LED_module_'+led['name'],(x,y,42.8),(9.1,9.1,1.6),navy)
  cube('VISUAL_LED_package_'+led['name'],(x,y,44.4),(5,5,1.6),white)
 # One physical deck, three slicer color volumes. All color polygons touch the base.
 mark=json.loads((root/'artwork/logo/wordmark.json').read_text());scale=logo['letter_height_mm']/mark['height'];x0,y0=logo['origin_mm']
 outlines=[[(x0+x*scale,y0+(mark['height']-y)*scale) for x,y in poly['points']] for poly in mark['polygons']]
 slash=[]
 for i in range(3):
  x=x0+mark['width']*scale+8+i*9;h=logo['letter_height_mm']
  slash.append([(x,y0),(x+5,y0),(x+5+4,y0+h),(x+4,y0+h)])
 ztop=47-logo['recess_depth_mm'];zbottom=ztop-logo['color_thickness_mm'];colors=[]
 for name,polygons,ma in [('white',outlines,white),('magenta',slash,pink)]:
  pieces=[]
  for i,poly in enumerate(polygons):
   cut(panel,prism('Logo recess cutter',poly,zbottom,47.2))
   pieces.append(prism('Logo colored floor',poly,zbottom,ztop,ma))
  colors.append(join(pieces,'COLOR_control_panel_'+name))
 return colors

def finish_panel(panel,colors,root,boolean):
 root=Path(root)
 # Raising the cavity floor gives the exact finished recess without coplanar Boolean unions.
 mesh=panel.data.copy();cfg=json.loads((root/'artwork/led_layout.json').read_text())['surface_logo']
 floor=47-cfg['recess_depth_mm']-cfg['color_thickness_mm']
 for v in mesh.vertices:
  if abs(v.co.z-floor)<1e-4:v.co.z+=cfg['color_thickness_mm']
 mesh.update()
 # Shared origin is essential: individual auto-grounding would destroy the inlay alignment.
 out=root/'print/h3c/panel_color_meshes';out.mkdir(exist_ok=True)
 for obj,name in [(panel,'base'),*[(o,o.name.split('_')[-1]) for o in colors]]:
  cp=obj.copy();cp.data=obj.data.copy();bpy.context.collection.objects.link(cp)
  for v in cp.data.vertices:v.co.z-=43
  bpy.ops.object.select_all(action='DESELECT');cp.select_set(True);bpy.context.view_layer.objects.active=cp
  bpy.ops.wm.stl_export(filepath=str(out/(name+'.stl')),export_selected_objects=True)
  bpy.data.objects.remove(cp,do_unlink=True)
 return mesh
