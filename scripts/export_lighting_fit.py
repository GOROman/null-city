"""Export upright pocket sections and flat lens sections for a small push-fit test."""
from pathlib import Path
import bpy
import bmesh
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[1]
out=root/'print/lighting-fit';out.mkdir(parents=True,exist_ok=True)
for side,center,size in [('front',(0,-92,12),(40,14,26)),('right',(147,0,12),(14,40,26))]:
 for kind,source in [('case','PRINT_01_lower_tray'),('lens',f'PRINT_light_{side}_diffuser')]:
  original=bpy.data.objects[source]
  obj=original.copy();obj.data=original.data.copy();bpy.context.collection.objects.link(obj)
  bpy.ops.mesh.primitive_cube_add(size=1,location=center);clip=bpy.context.object;clip.dimensions=size
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  bpy.context.view_layer.objects.active=obj
  mod=obj.modifiers.new('Coupon region','BOOLEAN');mod.operation='INTERSECT';mod.object=clip
  bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(clip,do_unlink=True)
  # Case stays upright like the final print; lens retains its original flat orientation.
  if kind=='case':obj.data.transform(obj.matrix_world)
  obj.matrix_world=Matrix.Identity(4)
  lo=Vector(tuple(min(v.co[k] for v in obj.data.vertices) for k in range(3)))
  hi=Vector(tuple(max(v.co[k] for v in obj.data.vertices) for k in range(3)))
  obj.data.transform(Matrix.Translation((-(lo.x+hi.x)/2,-(lo.y+hi.y)/2,-lo.z)))
  bm=bmesh.new();bm.from_mesh(obj.data)
  assert all(e.is_manifold for e in bm.edges) and bm.calc_volume()>0,(side,kind)
  bm.free()
  bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
  bpy.ops.wm.stl_export(filepath=str(out/f'FIT_light_{side}_{kind}.stl'),export_selected_objects=True)
  bpy.data.objects.remove(obj,do_unlink=True)
print('PASS: four closed lighting-fit sections exported')
