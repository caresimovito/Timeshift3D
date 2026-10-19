# Editor Python: what blocks at the rockfall path? Simple-collision traces (what the player collides with) vs complex,
# on a line along the path, plus the RCTree actors' bounds near it.
import unreal
TAG = "[HULL]"
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()
for x in range(49200, 51001, 300):
    row = []
    for y in (0, 300, 500, 800, 1100):
        hs = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, 1200), unreal.Vector(x, y, -500),
                                                    unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True).to_tuple()
        row.append("y%d:%s:%s" % (y, int(hs[4].z) if hs[0] else "-", (hs[9].get_actor_label() if hs[9] else "")[:12]))
    unreal.log_warning("%s x=%d %s" % (TAG, x, " ".join(row)))
for a in EAS.get_all_level_actors():
    if a.get_actor_label() in ("RCTree_14", "RCTree_19", "RCTree_21", "RCTree_23"):
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        l, s = a.get_actor_location(), a.get_actor_scale3d()
        unreal.log_warning("%s %s at (%.0f,%.0f,%.0f) scale %.2f mesh %s col=%s" % (TAG, a.get_actor_label(), l.x, l.y, l.z, s.x, smc.static_mesh.get_name(),
                           str(smc.get_collision_enabled()).split(".")[-1].split(":")[0]))
