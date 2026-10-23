# Editor Python: which A2_Crust_* slabs actually lie over the lava? The lava mesh (SM_Arena2_Lava on the rotating
# A2_LavaFlow) has no trace collision, so test geometrically: slab centre (x, y) inside a lava triangle (world space,
# bucketed by 2 m grid), with the lava surface z there. Writes C:/agentpy/crust_rows2.json.
import json
import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()
TAG = "[CRU3]"
acts = EAS.get_all_level_actors()
crust = [a for a in acts if a.get_actor_label().startswith("A2_Crust_")]
ring = [a for a in acts if a.get_actor_label() == "A2_LavaFlow"][0]
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


rows = []
for a in crust:
    o, e = a.get_actor_bounds(False)
    bot = o.z - e.z
    lz = lava_z(o.x, o.y)
    t = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(o.x, o.y, o.z + 30), unreal.Vector(o.x, o.y, o.z - 5000),
                                               unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, crust + [ring], unreal.DrawDebugTrace.NONE, True).to_tuple()
    gz = t[4].z if t[0] else None
    rows.append({"label": a.get_actor_label(), "x": o.x, "y": o.y, "bottom": bot, "top": o.z + e.z, "lava": lz, "ground": gz,
                 "over": t[9].get_actor_label() if t[0] and t[9] else None, "r": ((o.x - 95600) ** 2 + o.y ** 2) ** 0.5})
on = [r for r in rows if r["lava"] is not None]
off = [r for r in rows if r["lava"] is None]
json.dump(rows, open(r"C:/agentpy/crust_rows2.json", "w"), indent=0)
unreal.log_warning("%s lava tris %d, verts %d, lava z %.0f..%.0f" % (TAG, len(tri) // 3, len(vs), min(v.z for v in vs), max(v.z for v in vs)))
unreal.log_warning("%s over lava %d, over dry ground %d" % (TAG, len(on), len(off)))
if on:
    g = sorted(r["bottom"] - r["lava"] for r in on)
    unreal.log_warning("%s   over lava: bottom - lava surface min %.0f median %.0f max %.0f" % (TAG, g[0], g[len(g) // 2], g[-1]))
if off:
    g = sorted(r["bottom"] - r["ground"] for r in off if r["ground"] is not None)
    unreal.log_warning("%s   over dry ground: bottom - ground min %.0f median %.0f max %.0f; > 15 cm above: %d" % (TAG, g[0], g[len(g) // 2], g[-1], sum(1 for x in g if x > 15)))
    rr = sorted(r["r"] for r in rows)
    unreal.log_warning("%s   radius from ring centre: all %.0f..%.0f; dry ones %.0f..%.0f" % (TAG, rr[0], rr[-1], min(r["r"] for r in off), max(r["r"] for r in off)))
unreal.log_warning("%s done" % TAG)
