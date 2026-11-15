"""Check the three diffuser pockets and wire passages in the current 4 mm-deck assembly."""
import bpy
import bmesh
import math
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

layout=json.loads((Path(__file__).resolve().parents[1]/'artwork/lighting_layout.json').read_text())
for section,a,b,depth in [
    ('front','inner_back','inner_seat',layout['front']['seat_depth_mm']),
    ('front','outer_back','outer_front',layout['front']['outer_depth_mm']-layout['front']['seat_depth_mm']),
    ('side','inner_back','inner_seat',layout['side']['seat_depth_mm']),
    ('side','outer_seat','outer_front',layout['side']['outer_depth_mm']-layout['side']['seat_depth_mm'])]:
    # Roof rises one mm per mm of outward depth: printable 45-degree ceiling.
    assert abs((layout[section][b][2][1]-layout[section][a][2][1])-depth)<1e-6
base=bpy.data.objects['PRINT_01_lower_tray']
def tree(obj):
    bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world)
    result=BVHTree.FromBMesh(bm);bm.free();return result
base_tree=tree(base)
for side in ('front','left','right'):
    obj=bpy.data.objects[f'PRINT_light_{side}_diffuser']
    bm=bmesh.new();bm.from_mesh(obj.data)
    assert all(e.is_manifold for e in bm.edges),side
    assert bm.calc_volume()>0,side
    assert abs(max(v.co.z for v in bm.verts)-1.2)<1e-4
    assert min(v.co.z for v in bm.verts)==0
    bm.free()
    # The seated back face intentionally touches its mechanical shoulder.
    original=obj.matrix_world.copy()
    outward=Vector((0,-1,0)) if side=='front' else Vector((-1 if side=='left' else 1,0,0))
    obj.location+=outward*.02;bpy.context.view_layer.update()
    assert not tree(obj).overlap(base_tree),side+' diffuser intersects case outside seat'
    obj.matrix_world=original;obj.location-=outward*.1;bpy.context.view_layer.update()
    assert tree(obj).overlap(base_tree),side+' has no inward push stop'
    obj.matrix_world=original;bpy.context.view_layer.update()
for obj in bpy.context.scene.objects:
    if obj.name.startswith(('VISUAL_front_LED_strip','VISUAL_side_LED_strip')):
        assert not tree(obj).overlap(base_tree),obj.name+' intersects LED pocket'
for x in (-90,90):
    assert not base.ray_cast(Vector((x,-100,13.5)),Vector((0,1,0)),distance=20)[0]
slope=math.tan(math.radians(2.55))
for sign in (-1,1):
    for y in (-64,64):
        assert not base.ray_cast(Vector((sign*155,y,13.5+slope*y)),Vector((-sign,0,0)),distance=20)[0]
for start,direction in [((0,-100,11),(0,1,0)),((155,0,11),(-1,0,0)),((-155,0,11),(1,0,0))]:
    direction=Vector(direction)
    hit,first,_,_=base.ray_cast(Vector(start),direction,distance=20);assert hit
    hit,second,_,_=base.ray_cast(first+direction*.001,direction,distance=10);assert hit
    assert abs((second-first).length-1.4)<.01,(first,second)
print('PASS: three flat-print 1.2 mm diffusers, seating clearance and inward mechanical stops, six wire passages, 1.4 mm pocket backing walls')
