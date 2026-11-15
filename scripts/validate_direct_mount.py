"""Run in Blender against the regenerated .blend to validate printable geometry."""
from pathlib import Path
import json
import math
import bpy
import bmesh
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[1]
c = json.loads((root / 'artwork/control_layout.json').read_text())
l = json.loads((root / 'artwork/led_layout.json').read_text())
m = c['lever_mount']
assert m['mounting_mode'] == 'direct_housing' and m['pitch_mm'] == [40, 40]
assert m['spacer_height_mm'] == 0 and m['body_depth_below_panel_underside_mm'] == 28.1
assert m['photo_observation']['coupon_fit_observation']['operation_8_directions_confirmed']
holes = [('lever', *c['lever'], 12)]
x, y = c['lever']
holes += [('mount', x+dx, y+dy, m['clearance_diameter_mm']/2)
          for dx in (-20, 20) for dy in (-20, 20)]
holes += [('main', *p, c['main_button_hole_diameter_mm']/2) for p in c['buttons']]
holes += [('menu', *p, c['menu_button_hole_diameter_mm']/2) for p in c['menu_buttons']]
holes += [(p['name'], p['x'], p['y'], l['hole_diameter_mm']/2) for p in l['leds']]
holes += [('corner', px, py, 1.7) for px in (-135, 135) for py in (-80, 80)]
assert len(holes) == 33
gap = min(math.hypot(a[1]-b[1], a[2]-b[2])-a[3]-b[3]
          for i, a in enumerate(holes) for b in holes[i+1:])
assert gap >= 4.19, gap
parts = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('PRINT_')]
assert len(parts) == 17
for obj in parts:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    assert all(e.is_manifold for e in bm.edges), obj.name
    assert bm.calc_volume() > 0, obj.name
    if obj.name == 'PRINT_03_control_panel':
        # Both outer faces are inset 0.5 mm; maximum outline starts 0.5 mm above/below them.
        for plane in (43, 47):
            face_vertices = [v.co for v in bm.verts if abs(v.co.z-plane) < 1e-4]
            assert face_vertices
            assert abs(max(abs(v.x) for v in face_vertices)-143.5) < 1e-3
            assert abs(max(abs(v.y) for v in face_vertices)-88.5) < 1e-3
        outer = [v.co for v in bm.verts if abs(abs(v.co.x)-144) < 1e-4 or abs(abs(v.co.y)-89) < 1e-4]
        assert abs(min(v.z for v in outer)-43.5) < 1e-3
        assert abs(max(v.z for v in outer)-46.5) < 1e-3
        assert len(bm.verts)-len(bm.edges)+len(bm.faces) == -64  # 33 through holes
        tree = BVHTree.FromBMesh(bm)
        for name, hx, hy, _ in holes:
            assert tree.ray_cast((hx, hy, 60), (0, 0, -1), 30)[0] is None, name
        # Former 40x85 mounting holes must now be solid material.
        for dx in (-20, 20):
            for dy in (-42.5, 42.5):
                assert tree.ray_cast((x+dx, y+dy, 60), (0, 0, -1), 30)[0] is not None
    bm.free()
t = math.radians(2.55)
z = 43-m['body_depth_below_panel_underside_mm']-m['wire_depth_allowance_mm']
lowest = 43+(y-m['clearance_envelope_half_depth_mm'])*math.sin(t)+(z-43)*math.cos(t)
clearance = lowest-5-m['vertical_tolerance_allowance_mm']
assert clearance >= m['required_clearance_mm'], clearance
print(f'PASS: 17 manifold parts; 33 bores; min web {gap:.3f} mm; assumed wired clearance {clearance:.3f} mm')
