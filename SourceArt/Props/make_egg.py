"""Headless Blender: a smooth dinosaur egg (egg-shaped profile, slight bumps), 50 cm tall, pivot at the base."""
import bpy, bmesh, math, os, random
bpy.ops.wm.read_homefile(use_empty=True)
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=1.0)
ob = bpy.context.active_object
random.seed(4)
me = ob.data
for v in me.vertices:
    x, y, z = v.co
    k = 1.0 - 0.22 * max(z, 0.0) + 0.06 * min(z, 0.0)       # narrower top, fuller bottom
    bump = 1.0 + 0.012 * math.sin(7 * x + 3 * z) * math.cos(5 * y)
    v.co = (x * k * bump, y * k * bump, z * 1.32)
# 50 cm tall, base at z=0 (Blender metres; FBX exports cm)
zs = [v.co.z for v in me.vertices]
s = 0.5 / (max(zs) - min(zs))
for v in me.vertices:
    v.co = (v.co.x * s, v.co.y * s, (v.co.z - min(zs)) * s)
for p in me.polygons:
    p.use_smooth = True
ob.name = me.name = 'SM_GlowEgg'
mat = bpy.data.materials.new('M_GlowEgg'); me.materials.append(mat)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SM_GlowEgg.fbx')
bpy.ops.export_scene.fbx(filepath=out, use_selection=False, object_types={'MESH'}, mesh_smooth_type='FACE')
print('EGG ok', len(me.vertices))
