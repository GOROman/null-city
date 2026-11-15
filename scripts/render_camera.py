"""Perspective product camera with an explicit focal length and a measured frame margin."""
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

def fit_perspective(scene,location,target,objects=None,lens_mm=70,margin=.08):
    cam=scene.camera;target=Vector(target)
    backward=(Vector(location)-target).normalized()
    cam.rotation_euler=(-backward).to_track_quat('-Z','Y').to_euler()
    cam.data.type='PERSP';cam.data.lens=lens_mm
    cam.data.sensor_width=36;cam.data.sensor_fit='HORIZONTAL'
    cam.data.shift_x=cam.data.shift_y=0
    cam.data.clip_start=.1;cam.data.clip_end=5000
    cam.data.dof.use_dof=False
    bpy.context.view_layer.update()
    deps=bpy.context.evaluated_depsgraph_get()
    if objects is None:
        objects=[o for o in scene.objects if o.type in ('MESH','CURVE','FONT') and not o.hide_render and o.name!='STUDIO_floor']
    points=[]
    for obj in objects:
        evaluated=obj.evaluated_get(deps)
        points.extend(evaluated.matrix_world@Vector(corner) for corner in evaluated.bound_box)
    assert points,'No product bounds to frame'
    rotation=cam.rotation_euler.to_matrix()
    right=rotation@Vector((1,0,0));up=rotation@Vector((0,1,0))
    aspect=(scene.render.resolution_x*scene.render.pixel_aspect_x)/(scene.render.resolution_y*scene.render.pixel_aspect_y)
    tan_h=cam.data.sensor_width/(2*lens_mm);tan_v=tan_h/aspect;q=1-2*margin
    distance=max(max((p-target).dot(backward)+abs((p-target).dot(right))/(q*tan_h),
                     (p-target).dot(backward)+abs((p-target).dot(up))/(q*tan_v)) for p in points)+.1
    cam.location=target+backward*distance
    bpy.context.view_layer.update()
    projected=[world_to_camera_view(scene,cam,p) for p in points]
    assert all(p.z>0 and margin-1e-4<=p.x<=1-margin+1e-4 and margin-1e-4<=p.y<=1-margin+1e-4 for p in projected)
    print(f'Camera: perspective {lens_mm} mm; frame margin >= {margin:.0%}; distance {distance:.1f} mm',flush=True)
