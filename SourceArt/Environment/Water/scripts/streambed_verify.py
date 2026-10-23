# Editor Python: ground height (landscape only) at points in the raised strip vs the pond samples from 2026-10-19.
import json
import unreal
W = unreal.EditorLevelLibrary.get_editor_world()
d = json.load(open(r"C:/agentpy/pond_Swamp_Pond_Water.json"))
nx, c = d["nx"], d["cell"]
for (x, y) in ((23500, 0), (23600, 1000), (23700, 2000), (23750, -500), (23400, 1500), (24500, 1000)):
    i, j = int(round((x - d["x0"]) / c)), int(round((y - d["y0"]) / c))
    old = d["h"][j * nx + i]
    z, ign = 3000.0, []
    now = None
    for _ in range(10):
        h = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, z), unreal.Vector(x, y, -3000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                   False, ign, unreal.DrawDebugTrace.NONE, True)
        t = h.to_tuple() if h else None
        if not t or not t[0]:
            break
        if t[10] and "Landscape" in t[10].get_name():
            now = t[4].z
            break
        ign.append(t[9])
    unreal.log_warning("[SBV] (%d,%d) old %s  now %s" % (x, y, old, None if now is None else round(now, 1)))
unreal.log_warning("[SBV] done")
