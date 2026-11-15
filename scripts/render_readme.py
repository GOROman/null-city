"""Render README assets from the current assembly. Run with Blender -b ... -P."""
import bpy,os
from mathutils import Vector,Matrix
from math import radians
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scene=bpy.context.scene
cam=scene.camera
original={o.name:o.matrix_world.copy() for o in scene.objects}
parts=[o for o in scene.objects if o.type=='MESH' and o.name!='STUDIO_floor']
def aim(point):cam.rotation_euler=(Vector(point)-cam.location).to_track_quat('-Z','Y').to_euler()
def render(path,w=1400,h=900):
 scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='JPEG';scene.render.image_settings.color_mode='RGB';scene.render.filepath=os.path.join(root,path)
 bpy.ops.render.render(write_still=True)
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
render('docs/images/cycles.jpg')
import shutil
shutil.copyfile(os.path.join(root,'docs/images/cycles.jpg'),os.path.join(root,'preview.jpg'))
# Exploded assembly: preserve each group's shared transform.
for o in parts:
 if 'upper_frame' in o.name:o.location.z+=34
 elif 'control_panel' in o.name or o.name.startswith(('VISUAL_LED','VISUAL_switch','VISUAL_shaft','VISUAL_dust','VISUAL_purple','VISUAL_M3','PRINT_button','PRINT_menu')):o.location.z+=72
cam.location=(90,-570,450);cam.data.ortho_scale=420;aim((0,0,65))
render('assembly.jpg')
for o in parts:o.matrix_world=original[o.name]
# Orthographic views at a shared scale in a single scene.
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=True
scene.display.shading.background_type='WORLD';scene.world.color=(.11,.12,.15)
bpy.data.objects['STUDIO_floor'].hide_render=True
copies=[]
transforms=[Matrix.Translation((-110,120,0)),Matrix.Translation((-110,-95,0))@Matrix.Rotation(radians(-90),4,'X'),Matrix.Translation((165,-95,0))@Matrix(((0,1,0,0),(0,0,1,0),(1,0,0,0),(0,0,0,1)))]
for transform in transforms:
 for o in parts:
  c=o.copy();c.data=o.data.copy();scene.collection.objects.link(c);c.matrix_world=transform@original[o.name];copies.append(c)
for o in parts:o.hide_render=True
cam.location=(0,45,1200);cam.rotation_euler=(0,0,0);cam.data.ortho_scale=630
labels=[]
for text,x,y in [('TOP',-250,228),('FRONT',-250,-125),('RIGHT',75,-125)]:
 d=bpy.data.curves.new(text,'FONT');d.body=text;d.size=10;o=bpy.data.objects.new(text,d);scene.collection.objects.link(o);o.location=(x,y,100);labels.append(o)
render('docs/images/three-views.jpg',1800,1100)
for o in copies+labels:bpy.data.objects.remove(o,do_unlink=True)
# Exploded structural mesh, with real opening boundaries visible.
for o in parts:
 if o.name in ['PRINT_01_lower_tray','PRINT_02_upper_frame','PRINT_03_control_panel']:
  o.hide_render=False;o.matrix_world=original[o.name]
  if 'upper_frame' in o.name:o.location.z+=34
  if 'control_panel' in o.name:o.location.z+=72
  mod=o.modifiers.new('Display mesh edges','WIREFRAME');mod.thickness=.4;mod.use_replace=True
cam.location=(120,-540,440);cam.data.ortho_scale=425;aim((0,0,70))
render('docs/images/wireframe.jpg')
