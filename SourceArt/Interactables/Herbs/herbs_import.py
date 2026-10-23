# Editor Python: import SM_HealingHerbs.glb (Tripo herb bundle, prepared by herbs_prep.py) into /Game/Timeshift/Interactables/Herbs
# and list what the importer made (mesh, materials and their parameters - for the glow)
import unreal
EAL = unreal.EditorAssetLibrary
DEST = "/Game/Timeshift/Interactables/Herbs"
t = unreal.AssetImportTask()
t.set_editor_property("filename", r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/Interactables/Herbs/SM_HealingHerbs.glb")
t.set_editor_property("destination_path", DEST)
t.set_editor_property("replace_existing", True)
t.set_editor_property("automated", True)
t.set_editor_property("save", True)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
for p in EAL.list_assets(DEST, True):
    a = EAL.load_asset(p.split(".")[0])
    info = a.get_class().get_name()
    if isinstance(a, unreal.StaticMesh):
        bb = a.get_bounding_box()
        info += " tris %d size %s..%s mat %s" % (a.get_num_triangles(0), bb.min, bb.max, a.get_material(0).get_path_name() if a.get_material(0) else None)
    if isinstance(a, unreal.MaterialInstanceConstant):
        info += " parent %s | vec %s | tex %s | scal %s" % (a.get_editor_property("parent").get_path_name() if a.get_editor_property("parent") else None,
                [(str(v.parameter_info.name), v.parameter_value) for v in a.get_editor_property("vector_parameter_values")][:8],
                [(str(v.parameter_info.name), v.parameter_value.get_name() if v.parameter_value else None) for v in a.get_editor_property("texture_parameter_values")][:8],
                [(str(v.parameter_info.name), v.parameter_value) for v in a.get_editor_property("scalar_parameter_values")][:8])
    unreal.log_warning("[HIMP] %s : %s" % (p.split(".")[0], info))
unreal.log_warning("[HIMP] done")
