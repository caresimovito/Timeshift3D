# Blender headless: swamp_water_smooth.json -> flat water mesh FBX (cm, Z up, +X forward) for Unreal.
# Y is negated: the FBX import mirrors Y (Blender right-handed -> Unreal left-handed), found 2026-10-22 - v3 was
# imported mirrored across its centre line until then.
import json
import sys
import bpy
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
d = json.load(open(src))
bpy.ops.wm.read_factory_settings(use_empty=True)
me = bpy.data.meshes.new("water")
me.from_pydata([(x, -y, 0.0) for x, y in d["verts"]], [], [tuple(f) for f in d["faces"]])
me.validate()
ob = bpy.data.objects.new("SM_Swamp_Pond_Water_v3", me)
bpy.context.scene.collection.objects.link(ob)
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
if sum(p.normal.z for p in me.polygons) < 0:
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode="OBJECT")
up = sum(1 for p in me.polygons if p.normal.z > 0)
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                         axis_forward="X", axis_up="Z", mesh_smooth_type="FACE", add_leaf_bones=False, bake_space_transform=True)
print("[SWFBX] verts %d faces %d (up-facing %d) -> %s" % (len(me.vertices), len(me.polygons), up, out))
