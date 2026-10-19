# Editor Python: temporary "find it" beacon over the tar pit — a tall glowing orange pillar (unlit emissive, no collision,
# no shadow), visible from far off in editor and PIE. Folder Markers, label MARKER_TarPit. Delete when no longer needed.
import unreal

TAG = "[MARK]"
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
D = "/Game/Timeshift/Debug"
m = EAL.load_asset(D + "/M_DebugMarker") or unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    "M_DebugMarker", D, unreal.Material, unreal.MaterialFactoryNew())
MEL.delete_all_material_expressions(m)
col = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -400, 0)
col.set_editor_property("constant", unreal.LinearColor(12.0, 3.0, 0.2, 1))
MEL.connect_material_property(col, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)

for a in EAS.get_all_level_actors():
    if a.get_actor_label() == "MARKER_TarPit":
        EAS.destroy_actor(a)
tar = [a for a in EAS.get_all_level_actors() if a.get_actor_label() == "Swamp_TarPit"][0].get_actor_location()
a = EAS.spawn_actor_from_object(EAL.load_asset("/Engine/BasicShapes/Cylinder"), unreal.Vector(tar.x, tar.y, tar.z + 1250), unreal.Rotator(0, 0, 0))
a.set_actor_label("MARKER_TarPit")
a.set_folder_path("Markers")
a.set_actor_scale3d(unreal.Vector(0.6, 0.6, 25.0))   # 60 cm wide, 25 m tall
c = a.static_mesh_component
c.set_material(0, m)
c.set_collision_profile_name("NoCollision")
c.set_editor_property("cast_shadow", False)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log_warning("%s MARKER_TarPit at %s" % (TAG, a.get_actor_location()))
