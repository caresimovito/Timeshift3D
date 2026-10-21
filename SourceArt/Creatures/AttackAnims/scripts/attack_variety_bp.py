# Editor Python: create BP_AttackVariety (ActorComponent) - logic is written separately with the DSL; MODE='attach' adds
# it to TARGET (default BP_EnemyBase) as a component named AttackVariety (none of the target's graphs is touched). The
# hero carries one too, so the morph can play the same moves (its Watch tick does nothing: the owner is not an enemy).
import unreal
TAG = "[AVB]"
EAL = unreal.EditorAssetLibrary
P = "/Game/Timeshift/Enemies/BP_AttackVariety"
mode = globals().get("MODE", "create")
if mode == "create":
    if not EAL.does_asset_exist(P):
        f = unreal.BlueprintFactory()
        f.set_editor_property("parent_class", unreal.ActorComponent)
        unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_AttackVariety", "/Game/Timeshift/Enemies", unreal.Blueprint, f)
    EAL.save_asset(P, only_if_is_dirty=False)
    unreal.log_warning("%s created %s" % (TAG, EAL.does_asset_exist(P)))
else:
    eb = EAL.load_asset(globals().get("TARGET", "/Game/Timeshift/Enemies/BP_EnemyBase"))
    cls = unreal.load_class(None, P + ".BP_AttackVariety_C")
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    LIB = unreal.SubobjectDataBlueprintFunctionLibrary
    handles = sds.k2_gather_subobject_data_for_blueprint(eb)
    names = []
    for h in handles:
        ob = LIB.get_object(sds.k2_find_subobject_data_from_handle(h))
        if ob:
            names.append(ob.get_name())
    if not any("AttackVariety" in n for n in names):
        h, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=handles[0], new_class=cls, blueprint_context=eb))
        sds.rename_subobject(h, unreal.Text("AttackVariety"))
    unreal.BlueprintEditorLibrary.compile_blueprint(eb)
    EAL.save_asset(eb.get_path_name(), only_if_is_dirty=False)
    unreal.log_warning("%s attached; enemy status %s; comps now %s" % (TAG, eb.get_editor_property("status"),
                       [LIB.get_object(sds.k2_find_subobject_data_from_handle(h)).get_name() for h in sds.k2_gather_subobject_data_for_blueprint(eb) if LIB.get_object(sds.k2_find_subobject_data_from_handle(h))][-4:]))
