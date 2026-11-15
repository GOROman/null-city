"""Reference-style front/right view of the actual current lighting-pocket assembly."""
from pathlib import Path
import bpy,sys
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from render_camera import fit_perspective
scene=bpy.context.scene;cam=scene.camera
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
fit_perspective(scene,(360,-760,450),(0,0,31))
scene.render.image_settings.file_format='JPEG';scene.render.filepath=str(root/'docs/images/lighting.jpg')
bpy.ops.render.render(write_still=True)
# Show the actual printable pockets without emissive lenses or the deck hiding the interior.
for obj in scene.objects:
    if obj.type in ('MESH','CURVE','FONT'):
        obj.hide_render=obj.name not in ['PRINT_01_lower_tray','PRINT_USB_bridge_1','PRINT_USB_bridge_2','STUDIO_floor']
fit_perspective(scene,(360,-760,600),(0,0,12))
scene.render.filepath=str(root/'docs/images/lighting-open.jpg')
bpy.ops.render.render(write_still=True)
