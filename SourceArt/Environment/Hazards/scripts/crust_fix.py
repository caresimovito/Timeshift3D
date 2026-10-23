# Editor Python: fix the floating arena rocks (user 2026-10-22 screenshot: "floating something!?? looks wrong").
#  1. A2_Crust_* slabs that lie OUTSIDE the lava mesh (crust_probe3: 29 of 130, at the channel edges) - they ride the
#     rotating A2_LavaFlow, so they slid over dry ground at lava height. Each moves to the nearest point at least 60 cm
#     inside the lava (searching radius +-9 m and angle +-12 deg around the ring centre), bottom 6 cm under the lava surface
#     like the others. Attachment to the ring is kept (they are meant to drift with the lava).
#  2. Other Arena2/Detail rocks (scree / talus, SM_Rock09) whose bottom hangs > 30 cm above the first surface under them:
#     dropped so the bottom sits 5 cm into that surface.
# Nothing is deleted. Previous locations -> C:/agentpy/crust_fix_prev.json (MODE='revert' puts them back). MODE='dry' logs only.
import json
import math
import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()
TAG = "[CFIX]"
mode = globals().get("MODE", "dry")
acts = EAS.get_all_level_actors()
by_label = {a.get_actor_label(): a for a in acts}
if mode == "revert":
    prev = json.load(open(r"C:/agentpy/crust_fix_prev.json"))
    for lab, (x, y, z) in prev.items():
        if lab in by_label:
            by_label[lab].set_actor_location(unreal.Vector(x, y, z), False, False)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    unreal.log_warning("%s reverted %d" % (TAG, len(prev)))
else:
    crust = [a for a in acts if a.get_actor_label().startswith("A2_Crust_")]
    ring = by_label["A2_LavaFlow"]
    lava = ring.get_components_by_class(unreal.StaticMeshComponent)[0]
    T = lava.get_world_transform()
    sec = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(lava.static_mesh, 0, 0)
    vs = [T.transform_location(v) for v in sec[0]]
    tri = sec[1]
    G = 200.0
    buckets = {}
    for k in range(0, len(tri), 3):
        a, b, c = vs[tri[k]], vs[tri[k + 1]], vs[tri[k + 2]]
        for gx in range(int(min(a.x, b.x, c.x) // G), int(max(a.x, b.x, c.x) // G) + 1):
            for gy in range(int(min(a.y, b.y, c.y) // G), int(max(a.y, b.y, c.y) // G) + 1):
                buckets.setdefault((gx, gy), []).append((a, b, c))

    def lava_z(x, y):
        for a, b, c in buckets.get((int(x // G), int(y // G)), []):
            d = (b.y - c.y) * (a.x - c.x) + (c.x - b.x) * (a.y - c.y)
            if abs(d) < 1e-6:
                continue
            l1 = ((b.y - c.y) * (x - c.x) + (c.x - b.x) * (y - c.y)) / d
            l2 = ((c.y - a.y) * (x - c.x) + (a.x - c.x) * (y - c.y)) / d
            l3 = 1 - l1 - l2
            if l1 >= -1e-4 and l2 >= -1e-4 and l3 >= -1e-4:
                return l1 * a.z + l2 * b.z + l3 * c.z
        return None

    def deep(x, y):
        z = lava_z(x, y)
        if z is None:
            return None
        for dx, dy in ((60, 0), (-60, 0), (0, 60), (0, -60), (42, 42), (-42, 42), (42, -42), (-42, -42)):
            if lava_z(x + dx, y + dy) is None:
                return None
        return z

    cx, cy = ring.get_actor_location().x, ring.get_actor_location().y
    prev, moved, failed = {}, 0, []
    for a in crust:
        o, e = a.get_actor_bounds(False)
        if lava_z(o.x, o.y) is not None:
            continue
        r0 = math.hypot(o.x - cx, o.y - cy)
        th0 = math.atan2(o.y - cy, o.x - cx)
        best = None
        for dr in range(-900, 901, 50):
            for dth in [k * 0.5 for k in range(-24, 25)]:
                r, th = r0 + dr, th0 + math.radians(dth)
                x, y = cx + r * math.cos(th), cy + r * math.sin(th)
                z = deep(x, y)
                if z is None:
                    continue
                dist = math.hypot(x - o.x, y - o.y)
                if best is None or dist < best[0]:
                    best = (dist, x, y, z)
        if not best:
            failed.append(a.get_actor_label())
            continue
        l = a.get_actor_location()
        bot = o.z - e.z
        nl = unreal.Vector(l.x + (best[1] - o.x), l.y + (best[2] - o.y), l.z + (best[3] - 6 - bot))
        prev[a.get_actor_label()] = [l.x, l.y, l.z]
        moved += 1
        if mode == "apply":
            a.modify()
            a.set_actor_location(nl, False, False)
    unreal.log_warning("%s crust: %d moved onto the lava (max shift %s), no lava spot found: %s" % (TAG, moved,
                       "%.0f cm" % max([math.hypot(by_label[k].get_actor_location().x - v[0], by_label[k].get_actor_location().y - v[1]) for k, v in prev.items()] or [0]) if mode == "apply" else "n/a (dry)", failed))

    rocks = [a for a in acts if str(a.get_folder_path()).startswith("Arena2/Detail") and a.get_class().get_name() == "StaticMeshActor"
             and not a.get_actor_label().startswith("A2_Crust_")
             and any(c.get_editor_property("static_mesh") and "Rock09" in c.get_editor_property("static_mesh").get_name()
                     for c in a.get_components_by_class(unreal.StaticMeshComponent))]
    dropped, gaps = 0, []
    for a in rocks:
        o, e = a.get_actor_bounds(False)
        t = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(o.x, o.y, o.z + e.z + 10), unreal.Vector(o.x, o.y, o.z - 5000),
                                                   unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [a], unreal.DrawDebugTrace.NONE, True)
        t = t.to_tuple() if t else None
        if not t or not t[0]:
            continue
        gap = (o.z - e.z) - t[4].z
        if gap > 30:
            gaps.append((round(gap), a.get_actor_label(), t[9].get_actor_label() if t[9] else None))
            l = a.get_actor_location()
            prev[a.get_actor_label()] = [l.x, l.y, l.z]
            dropped += 1
            if mode == "apply":
                a.modify()
                a.set_actor_location(unreal.Vector(l.x, l.y, l.z - gap - 5), False, False)
    gaps.sort(reverse=True)
    unreal.log_warning("%s other rocks: %d of %d hanging > 30 cm, dropped%s; worst %s" % (TAG, dropped, len(rocks), "" if mode == "apply" else " (dry)", gaps[:6]))
    if mode == "apply":
        json.dump(prev, open(r"C:/agentpy/crust_fix_prev.json", "w"))
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log_warning("%s done (%s)" % (TAG, mode))
