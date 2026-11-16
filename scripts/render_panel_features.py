"""Render actual printed top and rear LED pockets from the canonical assembly."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from render_camera import fit_perspective
scene=bpy.context.scene;cam=scene.camera
for o in scene.objects:
 if o.type in ('MESH','CURVE','FONT'):o.hide_render=not(o.name=='PRINT_03_control_panel' or o.name.startswith('COLOR_control_panel') or o.name=='STUDIO_floor')
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='JPEG'
parts=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name!='STUDIO_floor']
fit_perspective(scene,(0,-240,560),(0,0,43),parts,margin=.1)
scene.render.filepath=str(root/'docs/images/panel-multicolor.jpg');bpy.ops.render.render(write_still=True)
scene.render.engine='BLENDER_WORKBENCH';scene.view_settings.view_transform='Standard';scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.8,.82,.86);scene.display.shading.show_cavity=True;scene.display.shading.background_type='WORLD';scene.world.color=(.11,.12,.15)
bpy.data.objects['STUDIO_floor'].hide_render=True
cam.data.type='ORTHO';cam.data.ortho_scale=335;cam.location=(0,0,-450);cam.rotation_euler=(Vector((0,0,43))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(root/'docs/images/panel-rear-led-seats.jpg');bpy.ops.render.render(write_still=True)
