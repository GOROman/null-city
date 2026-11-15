import bpy, os, json
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
OUT=os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
def mat(n,c,metal=0,rough=.35):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
ivory=mat('Pearl white PETG',(.85,.86,.92));navy=mat('Deep navy',(.012,.019,.075));green=mat('Lime green',(.018,.72,.001));clear=mat('Transparent button placeholder',(.65,.8,.95));purple=mat('Purple balltop',(.26,.015,.72),.1,.12);pink=mat('Magenta accent',(.95,.01,.43));black=mat('Black',(.018,.018,.025))
def cube(n,loc,dim,ma=None,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev: mod=o.modifiers.new('Rounded printable edges','BEVEL');mod.width=bev;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 if ma:o.data.materials.append(ma)
 return o
def cyl(n,x,y,z,r,depth,ma=None,verts=64):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=(x,y,z));o=bpy.context.object;o.name=n
 if ma:o.data.materials.append(ma)
 return o
def boolean(obj,tool,operation):
 bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('Machined clearance','BOOLEAN');mod.operation=operation;mod.object=tool
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
def cut(obj,tool):
 boolean(obj,tool,'DIFFERENCE')
def bake(obj):
 bpy.context.view_layer.objects.active=obj
 for modifier in list(obj.modifiers):
  bpy.ops.object.modifier_apply(modifier=modifier.name)
# Octagonal perimeter, with independent inset rings for the lower and upper bevels.
def shell(name, levels, material):
 vertices=[]
 for z,w,d,c in levels:
  x,y=w/2,d/2
  vertices.extend([(u,v,z) for u,v in [(-x+c,-y),(x-c,-y),(x,-y+c),(x,y-c),(x-c,y),(-x+c,y),(-x,y-c),(-x,-y+c)]])
 faces=[tuple(reversed(range(8)))]
 for k in range(len(levels)-1):
  for j in range(8):
   a=k*8+j;b=k*8+(j+1)%8
   faces.append((a,b,b+8,a+8))
 faces.append(tuple(range(len(vertices)-8,len(vertices))))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
 obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(material)
 return obj

def front_prism(name,outline,y0,y1,material):
 # outline is counterclockwise in X,Z; positive face normal is toward the front.
 v=[(x,y,z) for y in (y0,y1) for x,z in outline];n=len(outline)
 faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]
 for i in range(n):
  j=(i+1)%n;faces.append((j,i,i+n,j+n))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],faces);mesh.update()
 obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(material)
 return obj

def polish(obj):
 for face in obj.data.polygons:
  if abs(face.normal.z)<.98:face.use_smooth=True

base=shell('PRINT_01_lower_tray',[(0,290,180,7),(3,298,188,8),(5,300,190,8),(24,300,190,8)],ivory)
cut(base,cube('Lower cavity',(0,0,17),(288,178,24)))
# Rear cable notch opens at the split line so the USB plug need not pass through.
# 8 mm wide x 6 mm deep below Z=24; rear wall is Y=89..95.
cut(base,cube('USB cable exit notch',(0,94,22),(8,16,8)))
rim=shell('PRINT_02_upper_frame',[(24,300,190,8),(38,300,190,8),(43,292,182,6)],ivory)
cut(rim,cube('Upper opening',(0,0,34),(274,164,28)))
panel=shell('PRINT_03_control_panel',[(43,288,178,5),(46.5,288,178,5),(47,287,177,5)],navy)

# Recess remains within the solid front wall; the light and lettering are display geometry.
recess=[(-102,5),(102,5),(90,22),(-90,22)]
cut(base,front_prism('front pocket',recess,-97,-91.8,black))
front_prism('VISUAL_smoked_front_window',[(-101.2,5.4),(101.2,5.4),(89.6,21.6),(-89.6,21.6)],-92.2,-91.9,black)
def emission(name,color,strength):
 m=mat(name,color);bs=m.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=strength
 return m
lightbar=emission('Magenta light guide',(1,.008,.36),5)
front_prism('VISUAL_light_guide',[(-99,5.8),(99,5.8),(97.8,7.8),(-97.8,7.8)],-93,-92.4,lightbar)
from math import radians
def label(body,x,z,material):
 data=bpy.data.curves.new(body,'FONT');data.body=body;data.size=8.5;data.shear=.27
 o=bpy.data.objects.new(body,data);bpy.context.collection.objects.link(o);o.location=(x,-92.65,z);o.rotation_euler.x=radians(90);data.materials.append(material)
