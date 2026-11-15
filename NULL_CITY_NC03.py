import bpy, math, os
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
OUT=os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
def mat(n,c,metal=0,rough=.35):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
ivory=mat('Pearl white PETG',(.85,.86,.92));navy=mat('Deep navy',(.012,.019,.075));green=mat('Lime green',(.05,.95,.025));clear=mat('Transparent button placeholder',(.65,.8,.95));purple=mat('Purple balltop',(.34,.08,.8),.1,.12);pink=mat('Magenta accent',(.95,.01,.43));black=mat('Black',(.018,.018,.025))
def cube(n,loc,dim,ma=None,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev: mod=o.modifiers.new('Rounded printable edges','BEVEL');mod.width=bev;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 if ma:o.data.materials.append(ma)
 return o
def cyl(n,x,y,z,r,depth,ma=None,verts=64):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=(x,y,z));o=bpy.context.object;o.name=n
 if ma:o.data.materials.append(ma)
 return o
def cut(obj,tool):
 bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('Machined clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.object=tool
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
# 300x190 footprint; z=0..48; panel rises only 4 mm from back to front
# Split body: bottom tray + upper rim + removable 4 mm top plate.
base=cube('PRINT_01_lower_tray',(0,0,13),(300,190,26),ivory,4)
cut(base,cube('cavity',(0,0,17),(288,178,24))) # 6 mm bottom, 6 mm walls
rim=cube('PRINT_02_upper_frame',(0,0,35),(300,190,18),ivory,3)
cut(rim,cube('frame opening',(0,0,35),(284,174,22)))
panel=cube('PRINT_03_control_panel',(0,0,45),(294,184,4),navy,2)
# 3 active action buttons in exact triangular orientation, plus 3 optional transparent placeholders.
buttons=[(-2,-29),(12,23),(57,33)]
blanks=[(45,-27),(98,-26),(103,27)]
for i,(x,y) in enumerate(buttons+blanks):
 cut(panel,cyl('button hole',x,y,45,15.2,10))
 # detachable visual caps; real arcade switches should replace these
 cap=cyl(('PRINT_04_green_cap_' if i<3 else 'PRINT_05_clear_cap_')+str(i+1),x,y,50,14.4,6,green if i<3 else clear)
 bevel=cap.modifiers.new('Soft button top','BEVEL');bevel.width=1.1;bevel.segments=3
# Lever mounting aperture: nominal 24 mm shaft hole; mounting pattern hardware-dependent
cut(panel,cyl('lever hole',-91,-3,45,12,10))
cyl('VISUAL_joystick_shaft',-91,-3,59,5,26,black)
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=17,location=(-91,-3,83));bpy.context.object.name='VISUAL_purple_balltop';bpy.context.object.data.materials.append(purple)
# 1P and START: small separate buttons
for i,(x,y) in enumerate([(108,57),(108,-58)]):
 cut(panel,cyl('menu hole',x,y,45,6.2,10));cyl('PRINT_06_'+('1P' if i==0 else 'START')+'_cap',x,y,49,5.7,5,green)
# M3 through holes in top and rim, coordinates kept away from panel edges
for x in [-139,139]:
 for y in [-84,84]:
  cut(panel,cyl('M3 clearance',x,y,45,1.7,12))
  cut(rim,cyl('M3 frame clearance',x,y,35,1.7,25))
# LED strips / decals are visual separate pieces; do not require support
cube('VISUAL_front_magenta_light',(0,-95,19),(210,1.5,4),pink,.6)
cube('VISUAL_front_nameplate',(0,-95.8,24),(150,1,10),black,1)
# small feet printable TPU
for i,x in enumerate([-113,113]):
 for j,y in enumerate([-66,66]):cyl('PRINT_07_TPU_foot_%d_%d'%(i,j),x,y,-2,11,4,black)
# camera and light
world=bpy.context.scene.world;world.color=(.14,.14,.14)
bpy.ops.object.camera_add(location=(420,-530,350));camera=bpy.context.object;direction=Vector((0,0,30))-camera.location;camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();camera.data.clip_end=2000;camera.data.type='ORTHO';camera.data.ortho_scale=410;bpy.context.scene.camera=camera
bpy.ops.object.light_add(type='AREA',location=(0,-200,450));bpy.context.object.data.energy=850;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=450
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1400;scene.render.resolution_y=950;scene.render.resolution_percentage=100
# export independent printable mesh components (not visual reference geometry)
exportdir=os.path.join(OUT,'STL');os.makedirs(exportdir,exist_ok=True)
for o in list(bpy.data.objects):
 if not o.name.startswith('PRINT_'):continue
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.wm.stl_export(filepath=os.path.join(exportdir,o.name+'.stl'),export_selected_objects=True,apply_modifiers=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'NULL_CITY_NC03.blend'))
