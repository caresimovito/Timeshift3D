# Editor Python: import SM_Swamp_Pond_Water_v3 (smooth marching-squares shoreline from swamp_water_smooth.py) and swap it
# into the Swamp_Pond_Water actor (same material, NoCollision, no shadow, actor at the mesh centre / water surface). The
# v2 mesh stays in the project; C:/agentpy/swamp_v3_prev.json records the previous mesh + location for a revert.
import json
import unreal
TAG = "[SWV3]"
EAL = unreal.EditorAssetLibrary
d = json.load(open(r"C:/agentpy/swamp_water_smooth.json"))
cx, cy, surf = d["centre"]
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
t = unreal.AssetImportTask()
t.set_editor_property("filename", r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/Environment/Water/SM_Swamp_Pond_Water_v3.fbx")
t.set_editor_property("destination_path", "/Game/Timeshift/Environment/Water")
t.set_editor_property("destination_name", "SM_Swamp_Pond_Water_v3")
t.set_editor_property("replace_existing", True)
t.set_editor_property("automated", True)
t.set_editor_property("save", True)
o = unreal.FbxImportUI()
o.set_editor_property("import_mesh", True)
o.set_editor_property("import_as_skeletal", False)
o.set_editor_property("import_materials", False)
o.set_editor_property("import_textures", False)
o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
o.get_editor_property("static_mesh_import_data").set_editor_property("combine_meshes", True)
t.set_editor_property("options", o)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
mesh = EAL.load_asset("/Game/Timeshift/Environment/Water/SM_Swamp_Pond_Water_v3")
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    if a.get_actor_label() != "Swamp_Pond_Water":
        continue
    c = a.static_mesh_component
    l = a.get_actor_location()
    json.dump({"mesh": c.static_mesh.get_path_name(), "loc": [l.x, l.y, l.z]}, open(r"C:/agentpy/swamp_v3_prev.json", "w"))
    mat = c.get_material(0)
    mesh.set_material(0, mat)
    bs = mesh.get_editor_property("body_setup")
    if bs:
        bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_SIMPLE_AS_COMPLEX)
    EAL.save_asset(mesh.get_path_name(), only_if_is_dirty=False)
    a.modify()
    c.set_static_mesh(mesh)
    c.set_material(0, mat)
    c.set_collision_profile_name("NoCollision")
    c.set_cast_shadow(False)
    a.set_actor_location(unreal.Vector(cx, cy, surf), False, False)
    o_, e_ = a.get_actor_bounds(False)
    unreal.log_warning("%s swapped %s -> %s (tris %d), actor at (%.0f, %.0f, %.1f), top z %.1f, material %s, tags %s" % (
        TAG, json.load(open(r"C:/agentpy/swamp_v3_prev.json"))["mesh"].split(".")[-1], mesh.get_name(), mesh.get_num_triangles(0),
        cx, cy, surf, o_.z + e_.z, mat.get_name() if mat else None, list(a.tags)))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log_warning("%s done" % TAG)
