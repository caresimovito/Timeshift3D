# Blender headless: build a shoreline-following water surface from pond_<label>.json (Unreal ground samples).
# Region = low cells (ground below the water surface) flood-filled from the cells under the current water mesh, then grown
# DILATE cells so the outer edge tucks under the rising bank (hidden by the terrain instead of showing a cut edge).
# Output: flat quads at z=0 around the pond centre (cm units), exported as FBX; prints the actor location to use.
import json
import sys
from collections import deque
import bpy

src, out_fbx = sys.argv[sys.argv.index("--") + 1:][:2]
DILATE = 2
_a = sys.argv[sys.argv.index("--") + 1:]
XMIN = float(_a[2]) if len(_a) > 2 else -1e12      # cells west of XMIN ...
YLO = float(_a[3]) if len(_a) > 3 else -1e12       # ... and between YLO..YHI are dry (the old stream bed, behind the bank)
YHI = float(_a[4]) if len(_a) > 4 else 1e12
d = json.load(open(src))
nx, ny, c, surf = d["nx"], d["ny"], d["cell"], d["surf"]
H, IN = d["h"], d["inside"]
idx = lambda i, j: j * nx + i
def _cut(k):
    x, y = d["x0"] + (k % nx) * c, d["y0"] + (k // nx) * c
    return x < XMIN and YLO <= y <= YHI


wet = [H[k] is not None and H[k] < surf and not _cut(k) for k in range(nx * ny)]
reg = [False] * (nx * ny)
q = deque(k for k in range(nx * ny) if wet[k] and IN[k])
for k in q:
    reg[k] = True
while q:
    k = q.popleft()
    i, j = k % nx, k // nx
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = i + di, j + dj
        if 0 <= a < nx and 0 <= b < ny:
            kk = idx(a, b)
            if wet[kk] and not reg[kk]:
                reg[kk] = True
                q.append(kk)
core = sum(reg)
for _ in range(DILATE):
    grow = reg[:]
    for k in range(nx * ny):
        if reg[k]:
            i, j = k % nx, k // nx
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    a, b = i + di, j + dj
                    if 0 <= a < nx and 0 <= b < ny:
                        grow[idx(a, b)] = True
    reg = grow
cells = [k for k in range(nx * ny) if reg[k]]
xs = [d["x0"] + (k % nx) * c for k in cells]
ys = [d["y0"] + (k // nx) * c for k in cells]
cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
verts, vid, faces = [], {}, []


def v(ci, cj):
    key = (ci, cj)
    if key not in vid:
        vid[key] = len(verts)
        verts.append((d["x0"] + (ci - 0.5) * c - cx, d["y0"] + (cj - 0.5) * c - cy, 0.0))
    return vid[key]


for k in cells:
    i, j = k % nx, k // nx
    faces.append((v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1)))
bpy.ops.wm.read_factory_settings(use_empty=True)
me = bpy.data.meshes.new("water")
me.from_pydata(verts, [], faces)
me.validate()
ob = bpy.data.objects.new(d["label"] + "_v2", me)
bpy.context.scene.collection.objects.link(ob)
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=1.15)
bpy.ops.object.mode_set(mode="OBJECT")
# make sure the face normals point up (+Z)
if sum(p.normal.z for p in me.polygons) < 0:
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.export_scene.fbx(filepath=out_fbx, use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                         axis_forward="X", axis_up="Z", mesh_smooth_type="FACE", add_leaf_bones=False, bake_space_transform=True)
print("[PMESH] %s core cells %d (was under water %d) final %d tris %d | place actor at (%.1f, %.1f, %.1f)" % (
    d["label"], core, sum(IN), len(cells), len(faces) * 2, cx, cy, surf))
