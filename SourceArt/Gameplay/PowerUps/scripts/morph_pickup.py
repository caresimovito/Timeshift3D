# Editor Python: Morph Amber pickup.
#  - BP_Pickup_Morph = duplicate of BP_Pickup_Adrenaline (EventInteract rewritten to AddMorphCharge via the DSL)
#  - MI_PickupMorph: amber glow on M_PickupGlow
#  - 3 placed beside well-spread Hide pickups (folder Pickups/PowerUps), mesh = the small-egg pickup's mesh, glowing amber
#  - reports hero compile status
import math
import unreal
TAG = "[MPK]"
EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()
tools = unreal.AssetToolsHelpers.get_asset_tools()
hero = EAL.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
unreal.BlueprintEditorLibrary.compile_blueprint(hero)
unreal.log_warning("%s hero status %s" % (TAG, hero.get_editor_property("status")))
I = "/Game/Timeshift/Interactables/"
if not EAL.does_asset_exist(I + "BP_Pickup_Morph"):
    EAL.duplicate_asset(I + "BP_Pickup_Adrenaline", I + "BP_Pickup_Morph")
EAL.save_asset(I + "BP_Pickup_Morph", only_if_is_dirty=False)
D = I + "Materials"
mi = EAL.load_asset(D + "/MI_PickupMorph") or tools.create_asset("MI_PickupMorph", D, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
mi.set_editor_property("parent", EAL.load_asset(D + "/M_PickupGlow"))
unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(mi, "GlowColor", unreal.LinearColor(1.0, 0.45, 0.04, 1))
unreal.MaterialEditingLibrary.update_material_instance(mi)
EAL.save_asset(mi.get_path_name(), only_if_is_dirty=False)
acts = EAS.get_all_level_actors()
egg = [a for a in acts if a.get_class().get_name() == "BP_Pickup_EggSmall_C"][0].get_component_by_class(unreal.StaticMeshComponent)
egg_mesh, egg_scale = egg.static_mesh, egg.get_editor_property("relative_scale3d")
unreal.log_warning("%s egg mesh %s scale %s" % (TAG, egg_mesh.get_path_name(), egg_scale))
for a in acts:
    if a.get_actor_label().startswith("PowerUp_Morph"):
        EAS.destroy_actor(a)


def land(x, y):
    ign = []
    for _ in range(12):
        h = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, 5000), unreal.Vector(x, y, -3000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                   False, ign, unreal.DrawDebugTrace.NONE, True).to_tuple()
        if not h[0] or not h[9]:
            return None
        if "Landscape" in type(h[9]).__name__:
            return h[4].z
        ign.append(h[9])


hide = [a.get_actor_location() for a in acts if a.get_class().get_name() == "BP_Pickup_Hide_C"]
pick = [hide[0]]
while len(pick) < min(3, len(hide)):
    pick.append(max(hide, key=lambda l: min((l - p).length() for p in pick)))
cls = unreal.load_class(None, I + "BP_Pickup_Morph.BP_Pickup_Morph_C")
done = []
for i, l in enumerate(pick):
    for ang in (0, 90, 180, 270, 45, 135):
        x, y = l.x + 250 * math.cos(math.radians(ang)), l.y + 250 * math.sin(math.radians(ang))
        z = land(x, y)
        if z is not None and abs(z - l.z) < 120:
            break
    a = EAS.spawn_actor_from_class(cls, unreal.Vector(x, y, z), unreal.Rotator(0, 0, 0))
    a.set_actor_label("PowerUp_Morph_%d" % i)
    a.set_folder_path("Pickups/PowerUps")
    a.modify()
    c = a.get_component_by_class(unreal.StaticMeshComponent)
    c.modify()
    c.set_static_mesh(egg_mesh)
    for k in range(max(1, c.get_num_materials())):
        c.set_material(k, mi)
    c.set_relative_scale3d(egg_scale * 1.3)
    done.append("(%.0f,%.0f,%.0f)" % (x, y, z))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log_warning("%s Morph x%d at %s" % (TAG, len(done), " ".join(done)))
