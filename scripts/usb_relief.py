"""Printable open S channel, sloped to the existing rear notch, with two flat bridges."""
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector


def path_at(t, cfg):
    r = cfg['planar_centerline_radius_mm']
    a = math.pi*(t if t <= .5 else t-.5)
    if t <= .5:
        x, y = -r+r*math.cos(a), cfg['start_y_mm']-r*math.sin(a)
        tangent = Vector((-math.sin(a), -math.cos(a), 0))
    else:
        x, y = -r-r*math.sin(a), cfg['start_y_mm']-2*r+r*math.cos(a)
        tangent = Vector((-math.cos(a), -math.sin(a), 0))
    z = cfg['front_center_z_mm']+(cfg['rear_center_z_mm']-cfg['front_center_z_mm'])*(1+math.cos(math.pi*t))/2
    return Vector((x, y, z)), Vector((-tangent.y, tangent.x, 0))


def add_usb_relief(base, material, cube, cyl, boolean, cut, root):
    cfg = json.loads((Path(root)/'artwork/usb_relief.json').read_text())
    half = cfg['channel_width_mm']/2
    outer = half+cfg['wall_thickness_mm']
    vertices = []
    count = 97
    for i in range(count):
        p, n = path_at(i/(count-1), cfg)
        profile = [(-outer, 4.8), (outer, 4.8), (outer, p.z+half),
                   (half, p.z+half), (half, p.z-half), (-half, p.z-half),
                   (-half, p.z+half), (-outer, p.z+half)]
        for offset, z in profile:
            v = p+n*offset
            vertices.append((v.x, v.y, z))
    faces = [tuple(reversed(range(8)))]
    for i in range(count-1):
        for j in range(8):
            a = i*8+j
            b = i*8+(j+1)%8
            faces.append((a, b, b+8, a+8))
    faces.append(tuple(range((count-1)*8, count*8)))
    mesh = bpy.data.meshes.new('S channel mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    # Recalculate outward normals on the swept U-shaped solid.
    import bmesh
    bm = bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh); bm.free()
    guide = bpy.data.objects.new('USB S channel', mesh)
    bpy.context.collection.objects.link(guide)
    guide.data.materials.append(material)
    boolean(base, guide, 'UNION')
    bridges = []
    for index, station in enumerate(cfg['bridge_stations'], 1):
        p, n = path_at(station, cfg)
        underside = p.z+cfg['bridge_height_offsets_mm'][index-1]
        bridge = cube(f'PRINT_USB_bridge_{index}', (p.x, p.y, underside+1), cfg['bridge_size_mm'], material)
        bridge.rotation_euler.z = math.atan2(n.y, n.x)
        for sign in (-1, 1):
            center = p+n*sign*cfg['bridge_screw_pitch_mm']/2
            boss = cyl('USB insert boss', center.x, center.y, (4.8+underside)/2, 4.4, underside-4.8, material)
            boolean(base, boss, 'UNION')
            arm_center = p+n*sign*6.5
            web_top = underside-.4  # avoid coincident boss/web top faces in boolean unions
            arm = cube('USB boss web', (arm_center.x, arm_center.y, (4.8+web_top)/2), (7, 8, web_top-4.8), material)
            arm.rotation_euler.z = math.atan2(n.y, n.x)
            boolean(base, arm, 'UNION')
            cut(base, cyl('USB insert pilot', center.x, center.y, underside-2.15, cfg['insert_pilot_diameter_mm']/2, 4.7))
            cut(bridge, cyl('USB bridge screw clearance', center.x, center.y, underside+1, cfg['bridge_clearance_hole_mm']/2, 5))
        bridges.append(bridge)
    # Illustrative cable only; it is not included in STL/3MF exports.
    curve = bpy.data.curves.new('USB cable path', 'CURVE')
    curve.dimensions = '3D'; curve.bevel_depth = cfg['nominal_cable_diameter_mm']/2
    curve.bevel_resolution = 4; curve.use_fill_caps = True
    spline = curve.splines.new('POLY'); spline.points.add(count-1)
    for i, point in enumerate(spline.points):
        p, _ = path_at(i/(count-1), cfg); point.co = (*p, 1)
    cable = bpy.data.objects.new('VISUAL_USB_cable', curve)
    bpy.context.collection.objects.link(cable)
    cable.data.materials.append(material)
    return bridges
