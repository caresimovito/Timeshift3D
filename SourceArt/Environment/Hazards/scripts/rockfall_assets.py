# Editor Python: rockfall assets.
#  - import S_RockRumble + S_RockImpact_01..03 (SourceArt/Audio/Hazards) -> /Game/Timeshift/Hazards/Audio (3D, SFX class)
#  - NS_RockDust = NS_GeyserWarn duplicate (retinted/tuned afterwards with the Niagara tools)
#  - BP_FallingRock: Actor with a "Rock" static mesh (SM_Boulder_01, no collision - flight is scripted, see DSL)
#  - BP_Rockfall: Actor with a "Trigger" box over the path under the cliff
import unreal

TAG = "[RFA]"
EAL = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
names = ["S_RockRumble", "S_RockImpact_01", "S_RockImpact_02", "S_RockImpact_03"]
tasks = []
for nm in names:
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/Audio/Hazards/%s.wav" % nm)
    t.set_editor_property("destination_path", "/Game/Timeshift/Hazards/Audio")
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("automated", True)
    t.set_editor_property("save", True)
    tasks.append(t)
tools.import_asset_tasks(tasks)
att = EAL.load_asset("/Game/Timeshift/Audio/Attenuation/SA_Creature_Large")
sfx = EAL.load_asset("/Game/Timeshift/Audio/Classes/SC_SFX")
for nm in names:
    s = EAL.load_asset("/Game/Timeshift/Hazards/Audio/" + nm)
    if att:
        s.set_editor_property("attenuation_settings", att)
    if sfx:
        s.set_editor_property("sound_class_object", sfx)
    EAL.save_asset(s.get_path_name(), only_if_is_dirty=False)
if not EAL.does_asset_exist("/Game/Timeshift/Hazards/VFX/NS_RockDust"):
    EAL.duplicate_asset("/Game/Timeshift/Hazards/VFX/NS_GeyserWarn", "/Game/Timeshift/Hazards/VFX/NS_RockDust")
EAL.save_asset("/Game/Timeshift/Hazards/VFX/NS_RockDust", only_if_is_dirty=False)

sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
LIB = unreal.SubobjectDataBlueprintFunctionLibrary


def bp_with(path, comps):
    bp = EAL.load_asset(path)
    if bp is None:
        f = unreal.BlueprintFactory()
        f.set_editor_property("parent_class", unreal.Actor)
        bp = tools.create_asset(path.split("/")[-1], "/".join(path.split("/")[:-1]), unreal.Blueprint, f)
    handles = sds.k2_gather_subobject_data_for_blueprint(bp)
    have = {}
    for h in handles:
        ob = LIB.get_object(sds.k2_find_subobject_data_from_handle(h))
        if ob:
            have.setdefault(ob.get_name().replace("_GEN_VARIABLE", ""), ob)
    out = {}
    for name, cls in comps:
        if name not in have:
            h, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=handles[0], new_class=cls, blueprint_context=bp))
            sds.rename_subobject(h, unreal.Text(name))
            have[name] = LIB.get_object(sds.k2_find_subobject_data_from_handle(h))
        out[name] = have[name]
    return bp, out


bp, c = bp_with("/Game/Timeshift/Hazards/BP_FallingRock", [("Rock", unreal.StaticMeshComponent)])
c["Rock"].set_editor_property("static_mesh", EAL.load_asset("/Game/Timeshift/Environment/Meshes/SM_Boulder_01"))
c["Rock"].set_collision_profile_name("NoCollision")
c["Rock"].set_editor_property("relative_location", unreal.Vector(0, 0, 0))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset(bp.get_path_name(), only_if_is_dirty=False)

bp2, c2 = bp_with("/Game/Timeshift/Hazards/BP_Rockfall", [("Trigger", unreal.BoxComponent)])
c2["Trigger"].set_editor_property("box_extent", unreal.Vector(1000, 800, 300))
c2["Trigger"].set_editor_property("relative_location", unreal.Vector(0, 0, 250))
c2["Trigger"].set_collision_profile_name("OverlapAllDynamic")
c2["Trigger"].set_editor_property("generate_overlap_events", True)
unreal.BlueprintEditorLibrary.compile_blueprint(bp2)
EAL.save_asset(bp2.get_path_name(), only_if_is_dirty=False)
m = EAL.load_asset("/Game/Timeshift/Environment/Meshes/SM_Boulder_01").get_bounding_box()
unreal.log_warning("%s sounds=%s boulder size=(%.0f,%.0f,%.0f) centre z=%.0f" % (TAG, [EAL.does_asset_exist("/Game/Timeshift/Hazards/Audio/" + n) for n in names],
                   m.max.x - m.min.x, m.max.y - m.min.y, m.max.z - m.min.z, (m.max.z + m.min.z) / 2))
