"""Headless Blender: water surface for the Zone 2 pond that replaced the tar pool.

Covers only the carved basin (SourceArt/Landscape/pond_water_mask.npy, 50 cm landscape cells),
so the shoreline sits under the bank instead of cutting across the grass. Built on a 50 cm grid
in world space at z = -45 cm. Exports SM_MossPondWater.fbx next to this file.
"""
import bpy, bmesh, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
m = np.load(os.path.join(HERE, '..', 'Landscape', 'pond_water_mask.npy'))
H, W = m.shape
X0, Y0, STEP, Z = -3000.0, -12600.0, 50.0, -45.0

bpy.ops.wm.read_homefile(use_empty=True)
bm = bmesh.new()
uv = bm.loops.layers.uv.new('UVMap')
verts = {}


def v(i, j):
    k = (i, j)
    if k not in verts:
        # Blender metres; FBX -> UE flips Y, so store -y
        verts[k] = bm.verts.new(((X0 + i * STEP) / 100.0, -(Y0 + j * STEP) / 100.0, Z / 100.0))
    return verts[k]


n = 0
for j in range(H - 1):
    for i in range(W - 1):
        if m[j, i]:
            bm.faces.new((v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1)))
            n += 1
for f in bm.faces:
    for l in f.loops:
        l[uv].uv = (l.vert.co.x / 4.0, l.vert.co.y / 4.0)
bm.normal_update()
for f in bm.faces:
    if f.normal.z < 0:
        f.normal_flip()
me = bpy.data.meshes.new('SM_MossPondWater')
bm.to_mesh(me)
bm.free()
o = bpy.data.objects.new('SM_MossPondWater', me)
bpy.context.collection.objects.link(o)
me.materials.append(bpy.data.materials.new('M_SwampPond'))
bpy.ops.export_scene.fbx(filepath=os.path.join(HERE, 'SM_MossPondWater.fbx'), use_selection=False,
                         object_types={'MESH'}, global_scale=1.0, apply_unit_scale=True,
                         apply_scale_options='FBX_SCALE_NONE')
print('PONDMESH quads', n)
