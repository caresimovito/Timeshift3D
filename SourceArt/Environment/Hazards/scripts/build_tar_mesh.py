# Blender headless: flat tar surface from tar_cells.json (cell centres, cm), grown by 1 cell, centred; FBX out (cm units).
import json
import sys
import bpy

src, out_fbx = sys.argv[sys.argv.index("--") + 1:][:2]
d = json.load(open(src))
c = d["cell"]
mx = min(x for x, _ in d["cells"])
my = min(y for _, y in d["cells"])
cells = {(round((x - mx) / c), round((y - my) / c)) for x, y in d["cells"]}
grown = set(cells)
for (i, j) in cells:
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            grown.add((i + di, j + dj))
ii = [i for i, _ in grown]
jj = [j for _, j in grown]
ci, cj = (min(ii) + max(ii)) / 2, (min(jj) + max(jj)) / 2
verts, vid, faces = [], {}, []


def v(a, b):
    if (a, b) not in vid:
        vid[(a, b)] = len(verts)
        verts.append(((a - 0.5 - ci) * c, (b - 0.5 - cj) * c, 0.0))
    return vid[(a, b)]


for (i, j) in grown:
    faces.append((v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1)))
bpy.ops.wm.read_factory_settings(use_empty=True)
me = bpy.data.meshes.new("tar")
me.from_pydata(verts, [], faces)
me.validate()
ob = bpy.data.objects.new("SM_TarPit", me)
bpy.context.scene.collection.objects.link(ob)
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=1.15)
bpy.ops.object.mode_set(mode="OBJECT")
if sum(p.normal.z for p in me.polygons) < 0:
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.export_scene.fbx(filepath=out_fbx, use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                         axis_forward="X", axis_up="Z", mesh_smooth_type="FACE", add_leaf_bones=False, bake_space_transform=True)
print("[TAR] cells %d grown %d | centre (%.1f, %.1f)" % (len(cells), len(grown), mx + ci * c, my + cj * c))