# Use the same original outline wordmark as the printed deck, with no font dependency.
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'artwork','logo','wordmark.json')) as f:
 wordmark=json.load(f)
wordmark_material=emission('Cool white lettering',(.65,.82,1),2)
for i,glyph in enumerate(wordmark['polygons']):
 outline=[(-26+x*.064,11+(100-y)*.064) for x,y in glyph['points']]
 area=sum(outline[j][0]*outline[(j+1)%len(outline)][1]-outline[(j+1)%len(outline)][0]*outline[j][1] for j in range(len(outline)))
 if area<0:outline.reverse()
 front_prism('VISUAL_NULL_CITY_wordmark_%02d'%i,outline,-92.7,-92.5,wordmark_material)
label('///',23,10,lightbar)

steel=mat('Polished steel',(.64,.68,.78),.94,.19)
glass=clear;bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=.94;bs.inputs['IOR'].default_value=1.48;bs.inputs['Roughness'].default_value=.12
bs=purple.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=.48;bs.inputs['Coat Weight'].default_value=.65
bs=green.node_tree.nodes.get('Principled BSDF');bs.inputs['Coat Weight'].default_value=.45
def cap(name,x,y,r,material):
 o=cyl(name,x,y,49,r,5,material)
 bevel=o.modifiers.new('Rounded cap lip','BEVEL');bevel.width=1.2;bevel.segments=4
 polish(o)
def bezel(name,x,y,r,material):
 bpy.ops.mesh.primitive_torus_add(location=(x,y,47.9),major_radius=r,minor_radius=1.45,major_segments=80,minor_segments=12)
 o=bpy.context.object;o.name=name;o.data.materials.append(material);polish(o)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'artwork','control_layout.json')) as f:
 control_layout=json.load(f)
buttons=control_layout['buttons']
lever_x,lever_y=control_layout['lever']
for i,(x,y) in enumerate(buttons):
 cut(panel,cyl('button bore',x,y,45,control_layout['main_button_hole_diameter_mm']/2,12))
 m=green if i<3 else glass
 cap('PRINT_button_cap_%02d'%i,x,y,14.1,m);bezel('VISUAL_switch_bezel_%02d'%i,x,y,15.4,m)
# 1P moves 33 mm toward the rear; START retains its original position.
menu_buttons=control_layout['menu_buttons']
for i,(x,y) in enumerate(menu_buttons):
 cut(panel,cyl('menu bore',x,y,45,control_layout['menu_button_hole_diameter_mm']/2,12));cap('PRINT_menu_cap_%d'%i,x,y,11.2,green);bezel('VISUAL_menu_bezel_%d'%i,x,y,12,green)
# Provisional 3 mm discrete indicator LEDs; actual LED hardware is not specified yet.
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'artwork','led_layout.json')) as f:
 led_layout=json.load(f)
led_material=emission('Indicator LED cyan',(.02,.65,1),2)
for led in led_layout['leds']:
 x,y=led['x'],led['y']
 cut(panel,cyl('LED bore '+led['name'],x,y,45,led_layout['hole_diameter_mm']/2,12))
 cyl('VISUAL_LED_'+led['name'],x,y,47.4,1.5,.8,led_material,32)
# Seimitsu LS-55-01 with MS mounting plate, 85 x 40 mm centers.
mount=control_layout['lever_mount']
for dx in (-mount['pitch_mm'][0]/2,mount['pitch_mm'][0]/2):
 for dy in (-mount['pitch_mm'][1]/2,mount['pitch_mm'][1]/2):
  cut(panel,cyl('M4 lever mounting clearance',lever_x+dx,lever_y+dy,45,mount['clearance_diameter_mm']/2,12))
