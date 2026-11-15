"""Run with Blender --background --python; diagnostic direct-mount candidate only."""
from pathlib import Path
import bpy
import bmesh
import math

root = Path(__file__).resolve().parents[1]
out = root / 'print' / 'fit'
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2))
panel = bpy.context.object
panel.name = 'FIT_ONLY_direct_40x40'
panel.dimensions = (60, 60, 4)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
holes = [(0, 0, 12)] + [(x, y, 2.25) for x in (-20, 20) for y in (-20, 20)]
for x, y, r in holes:
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=r, depth=10, location=(x, y, 2))
    tool = bpy.context.object
    bpy.context.view_layer.objects.active = panel
    mod = panel.modifiers.new('Through hole', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = tool
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool, do_unlink=True)
bm = bmesh.new()
bm.from_mesh(panel.data)
assert all(e.is_manifold for e in bm.edges)
assert len(bm.verts) - len(bm.edges) + len(bm.faces) == -8  # five through holes
assert abs(bm.calc_volume() - (60*60 - sum(96*r*r*math.sin(2*math.pi/96)/2 for _,_,r in holes))*4) < 0.1
bm.free()
bpy.ops.object.select_all(action='DESELECT')
panel.select_set(True)
bpy.context.view_layer.objects.active = panel
bpy.ops.wm.stl_export(filepath=str(out / (panel.name + '.stl')), export_selected_objects=True)
print('PASS: 60 x 60 x 4 mm, five through holes, manifold; pitch 40 x 40 mm')
