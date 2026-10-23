# Blender headless: tar_smooth.json -> SM_TarPit_v2 FBX (cm, Z up, +X forward, planar UVs from the json) for Unreal.
# Y is negated: the FBX import mirrors Y (Blender right-handed -> Unreal left-handed), found 2026-10-22 when the
# imported mesh came out mirrored against the terrain it was traced from.
import json
import sys
import bpy
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
d = json.load(open(src))
bpy.ops.wm.read_factory_settings(use_empty=True)
me = bpy.data.meshes.new("tar")
me.from_pydata([(x, -y, 0.0) for x, y in d["verts"]], [], [tuple(f) for f in d["faces"]])
me.validate()
if sum(p.normal.z for p in me.polygons) < 0:
    me.flip_normals()
uvl = me.uv_layers.new(name="UVMap")
for loop in me.loops:
    uvl.data[loop.index].uv = d["uv"][loop.vertex_index]
ob = bpy.data.objects.new("SM_TarPit_v2", me)
bpy.context.scene.collection.objects.link(ob)
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
up = sum(1 for p in me.polygons if p.normal.z > 0)
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                         axis_forward="X", axis_up="Z", mesh_smooth_type="FACE", add_leaf_bones=False, bake_space_transform=True)
print("[TARFBX] verts %d faces %d (up-facing %d) -> %s" % (len(me.vertices), len(me.polygons), up, out))
