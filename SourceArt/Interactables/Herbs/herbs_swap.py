# Editor Python: BP_Pickup_Health shows the new herb bundle (template component: mesh, material, scale 1.3 = ~58 cm, overlap
# profile kept) and every placed herbs pickup is cleared of per-instance mesh / scale overrides so it uses the template.
import unreal
SC = float(globals().get("SCALE", 1.3))
EAL = unreal.EditorAssetLibrary
bp = EAL.load_asset("/Game/Timeshift/Interactables/BP_Pickup_Health")
mesh = EAL.load_asset("/Game/Timeshift/Interactables/Herbs/SM_HealingHerbs/StaticMeshes/SM_HealingHerbs")
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
done = []
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    d = sds.k2_find_subobject_data_from_handle(h)
    obj = unreal.SubobjectDataBlueprintFunctionLibrary.get_object_for_blueprint(d, bp) if hasattr(unreal.SubobjectDataBlueprintFunctionLibrary, "get_object_for_blueprint") else unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
    if isinstance(obj, unreal.StaticMeshComponent):
        obj.set_editor_property("static_mesh", mesh)
        obj.set_editor_property("override_materials", [])
        obj.set_editor_property("relative_scale3d", unreal.Vector(SC, SC, SC))
        done.append((obj.get_name(), obj.get_collision_profile_name()))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset("/Game/Timeshift/Interactables/BP_Pickup_Health", only_if_is_dirty=False)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
n = 0
for a in EAS.get_all_level_actors():
    if a.get_class().get_name() == "BP_Pickup_Health_C":
        c = a.get_components_by_class(unreal.StaticMeshComponent)[0]
        a.modify()
        c.modify()
        c.set_static_mesh(mesh)
        c.set_material(0, mesh.get_material(0))
        c.set_relative_scale3d(unreal.Vector(SC, SC, SC))
        n += 1
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log_warning("[HSWAP] template comps %s, placed herbs updated %d" % (done, n))
