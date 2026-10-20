# Editor Python: place Fury pickups beside 3 of the 4 armour pickups and Regeneration herbs beside 4 well-spread health
# pickups (2.5 m away, on the landscape). Folder Pickups/PowerUps, rebuilt each run.
#  Fury  = SM_Mushrooms (x0.8) in MI_PickupFury (pulsing red glow)
#  Regen = SM_Fern_01 (x0.35, a small herb) in MI_PickupRegen (pulsing green glow)
import math
import unreal
TAG = "[PPU]"
EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()
FOLDER = "Pickups/PowerUps"
acts = EAS.get_all_level_actors()
for a in acts:
    if str(a.get_folder_path()) == FOLDER:
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


def spread(locs, n):
    pick = [locs[0]]
    while len(pick) < min(n, len(locs)):
        pick.append(max(locs, key=lambda l: min((l - p).length() for p in pick)))
    return pick


def place(kind, near, mesh, mat, scale):
    cls = unreal.load_class(None, "/Game/Timeshift/Interactables/BP_Pickup_%s.BP_Pickup_%s_C" % (kind, kind))
    out = []
    for i, l in enumerate(near):
        for ang in (0, 90, 180, 270, 45, 135):
            x, y = l.x + 250 * math.cos(math.radians(ang)), l.y + 250 * math.sin(math.radians(ang))
            z = land(x, y)
            if z is not None and abs(z - l.z) < 120:
                break
        a = EAS.spawn_actor_from_class(cls, unreal.Vector(x, y, z), unreal.Rotator(0, 0, 0))
        a.set_actor_label("PowerUp_%s_%d" % (kind, i))
        a.set_folder_path(FOLDER)
        a.modify()
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        c.modify()
        c.set_static_mesh(EAL.load_asset(mesh))
        n = c.get_num_materials()
        for k in range(max(1, n)):
            c.set_material(k, EAL.load_asset(mat))
        c.set_relative_scale3d(unreal.Vector(scale, scale, scale))
        out.append("(%.0f,%.0f,%.0f)" % (x, y, z))
    unreal.log_warning("%s %s x%d at %s" % (TAG, kind, len(out), " ".join(out)))


armour = [a.get_actor_location() for a in acts if a.get_class().get_name() == "BP_Pickup_Armour_C"]
health = [a.get_actor_location() for a in acts if a.get_class().get_name() == "BP_Pickup_Health_C"]
M = "/Game/Timeshift/Interactables/Materials/"
place("Fury", spread(armour, 3), "/Game/Timeshift/Environment/Meshes/Jungle/Mushrooms/Mushrooms/StaticMeshes/SM_Mushrooms", M + "MI_PickupFury", 0.8)
place("Regen", spread(health, 4), "/Game/Timeshift/Environment/Meshes/Fern/SM_Fern_01", M + "MI_PickupRegen", 0.35)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
