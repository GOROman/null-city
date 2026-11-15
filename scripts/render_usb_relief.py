"""Render the cable route and export a small fit coupon from the current assembly."""
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
out=root/'print/usb-relief';out.mkdir(parents=True,exist_ok=True)
base=bpy.data.objects['PRINT_01_lower_tray']
coupon=base.copy();coupon.data=base.data.copy();bpy.context.collection.objects.link(coupon)
coupon.name='FIT_USB_S_guide'
bpy.ops.mesh.primitive_cube_add(size=1,location=(-25,65,12))
clip=bpy.context.object;clip.dimensions=(80,66,26)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bpy.context.view_layer.objects.active=coupon
mod=coupon.modifiers.new('Test region','BOOLEAN');mod.operation='INTERSECT';mod.object=clip
bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(clip,do_unlink=True)
bm=bmesh.new();bm.from_mesh(coupon.data);assert all(e.is_manifold for e in bm.edges);bm.free()
bpy.ops.object.select_all(action='DESELECT');coupon.select_set(True)
bpy.ops.wm.stl_export(filepath=str(out/'FIT_USB_S_guide.stl'),export_selected_objects=True)
bpy.data.objects.remove(coupon,do_unlink=True)
for obj in bpy.context.scene.objects:
    if obj.type in ('MESH','CURVE','FONT'):
        obj.hide_render=obj.name not in ['PRINT_01_lower_tray','PRINT_USB_bridge_1','PRINT_USB_bridge_2','VISUAL_USB_cable']
for i in (1,2):bpy.data.objects[f'PRINT_USB_bridge_{i}'].location.z+=8
cable=bpy.data.objects['VISUAL_USB_cable']
mat=bpy.data.materials.new('Illustrative blue USB cable');mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.015,.3,.8,1)
cable.data.materials.clear();cable.data.materials.append(mat)
scene=bpy.context.scene;cam=scene.camera;cam.location=(90,-65,180)
cam.rotation_euler=(Vector((-24,65,11))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=145
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.view_settings.exposure=-1.5
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG';scene.render.filepath=str(root/'docs/images/usb-relief.jpg')
bpy.ops.render.render(write_still=True)
print('Exported USB fit coupon and exploded cable-guide view')
