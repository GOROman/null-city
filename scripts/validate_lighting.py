"""Check the three diffuser pockets and wire passages in the current 4 mm-deck assembly."""
import bpy
import bmesh
import math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

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
    assert not tree(obj).overlap(base_tree),side+' diffuser hits case'
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
print('PASS: three flat-print 1.2 mm diffusers, case clearance, six wire passages, 1.4 mm pocket backing walls')
