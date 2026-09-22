"""Headless Blender: water surface mesh for the Zone 2 swamp, only over the flooded basin
(SourceArt/Landscape/swamp_water_mask.npy, 50 cm landscape cells), so its edges sit under the banks.
Built on a 1 m grid, world-space, at z = -30 cm. Exports SM_SwampPondWater.fbx next to this file."""
import bpy, bmesh, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
m = np.load(os.path.join(HERE, '..', 'Landscape', 'swamp_water_mask.npy'))
NY, NX = m.shape
# 1 m cells: a cell is water if any of its four 50 cm samples is
mc = m[:NY // 2 * 2, :NX // 2 * 2].reshape(NY // 2, 2, NX // 2, 2).any(axis=(1, 3))
H, W = mc.shape
X0, Y0, STEP, Z = -3000.0, -12600.0, 100.0, -30.0
bpy.ops.wm.read_homefile(use_empty=True)
bm = bmesh.new(); uv = bm.loops.layers.uv.new('UVMap')
verts = {}
def v(i, j):
    k = (i, j)
    if k not in verts:
        # Blender metres; FBX -> UE flips Y, so store -y
        verts[k] = bm.verts.new(((X0 + i * STEP) / 100.0, -(Y0 + j * STEP) / 100.0, Z / 100.0))
    return verts[k]
n = 0
for j in range(H):
    for i in range(W):
        if mc[j, i]:
            f = bm.faces.new((v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1)))
            n += 1
for f in bm.faces:
    for l in f.loops:
        l[uv].uv = (l.vert.co.x / 4.0, l.vert.co.y / 4.0)
bm.normal_update()
for f in bm.faces:
    if f.normal.z < 0: f.normal_flip()
me = bpy.data.meshes.new('SM_SwampPondWater'); bm.to_mesh(me); bm.free()
o = bpy.data.objects.new('SM_SwampPondWater', me); bpy.context.collection.objects.link(o)
me.materials.append(bpy.data.materials.new('M_SwampPond'))
bpy.ops.export_scene.fbx(filepath=os.path.join(HERE, 'SM_SwampPondWater.fbx'), use_selection=False,
                         object_types={'MESH'}, global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE')
print('WATERMESH quads', n)
