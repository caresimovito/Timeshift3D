# Editor Python: create BP_SinkZone (Actor) with a Trigger box, a MudDecal (deferred decal, projects down) and a TarSurface
# (flat static mesh, used when bIsTar). Logic is written separately with the DSL.
import unreal

TAG = "[SINKBP]"
EAL = unreal.EditorAssetLibrary
P = "/Game/Timeshift/Hazards/BP_SinkZone"
bp = EAL.load_asset(P)
if bp is None:
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", unreal.Actor)
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_SinkZone", "/Game/Timeshift/Hazards", unreal.Blueprint, f)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
LIB = unreal.SubobjectDataBlueprintFunctionLibrary
handles = sds.k2_gather_subobject_data_for_blueprint(bp)
have = {}
for h in handles:
    ob = LIB.get_object(sds.k2_find_subobject_data_from_handle(h))
    if ob:
        have.setdefault(ob.get_name().replace("_GEN_VARIABLE", ""), (h, ob))
root = handles[0]


def add(name, cls):
    if name in have:
        return have[name][1]
    h, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=cls, blueprint_context=bp))
    sds.rename_subobject(h, unreal.Text(name))
    ob = LIB.get_object(sds.k2_find_subobject_data_from_handle(h))
    have[name] = (h, ob)
    return ob


box = add("Trigger", unreal.BoxComponent)
box.set_editor_property("box_extent", unreal.Vector(250, 250, 120))
box.set_collision_profile_name("OverlapAllDynamic")
box.set_editor_property("generate_overlap_events", True)
box.set_editor_property("relative_location", unreal.Vector(0, 0, 60))
dec = add("MudDecal", unreal.DecalComponent)
dec.set_editor_property("decal_material", EAL.load_asset("/Game/Timeshift/Hazards/Materials/M_MudDecal"))
dec.set_editor_property("decal_size", unreal.Vector(150, 300, 300))
dec.set_editor_property("relative_rotation", unreal.Rotator(0, -90, 0))
tar = add("TarSurface", unreal.StaticMeshComponent)
tar.set_editor_property("static_mesh", EAL.load_asset("/Engine/BasicShapes/Plane"))
tar.set_material(0, EAL.load_asset("/Game/Timeshift/Hazards/Materials/M_Tar"))
tar.set_collision_profile_name("NoCollision")
tar.set_editor_property("visible", False)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset(P, only_if_is_dirty=False)
unreal.log_warning("%s components: %s" % (TAG, sorted(have.keys())))
