"""Reference-style front/right view of the actual current lighting-pocket assembly."""
from pathlib import Path
import bpy
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;cam=scene.camera
cam.location=(420,-500,280)
cam.rotation_euler=(Vector((0,0,25))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.ortho_scale=395
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG';scene.render.filepath=str(root/'docs/images/lighting.jpg')
bpy.ops.render.render(write_still=True)
# Show the actual printable pockets without emissive lenses or the deck hiding the interior.
for obj in scene.objects:
    if obj.type in ('MESH','CURVE','FONT'):
        obj.hide_render=obj.name not in ['PRINT_01_lower_tray','PRINT_USB_bridge_1','PRINT_USB_bridge_2','STUDIO_floor']
cam.location=(420,-500,390)
cam.rotation_euler=(Vector((0,0,12))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.ortho_scale=405
scene.render.filepath=str(root/'docs/images/lighting-open.jpg')
bpy.ops.render.render(write_still=True)