# Clear the 95 x 50 x 1.6 mm plate below 3 mm LED-lead spacers, with 0.5 mm side clearance.
# Extends the upper opening locally without cutting the exterior wall.
cut(rim,cube('MS plate underside clearance',(lever_x,lever_y,40.5),(96,51,8)))
cut(panel,cyl('lever opening',lever_x,lever_y,45,12,12))
cyl('VISUAL_dust_washer',lever_x,lever_y,47.8,18,1.6,black)
cyl('VISUAL_shaft',lever_x,lever_y,59,4.2,24,steel)
bpy.ops.mesh.primitive_uv_sphere_add(segments=72,ring_count=40,radius=14.5,location=(lever_x,lever_y,80))
o=bpy.context.object;o.name='VISUAL_purple_balltop';o.data.materials.append(purple);polish(o)
for x in (-135,135):
 for y in (-80,80):
  for obj,z,depth in [(base,14,20),(rim,33.5,19)]:
   boolean(obj,cyl('corner boss',x,y,z,11,depth),'UNION')
  cut(base,cyl('M3 insert pilot',x,y,21.5,2.05,7))
  cut(rim,cyl('M3 clearance',x,y,33.5,1.7,24));cut(panel,cyl('M3 clearance',x,y,45,1.7,8))
  screw=cyl('VISUAL_M3_button_head',x,y,48,3.25,2,steel)
  cut(screw,cyl('hex socket',x,y,49,1.25,1.8,None,6))
for x in (-113,113):
 for y in (-66,66):cyl('PRINT_TPU_foot_%d_%d'%(x,y),x,y,-2,11,4,black)
# Use planar local coordinates for the exposed deck, preserving physical holes.
texture=mat('Printed NC-03 graphic',(1,1,1),.03,.38)
panel.data.materials.append(texture);texture_index=len(panel.data.materials)-1;uv=panel.data.uv_layers.new(name='Deck artwork')
uv.active_render=True
for face in panel.data.polygons:
 if face.normal.z>.999 and face.center.z>46.9:face.material_index=texture_index
 for li in face.loop_indices:
  v=panel.data.vertices[panel.data.loops[li].vertex_index].co
  uv.data[li].uv=(v.x/288+.5,v.y/178+.5)
img=bpy.data.images.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),'artwork','panel.png'));img.pack()
tex=texture.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img
texture.node_tree.links.new(tex.outputs['Color'],texture.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
# Rotate the deck and its controls together; slope only the upper portion of the frame.
from mathutils import Matrix
tilt=Matrix.Translation((0,0,43)) @ Matrix.Rotation(radians(2.55),4,'X') @ Matrix.Translation((0,0,-43))
for obj in list(bpy.context.scene.objects):
 if obj==rim:
  for v in obj.data.vertices:
   if v.co.z>24.001:
    mix=(v.co.z-24)/19
    v.co=v.co.lerp(tilt @ v.co,min(1,mix))
 elif obj==panel or obj.location.z>=43:
  obj.matrix_world=tilt @ obj.matrix_world
bpy.context.view_layer.update()
def aim(obj,point):obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add(location=(44,-535,389))
camera=bpy.context.object;aim(camera,(0,0,31));camera.data.type='ORTHO';camera.data.ortho_scale=349;camera.data.clip_end=2000;scene.camera=camera
for name,pos,power,size,color in [('Softbox left',(-190,-140,250),1500000,170,(.88,.91,1)),('Front',(130,-200,140),820000,130,(1,.86,.94)),('Violet rim',(100,140,180),1450000,150,(.56,.34,1))]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;aim(o,(0,0,25))
floor=cube('STUDIO_floor',(0,0,-6),(2500,2500,4),mat('Studio graphite',(.022,.023,.036),.25,.32))
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.34,.42,1)
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=False
scene.render.resolution_x=1152;scene.render.resolution_y=730;scene.render.resolution_percentage=100
# Export each component in its local printing orientation, resting at Z=0.
deps=bpy.context.evaluated_depsgraph_get()
exportdir=os.path.join(OUT,'STL');os.makedirs(exportdir,exist_ok=True)
for obj in list(scene.objects):
 if not obj.name.startswith('PRINT_'):continue
 mesh=bpy.data.meshes.new_from_object(obj.evaluated_get(deps))
 mesh.transform(Matrix.Translation((0,0,-min(v.co.z for v in mesh.vertices))))
 temp=bpy.data.objects.new('Temporary export',mesh);scene.collection.objects.link(temp)
 bpy.ops.object.select_all(action='DESELECT');temp.select_set(True);bpy.context.view_layer.objects.active=temp
 bpy.ops.wm.stl_export(filepath=os.path.join(exportdir,obj.name+'.stl'),export_selected_objects=True)
 bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(mesh)
bpy.ops.object.select_all(action='DESELECT');scene.render.image_settings.file_format='JPEG';scene.render.filepath='//preview.jpg'
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.clip_end=2500
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'NULL_CITY_NC03.blend'),compress=True)
