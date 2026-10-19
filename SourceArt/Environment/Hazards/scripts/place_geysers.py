# Editor Python: BP_GeyserVent defaults, then 3 vents in shallow swamp water (25-60 cm deep), well apart and clear of the
# mud/tar zones. Folder Swamp/Hazards/Geysers, rebuilt each run. Root at the water surface (steam starts at the surface).
import unreal

TAG = "[GEYP]"
EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()
cls = unreal.load_class(None, "/Game/Timeshift/Hazards/BP_GeyserVent.BP_GeyserVent_C")
cdo = unreal.get_default_object(cls)
for k, v in (("IdleMin", 6.0), ("IdleMax", 10.0), ("WarnTime", 1.8), ("BurstTime", 3.0), ("Damage", 15.0), ("LaunchZ", 1100.0)):
    cdo.set_editor_property(k, v)
EAL.save_asset("/Game/Timeshift/Hazards/BP_GeyserVent", only_if_is_dirty=False)

acts = EAS.get_all_level_actors()
pond = [a for a in acts if a.get_actor_label() == "Swamp_Pond_Water"][0]
avoid = [a.get_actor_location() for a in acts if str(a.get_folder_path()).startswith("Swamp/Hazards")]
FOLDER = "Swamp/Hazards/Geysers"
for a in acts:
    if str(a.get_folder_path()) == FOLDER:
        EAS.destroy_actor(a)


def hits(x, y):
    """(water surface z, ground z) along a vertical line, ground = first Landscape hit."""
    ign, water, ground = [], None, None
    for _ in range(12):
        h = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, 3000), unreal.Vector(x, y, -3000),
                                                   unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ign, unreal.DrawDebugTrace.NONE, True)
        t = h.to_tuple() if h else None
        if not t or not t[0] or not t[9]:
            break
        if t[9] == pond and water is None:
            water = t[4].z
        if "Landscape" in type(t[9]).__name__:
            ground = t[4].z
            break
        ign.append(t[9])
    return water, ground


o, e = pond.get_actor_bounds(False)
surf = o.z + e.z   # flat water mesh without collision: its top is the surface
unreal.log_warning("%s pond surface z=%.1f bounds %s %s" % (TAG, surf, o, e))
# spots from geyser_spots.py (inside the real water footprint, 25-60 cm deep, near the swamp centre)
import json
picked = []
for x, y in json.load(open(r"C:/agentpy/geyser_spots.py".replace(".py", ".json"))):
    _, gz = hits(x, y)
    picked.append((surf - gz if gz is not None else -1, unreal.Vector(x, y, surf)))
for i, (dep, p) in enumerate(picked):
    a = EAS.spawn_actor_from_class(cls, p, unreal.Rotator(0, 0, 0))
    a.set_actor_label("Swamp_Geyser_%d" % i)
    a.set_folder_path(FOLDER)
    unreal.log_warning("%s Swamp_Geyser_%d at (%.0f,%.0f,%.0f) depth %.0f" % (TAG, i, p.x, p.y, p.z, dep))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
