"""Validate the assembled Blender file: holes, connected solids, and hardware/lens clearance."""
from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1]
c=json.loads((root/'artwork/control_layout.json').read_text());leds=json.loads((root/'artwork/led_layout.json').read_text())['leds']
parts=[o for o in bpy.data.objects if o.name.startswith('PRINT_')]
assert len(parts)==19,len(parts)
for obj in parts:
 bm=bmesh.new();bm.from_mesh(obj.data)
 assert all(e.is_manifold for e in bm.edges),obj.name+' is not manifold'
 assert bm.calc_volume(signed=True)>0,obj.name+' has reversed volume'
 seen=set();components=0
 for vertex in bm.verts:
  if vertex in seen:continue
  components+=1;stack=[vertex];seen.add(vertex)
  while stack:
   for edge in stack.pop().link_edges:
    for neighbour in edge.verts:
     if neighbour not in seen:seen.add(neighbour);stack.append(neighbour)
 assert components==1,(obj.name,components)
 bm.free()
# Every through-hole must exist in BOTH deck layers.
x,y=c['lever'];mount=c['lever_mount']
holes=[c['lever'],*c['buttons'],*c['menu_buttons'],*[(l['x'],l['y']) for l in leds]]
holes += [(x+dx,y+dy) for dx in (-mount['pitch_mm'][0]/2,mount['pitch_mm'][0]/2) for dy in (-mount['pitch_mm'][1]/2,mount['pitch_mm'][1]/2)]
holes += [(x,y) for x in (-135,135) for y in (-80,80)]
assert len(holes)==33
for name in ('PRINT_03_mounting_plate','PRINT_04_top_panel'):
 obj=bpy.data.objects[name]
 assert all(not obj.ray_cast(Vector((px,py,60)),Vector((0,0,-1)),distance=60)[0] for px,py in holes),name
# A rotated MS plate must clear purchased button bodies, not only the drilled holes.
w,d,_=mount['plate_size_mm']
for bx,by in c['buttons']:
 distance=math.hypot(max(abs(bx-x)-w/2,0),max(abs(by-y)-d/2,0))
 assert distance>17.5,(bx,by,'button nut intersects MS plate')
def bvh(obj):
 bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world);tree=BVHTree.FromBMesh(bm);bm.free();return tree
base=bpy.data.objects['PRINT_01_lower_tray'];base_tree=bvh(base)
for name in ('PRINT_light_front_diffuser','PRINT_light_left_diffuser','PRINT_light_right_diffuser'):
 assert not bvh(bpy.data.objects[name]).overlap(base_tree),name+' intersects case'
# Wire passages and the retained backing wall are measured against the actual boolean mesh.
for px in (-90,90):assert not base.ray_cast(Vector((px,-100,13.5)),Vector((0,1,0)),distance=20)[0]
slope=math.tan(math.radians(2.55))
for sign in (-1,1):
 for py in (-64,64):assert not base.ray_cast(Vector((sign*155,py,13.5+slope*py)),Vector((-sign,0,0)),distance=20)[0]
for start,direction in [((0,-100,11),(0,1,0)),((155,0,11),(-1,0,0)),((-155,0,11),(1,0,0))]:
 direction=Vector(direction);hit,first,_,_=base.ray_cast(Vector(start),direction,distance=20);assert hit
 hit,second,_,_=base.ray_cast(first+direction*.001,direction,distance=10);assert hit
 assert abs((second-first).length-1.4)<.01,(first,second)
for px in (-135,135):
 for py in (-80,80):
  hit,point,_,_=base.ray_cast(Vector((px,py,25)),Vector((0,0,-1)),distance=20)
  assert hit and abs(point.z-16.5)<.001,point
print('PASS: 19 connected manifold solids, 33 bores per deck layer, MS-to-button clearance, 3 lens clearances, 6 wire passages, 1.4 mm backing walls, 7.5 mm insert pilots')
