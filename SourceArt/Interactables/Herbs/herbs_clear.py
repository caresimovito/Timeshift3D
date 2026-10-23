# Editor Python (user 2026-10-23: herbs hidden in the undergrowth): for each herbs pickup, how much scatter foliage (any
# instanced mesh: ferns, cycads, bushes - most have no collision, so use the instance positions) stands within 1.6 m.
# MODE='apply' moves each covered herb to the nearest spot within 8 m with no foliage instance inside 1.6 m whose ground is
# landscape (first downward hit) and not more than 1.5 m above / below its old spot. Previous spots -> herbs_clear_prev.json
import json
import math
import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()
mode = globals().get("MODE", "check")
R = 160.0
pts = []
for a in EAS.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        if not m:
            continue
        bb = m.get_bounding_box()
        if bb.max.z - bb.min.z > 1500:      # tall trees: canopy is overhead, not covering the ground
            continue
        for i in range(c.get_instance_count()):
            t = c.get_instance_transform(i, True)
            pts.append((t.translation.x, t.translation.y))
G = 400.0
grid = {}
for x, y in pts:
    grid.setdefault((int(x // G), int(y // G)), []).append((x, y))


def cover(x, y):
    n = 0
    for gx in range(int(x // G) - 1, int(x // G) + 2):
        for gy in range(int(y // G) - 1, int(y // G) + 2):
            for px, py in grid.get((gx, gy), []):
                if (px - x) ** 2 + (py - y) ** 2 < R * R:
                    n += 1
    return n


def land(x, y, top):
    t = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, top), unreal.Vector(x, y, top - 4000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                               False, [], unreal.DrawDebugTrace.NONE, True)
    t = t.to_tuple() if t else None
    return t[4].z if t and t[0] and t[10] and "Landscape" in t[10].get_name() else None


prev = {}
for a in EAS.get_all_level_actors():
    if a.get_class().get_name() != "BP_Pickup_Health_C":
        continue
    l = a.get_actor_location()
    n0 = cover(l.x, l.y)
    msg = "%-16s cover %2d" % (a.get_actor_label(), n0)
    if n0 > 0:
        g0 = land(l.x, l.y, l.z + 1500) or l.z
        best = None
        for rad in range(100, 801, 50):
            for k in range(24):
                x, y = l.x + rad * math.cos(k * math.pi / 12), l.y + rad * math.sin(k * math.pi / 12)
                if cover(x, y):
                    continue
                gz = land(x, y, l.z + 1500)
                if gz is None or abs(gz - g0) > 150:
                    continue
                best = (rad, x, y, gz + (l.z - g0))
                break
            if best:
                break
        msg += " -> %s" % ("open spot %d cm away" % best[0] if best else "no open spot")
        if best and mode == "apply":
            prev[a.get_actor_label()] = [l.x, l.y, l.z]
            a.modify()
            a.set_actor_location(unreal.Vector(best[1], best[2], best[3]), False, False)
    unreal.log_warning("[HCLR] " + msg)
if mode == "apply":
    json.dump(prev, open(r"C:/agentpy/herbs_clear_prev.json", "w"))
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log_warning("[HCLR] done (%s), %d foliage instances" % (mode, len(pts)))
