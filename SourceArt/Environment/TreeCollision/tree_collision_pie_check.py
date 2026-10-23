# Editor Python, during PIE: did the tree collision survive loading (PCG GenerateOnLoad)? Count copies of the trunk-capsule
# trees still without collision in the PLAY world, and trace horizontally through a few trunks at 1 m height to confirm
# they block (and pass through the crown height to confirm the crown does not).
import unreal
TAG = "[TPC]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
TREES = ("SM_FirTree_01", "SM_IslandTree_01", "SM_TreeFern", "SM_TreeCycad_01", "SM_TreeCycad_02", "SM_TreeCycad_03", "SM_BurntTrunk_01")
off = on = 0
samples = {}
for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        if not m or m.get_name() not in TREES:
            continue
        k = c.get_instance_count() if isinstance(c, unreal.InstancedStaticMeshComponent) else 1
        if "NO_COLLISION" in str(c.get_collision_enabled()):
            off += k
        else:
            on += k
            if m.get_name() not in samples:
                t = c.get_instance_transform(0, True) if isinstance(c, unreal.InstancedStaticMeshComponent) else c.get_world_transform()
                samples[m.get_name()] = t
unreal.log_warning("%s in PLAY: %d copies with collision, %d without" % (TAG, on, off))
for name, t in samples.items():
    p = t.translation
    res = []
    for hz in (100.0, 350.0):
        s, e = unreal.Vector(p.x - 400, p.y, p.z + hz), unreal.Vector(p.x + 400, p.y, p.z + hz)
        h = unreal.SystemLibrary.line_trace_single(w, s, e, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        tt = h.to_tuple() if h else None
        hitname = tt[10].get_owner().get_actor_label() if tt and tt[0] and tt[10] else None
        res.append("%dcm: %s" % (hz, ("hit %s at %.0f cm from centre" % (hitname, abs(tt[4].x - p.x))) if tt and tt[0] else "clear"))
    unreal.log_warning("%s %-18s scale %.2f | %s" % (TAG, name, t.scale3d.x, " | ".join(res)))
unreal.log_warning("%s done" % TAG)
