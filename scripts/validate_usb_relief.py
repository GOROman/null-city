"""Blender geometry checks for the assumed 4 mm USB cable and retaining bridges."""
from pathlib import Path
import sys
import json
import math
import bpy
import bmesh
from mathutils import Matrix

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'scripts'))
from usb_relief import path_at
cfg = json.loads((root/'artwork/usb_relief.json').read_text())
base = bpy.data.objects['PRINT_01_lower_tray']
bridges = [bpy.data.objects[f'PRINT_USB_bridge_{i}'] for i in (1, 2)]


def intersection(a, b):
    temp = a.copy(); temp.data = a.data.copy()
    bpy.context.collection.objects.link(temp)
    bpy.context.view_layer.objects.active = temp
    mod = temp.modifiers.new('Test overlap', 'BOOLEAN'); mod.operation = 'INTERSECT'; mod.object = b
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bm = bmesh.new(); bm.from_mesh(temp.data)
    volume = abs(bm.calc_volume()); bm.free()
    mesh = temp.data; bpy.data.objects.remove(temp, do_unlink=True); bpy.data.meshes.remove(mesh)
    return volume


for obj in [base, *bridges]:
    bm = bmesh.new(); bm.from_mesh(obj.data)
    assert all(e.is_manifold for e in bm.edges), obj.name
    assert bm.calc_volume() > 0, obj.name
    unseen=set(bm.verts); components=0
    while unseen:
        components+=1; stack=[unseen.pop()]
        while stack:
            vertex=stack.pop()
            for edge in vertex.link_edges:
                other=edge.other_vert(vertex)
                if other in unseen: unseen.remove(other); stack.append(other)
    assert components==1, (obj.name, 'disconnected printable solids', components)
    if obj in bridges:
        assert len(bm.verts)-len(bm.edges)+len(bm.faces) == -2  # two screw holes
        assert intersection(obj, base) < .01, obj.name
        assert intersection(obj, bpy.data.objects['PRINT_02_upper_frame']) < .01, obj.name
    bm.free()

tilt = Matrix.Translation((0,0,43)) @ Matrix.Rotation(math.radians(2.55),4,'X') @ Matrix.Translation((0,0,-43))
bpy.ops.mesh.primitive_cube_add(size=1, location=(-90,18,43-28.1/2))
lever = bpy.context.object; lever.dimensions=(70.5,95,28.1)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
lever.matrix_world=tilt @ lever.matrix_world
for obj in [base,*bridges]:
    assert intersection(obj,lever)<.01, (obj.name,'lever envelope')
bpy.data.objects.remove(lever,do_unlink=True)

cable = bpy.data.objects['VISUAL_USB_cable']
copy = cable.copy(); copy.data = cable.data.copy(); bpy.context.collection.objects.link(copy)
bpy.ops.object.select_all(action='DESELECT'); copy.select_set(True); bpy.context.view_layer.objects.active = copy
bpy.ops.object.convert(target='MESH'); copy = bpy.context.object
assert intersection(copy, base) < .01, 'Assumed 4 mm cable hits guide'
for obj in bridges:
    assert intersection(copy, obj) < .01, 'Retainer crushes assumed cable'
bpy.data.objects.remove(copy, do_unlink=True)

# Conservative button cylinders: include the full drawing depth below panel underside.
controls = json.loads((root/'artwork/control_layout.json').read_text())
for positions, radius, depth in [(controls['buttons'],17.5,34.3),(controls['menu_buttons'],14.2,31.2)]:
    for x, y in positions:
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=radius, depth=depth, location=(x,y,43-depth/2))
        proxy = bpy.context.object; proxy.matrix_world = tilt @ proxy.matrix_world
        for obj in [base, *bridges]:
            assert intersection(obj, proxy) < .01, (obj.name, 'button envelope', x, y)
        bpy.data.objects.remove(proxy, do_unlink=True)

# Sample analytic derivatives, avoiding float32 finite-difference noise at small steps.
radii=[]
for i in range(1001):
    t=i/1000
    if t==.5: continue
    from mathutils import Vector
    r=cfg['planar_centerline_radius_mm']; p=math.pi
    a=p*(t if t<.5 else t-.5)
    dz=-(cfg['rear_center_z_mm']-cfg['front_center_z_mm'])*p*math.sin(p*t)/2
    ddz=-(cfg['rear_center_z_mm']-cfg['front_center_z_mm'])*p*p*math.cos(p*t)/2
    if t<.5:
        velocity=Vector((-r*p*math.sin(a),-r*p*math.cos(a),dz))
        acceleration=Vector((-r*p*p*math.cos(a),r*p*p*math.sin(a),ddz))
    else:
        velocity=Vector((-r*p*math.cos(a),-r*p*math.sin(a),dz))
        acceleration=Vector((r*p*p*math.sin(a),-r*p*p*math.cos(a),ddz))
    curvature=velocity.cross(acceleration).length/(velocity.length**3)
    if curvature:radii.append(1/curvature)
print(f'PASS: USB base/bridges manifold; cable and button clearance; sampled bend radius >= {min(radii):.2f} mm')
