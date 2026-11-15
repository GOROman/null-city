"""Blender: derive an optional NULL FONT embossed panel from the current flat assembly."""
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

root = Path(__file__).resolve().parents[1]
out = root / 'print/embossed'
out.mkdir(parents=True, exist_ok=True)
panel = bpy.data.objects['PRINT_03_control_panel']
bpy.ops.object.text_add()
text = bpy.context.object
text.data.body = 'NULL CITY'
text.data.font = bpy.data.fonts.load(str(root / 'fonts/null-font/NULLFont-Italic.ttf'))
text.data.extrude = 0.35
text.data.resolution_u = 12
bpy.ops.object.convert(target='MESH')
text = bpy.context.object
lo = Vector(tuple(min(v.co[k] for v in text.data.vertices) for k in range(3)))
hi = Vector(tuple(max(v.co[k] for v in text.data.vertices) for k in range(3)))
scale = 130 / (hi.x-lo.x)
for v in text.data.vertices:
    v.co.x = (v.co.x-(lo.x+hi.x)/2)*scale+63
    v.co.y = (v.co.y-(lo.y+hi.y)/2)*scale-52.9
    v.co.z += 47.25  # overlap panel by 0.1 mm; top at 47.6
text.matrix_world = panel.matrix_world.copy()
bpy.context.view_layer.objects.active = panel
mod = panel.modifiers.new('NULL FONT raised lettering', 'BOOLEAN')
mod.operation = 'UNION'
mod.object = text
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(text, do_unlink=True)
bm = bmesh.new()
bm.from_mesh(panel.data)
assert all(e.is_manifold for e in bm.edges)
assert len(bm.verts)-len(bm.edges)+len(bm.faces) == -64
assert abs(max(v.co.z for v in bm.verts)-47.6) < 0.001
bm.free()
# Preview in one blue material, matching a single-filament print without a decal.
blue = bpy.data.materials.new('Single blue PLA embossed panel')
blue.diffuse_color = (.015, .25, .65, 1)
blue.use_nodes = True
blue.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = blue.diffuse_color
blue.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .4
panel.data.materials.clear()
panel.data.materials.append(blue)
for face in panel.data.polygons:
    face.material_index = 0
mesh = panel.data.copy()
for v in mesh.vertices:
    v.co.z -= 43
temp = bpy.data.objects.new('Embossed panel export', mesh)
bpy.context.collection.objects.link(temp)
bpy.ops.object.select_all(action='DESELECT')
temp.select_set(True)
bpy.context.view_layer.objects.active = temp
bpy.ops.wm.stl_export(filepath=str(out / 'PRINT_03_control_panel_embossed.stl'), export_selected_objects=True)
bpy.data.objects.remove(temp, do_unlink=True)
bpy.data.meshes.remove(mesh)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 1400
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'JPEG'
scene.render.filepath = str(root / 'docs/images/embossed.jpg')
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'NC03_embossed.blend'), compress=True)
bpy.ops.render.render(write_still=True)
print('PASS: manifold panel, 33 through holes, NULL FONT logo 130 mm wide and 0.6 mm raised')
