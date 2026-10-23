# Editor Python: import SM_TarPit_v2 (smooth organic outline, tar_smooth.py) and swap it into Swamp_TarPit's TarSurface
# (same M_Tar, NoCollision; the Trigger box is untouched, so the sinking behaves as before). SM_TarPit stays in the
# project - set it back on TarSurface to revert (2026-10-22).
import unreal
TAG = "[TARV2]"
EAL = unreal.EditorAssetLibrary
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
t = unreal.AssetImportTask()
t.set_editor_property("filename", r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/Environment/Hazards/SM_TarPit_v2.fbx")
t.set_editor_property("destination_path", "/Game/Timeshift/Hazards/Meshes")
t.set_editor_property("destination_name", "SM_TarPit_v2")
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
mesh = EAL.load_asset("/Game/Timeshift/Hazards/Meshes/SM_TarPit_v2")
mat = EAL.load_asset("/Game/Timeshift/Hazards/Materials/M_Tar")
mesh.set_material(0, mat)
EAL.save_asset(mesh.get_path_name(), only_if_is_dirty=False)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    if a.get_actor_label() != "Swamp_TarPit":
        continue
    a.modify()
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.get_name().startswith("TarSurface"):
            c.modify()
            c.set_static_mesh(mesh)
            c.set_material(0, mat)
            c.set_collision_profile_name("NoCollision")
            bb = mesh.get_bounding_box()
            unreal.log_warning("%s swapped -> %s tris %d bbox %s..%s visible %s" % (TAG, mesh.get_name(), mesh.get_num_triangles(0),
                               bb.min, bb.max, c.is_visible()))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log_warning("%s done" % TAG)
