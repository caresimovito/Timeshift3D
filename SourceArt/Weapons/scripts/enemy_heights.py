# Editor Python: BP_EnemyBase actors - actor z vs landscape z under them, root (cylinder) scale, fly-related vars.
import unreal
TAG = "[ENH]"
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()
cls = unreal.load_class(None, "/Game/Timeshift/Enemies/BP_EnemyBase.BP_EnemyBase_C")


def land(x, y, ign):
    ign = list(ign)
    for _ in range(10):
        h = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, 6000), unreal.Vector(x, y, -3000),
                                                   unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ign, unreal.DrawDebugTrace.NONE, True).to_tuple()
        if not h[0] or not h[9]:
            return None
        if "Landscape" in type(h[9]).__name__:
            return h[4].z
        ign.append(h[9])


en = [a for a in EAS.get_all_level_actors() if a.get_class() == cls or a.get_class().get_name() == "BP_EnemyBase_C"]
fly_props = []
if en:
    for p in ("bIsFlyer", "bFlying", "bCanFly", "IsFlyer", "Flyer", "bFlyer", "FlyHeight", "MovementType", "Species"):
        try:
            en[0].get_editor_property(p)
            fly_props.append(p)
        except Exception:
            pass
unreal.log_warning("%s %d enemies; readable props %s" % (TAG, len(en), fly_props))
rows = []
for a in en[:400]:
    l = a.get_actor_location()
    g = land(l.x, l.y, [a])
    extra = " ".join("%s=%s" % (p, a.get_editor_property(p)) for p in fly_props)
    rows.append((a.get_actor_label(), l.z - g if g is not None else None, a.get_actor_scale3d().z, extra))
grounded = [r for r in rows if r[1] is not None and abs(r[1]) < 60]
air = [r for r in rows if r[1] is not None and r[1] >= 60]
unreal.log_warning("%s grounded(|dz|<60): %d e.g. %s" % (TAG, len(grounded), [(r[0], round(r[1]), r[3]) for r in grounded[:4]]))
unreal.log_warning("%s above ground: %d e.g. %s" % (TAG, len(air), [(r[0], round(r[1]), r[3]) for r in air[:10]]))
