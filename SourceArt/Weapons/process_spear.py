"""Headless Blender: turn the Meshy spear GLB into SM_Spear.fbx.
Usage: blender -b -P process_spear.py -- <in.glb>
Result: length along +Z (flint head up), 2.0 m long, origin = grip point 0.31 m above the butt."""
import bpy, sys, os
from mathutils import Vector, Matrix

src = sys.argv[sys.argv.index('--') + 1]
out_dir = os.path.dirname(os.path.abspath(__file__))
LENGTH, GRIP_FROM_BUTT, TARGET_TRIS = 2.0, 0.31, 6000

bpy.ops.wm.read_homefile(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for o in bpy.data.objects:
    o.select_set(o in meshes)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
dec = ob.modifiers.new('dec', 'DECIMATE')
dec.ratio = min(1.0, TARGET_TRIS / max(tris, 1))
bpy.ops.object.modifier_apply(modifier='dec')

vs = [v.co.copy() for v in ob.data.vertices]
ext = [max(v[i] for v in vs) - min(v[i] for v in vs) for i in range(3)]
ax = ext.index(max(ext))
lo, hi = min(v[ax] for v in vs), max(v[ax] for v in vs)
def width(sel):
    pts = [v for v in vs if sel(v[ax])]
    others = [i for i in range(3) if i != ax]
    return max(max(p[i] for p in pts) - min(p[i] for p in pts) for i in others)
span = hi - lo
w_hi = width(lambda x: x > hi - 0.15 * span)
w_lo = width(lambda x: x < lo + 0.15 * span)
head_positive = w_hi > w_lo          # the flint head is the wide end
print('SPEAR axis', ax, 'extent', [round(e, 3) for e in ext], 'end widths hi/lo', round(w_hi, 3), round(w_lo, 3))

# rotate so the long axis becomes +Z with the head up
axis_vec = Vector([0, 0, 0]); axis_vec[ax] = 1.0 if head_positive else -1.0
rot = axis_vec.rotation_difference(Vector((0, 0, 1))).to_matrix().to_4x4()
ob.data.transform(rot)
vs = [v.co for v in ob.data.vertices]
zmin, zmax = min(v.z for v in vs), max(v.z for v in vs)
s = LENGTH / (zmax - zmin)
cx = sum(v.x for v in vs) / len(vs); cy = sum(v.y for v in vs) / len(vs)
# centre the shaft on the axis near the grip (use verts in the lower 30% = shaft only)
low = [v for v in vs if v.z < zmin + 0.3 * (zmax - zmin)]
cx = sum(v.x for v in low) / len(low); cy = sum(v.y for v in low) / len(low)
ob.data.transform(Matrix.Translation((-cx, -cy, -zmin)))
ob.data.transform(Matrix.Scale(s, 4))
ob.data.transform(Matrix.Translation((0, 0, -GRIP_FROM_BUTT)))
ob.name = ob.data.name = 'SM_Spear'
for m in ob.data.materials:
    if m: m.name = 'M_Spear'
vs = [v.co for v in ob.data.vertices]
print('SPEAR final z', round(min(v.z for v in vs), 3), round(max(v.z for v in vs), 3),
      'tris', sum(len(p.vertices) - 2 for p in ob.data.polygons))

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, 'Spear.blend'))
bpy.ops.export_scene.fbx(filepath=os.path.join(out_dir, 'SM_Spear.fbx'), use_selection=False,
                         object_types={'MESH'}, mesh_smooth_type='FACE', path_mode='COPY', embed_textures=False)
print('SPEAR exported')
