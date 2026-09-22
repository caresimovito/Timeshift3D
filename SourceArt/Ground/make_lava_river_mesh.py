"""Headless Blender: lava surface mesh for the Zone 4 lava rivers (from lava_river_mask.npy, 50 cm grid, z -135 cm).
Edges sit under the channel banks. World-space. Exports SM_LavaRiver.fbx next to this file."""
import bpy, bmesh, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
m = np.load(os.path.join(HERE, '..', 'Landscape', 'lava_river_mask.npy'))
NY, NX = m.shape
# 1 m cells: a cell is water if any of its four 50 cm samples is
mc = m
H, W = mc.shape
X0, Y0, STEP, Z = -3000.0, -12600.0, 50.0, -135.0
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
me = bpy.data.meshes.new('SM_LavaRiver'); bm.to_mesh(me); bm.free()
o = bpy.data.objects.new('SM_LavaRiver', me); bpy.context.collection.objects.link(o)
me.materials.append(bpy.data.materials.new('M_LavaRiver'))
bpy.ops.export_scene.fbx(filepath=os.path.join(HERE, 'SM_LavaRiver.fbx'), use_selection=False,
                         object_types={'MESH'}, global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE')
print('LAVAMESH quads', n)
