# Editor Python: reimport SM_Swamp_Pond_Water_v3 and SM_TarPit_v2 in place from their Y-corrected FBXs (the first imports
# were mirrored in Y). Actors keep their references; then print the mean vertex so it can be compared with the json.
import unreal
EAL = unreal.EditorAssetLibrary
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
for fbx, dest, name in ((r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/Environment/Water/SM_Swamp_Pond_Water_v3.fbx", "/Game/Timeshift/Environment/Water", "SM_Swamp_Pond_Water_v3"),
                        (r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/Environment/Hazards/SM_TarPit_v2.fbx", "/Game/Timeshift/Hazards/Meshes", "SM_TarPit_v2")):
    m0 = EAL.load_asset(dest + "/" + name)
    mat = m0.get_material(0)
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", fbx)
    t.set_editor_property("destination_path", dest)
    t.set_editor_property("destination_name", name)
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
    m = EAL.load_asset(dest + "/" + name)
    m.set_material(0, mat)
    EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)
    vs = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(m, 0, 0)[0]
    unreal.log_warning("[MIR2] %s mean x %.1f mean y %.1f n %d mat %s" % (name, sum(v.x for v in vs) / len(vs), sum(v.y for v in vs) / len(vs), len(vs),
                       mat.get_name() if mat else None))
unreal.log_warning("[MIR2] done")
