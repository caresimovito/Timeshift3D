# Editor Python: any PowerUp_* pickup sitting below the swamp water surface (-5) inside the swamp's bounds is moved to the
# nearest dry landscape spot (rings of 3-9 m around it, ground above 0).
import math
import unreal
TAG = "[DRY]"
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()


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


for a in EAS.get_all_level_actors():
    if not a.get_actor_label().startswith("PowerUp_"):
        continue
    l = a.get_actor_location()
    if not (23200 < l.x < 38450 and -5300 < l.y < 5100 and l.z < -5):
        continue
    best = None
    for r in (300, 450, 600, 750, 900):
        for k in range(16):
            x, y = l.x + r * math.cos(k * math.pi / 8), l.y + r * math.sin(k * math.pi / 8)
            z = land(x, y)
            if z is not None and z > 2:
                best = unreal.Vector(x, y, z)
                break
        if best:
            break
    if best:
        a.modify()
        a.set_actor_location(best, False, True)
        unreal.log_warning("%s moved %s (%.0f,%.0f,%.0f) -> (%.0f,%.0f,%.0f)" % (TAG, a.get_actor_label(), l.x, l.y, l.z, best.x, best.y, best.z))
    else:
        unreal.log_warning("%s no dry spot near %s" % (TAG, a.get_actor_label()))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log_warning("%s done" % TAG)
