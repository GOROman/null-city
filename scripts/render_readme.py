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
# Show front and side illumination together.
saved_camera=cam.matrix_world.copy();saved_scale=cam.data.ortho_scale
cam.location=(420,-510,300);cam.data.ortho_scale=425;aim((0,0,24))
render('docs/images/lighting.jpg')
cam.matrix_world=saved_camera;cam.data.ortho_scale=saved_scale
# Exploded assembly: preserve each group's shared transform.
for o in parts:
 if o.name.startswith('PRINT_TPU'):o.location.z-=20
 elif o.name.startswith('PRINT_light_front'):o.location.y-=25
 elif o.name.startswith('PRINT_light_left'):o.location.x-=25
 elif o.name.startswith('PRINT_light_right'):o.location.x+=25
 elif 'upper_frame' in o.name:o.location.z+=34
 elif 'mounting_plate' in o.name:o.location.z+=65
 elif 'top_panel' in o.name:o.location.z+=230;o.location.y+=30
 elif o.name.startswith(('VISUAL_LED','VISUAL_switch','VISUAL_shaft','VISUAL_dust','VISUAL_purple','VISUAL_M3','PRINT_button','PRINT_menu')):o.location.z+=100
cam.location=(90,-650,550);cam.data.ortho_scale=680;aim((0,0,140))
floor=bpy.data.objects['STUDIO_floor'];floor.hide_render=True
render('assembly.jpg')
# Self-contained vector callouts keep the assembly reference readable on GitHub.
import base64
from bpy_extras.object_utils import world_to_camera_view
jpg=base64.b64encode(open(os.path.join(root,'assembly.jpg'),'rb').read()).decode()
labels=[('PRINT_04_top_panel','装飾トップパネル','1 mm / 印刷部品＋デカール',90),('PRINT_button_cap_00','操作部','メインφ30×6 / 1P・START φ24×2',200),('PRINT_03_mounting_plate','取付プレート','3 mm / レバー・ボタン・LED穴',315),('PRINT_02_upper_frame','上ケース','M3で天板と下ケースを締結',435),('PRINT_01_lower_tray','下ケース','LED溝・配線穴 / M3インサート×4',555),('PRINT_light_front_diffuser','乳白ライトカバー','前面×1・左右×各1 / 1.2 mm',690),('PRINT_TPU_foot_113_-66','TPU脚','4個 / 貼付固定',815)]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1900" height="900" viewBox="0 0 1900 900"><rect width="1900" height="900" fill="#242532"/>',f'<image href="data:image/jpeg;base64,{jpg}" width="1400" height="900"/>']
for name,title,detail,row in labels:
 o=bpy.data.objects.get(name)
 if not o:continue
 points=[world_to_camera_view(scene,cam,o.matrix_world@Vector(v)) for v in o.bound_box]
 v=max(points,key=lambda p:p.x);px=v.x*1400;py=(1-v.y)*900
 svg += [f'<path d="M{px:.1f},{py:.1f} L1425,{row} H1460" fill="none" stroke="#ba90df" stroke-width="2"/>',f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="#f24fc8"/>',f'<text x="1475" y="{row-5}" fill="white" font-size="25" font-family="sans-serif">{title}</text>',f'<text x="1475" y="{row+27}" fill="#cbd0e4" font-size="17" font-family="sans-serif">{detail}</text>']
svg.append('</svg>')
open(os.path.join(root,'docs/images/assembly-labeled.svg'),'w').write(''.join(svg))
floor.hide_render=False
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
 if o.name in ['PRINT_01_lower_tray','PRINT_02_upper_frame','PRINT_03_mounting_plate','PRINT_04_top_panel']:
  o.hide_render=False;o.matrix_world=original[o.name]
  if 'upper_frame' in o.name:o.location.z+=34
  if 'mounting_plate' in o.name:o.location.z+=65
  if 'top_panel' in o.name:o.location.z+=96
  mod=o.modifiers.new('Display mesh edges','WIREFRAME');mod.thickness=.4;mod.use_replace=True
cam.location=(120,-540,460);cam.data.ortho_scale=450;aim((0,0,80))
render('docs/images/wireframe.jpg')
