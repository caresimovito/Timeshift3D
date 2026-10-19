# Editor Python: (1) visible cliff lip (complex traces, ignoring the RCTree canopies) per x; (2) landscape-only height grid
# over the rockfall path (x 48600..52000, y -800..1800, step 100) -> C:/agentpy/rockfall_grid.json for BP_Rockfall.
import json
import unreal

TAG = "[RFG]"
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()
trees = [a for a in EAS.get_all_level_actors() if a.get_actor_label().startswith(("RCTree", "Tupandactylus"))]


def trace(x, y, z0=5000, ign=None, complex_=True):
    h = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, z0), unreal.Vector(x, y, -3000),
                                               unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, complex_, ign or [], unreal.DrawDebugTrace.NONE, True).to_tuple()
    return (h[4].z, h[9]) if h[0] else (None, None)


def land(x, y):
    ign = []
    for _ in range(12):
        z, a = trace(x, y, ign=ign, complex_=False)
        if a is None:
            return None
        if "Landscape" in type(a).__name__:
            return z
        ign.append(a)
    return None


for x in range(49000, 51801, 400):
    prof = []
    for y in range(2400, 899, -100):
        z, a = trace(x, y, ign=trees)
        prof.append("%d:%s:%s" % (y, "-" if z is None else int(z), (a.get_actor_label() if a else "")[:14]))
    unreal.log_warning("%s x=%d %s" % (TAG, x, " ".join(prof[::2])))

X0, Y0, S, NX, NY = 48600.0, -800.0, 100.0, 35, 27
hs = []
for j in range(NY):
    for i in range(NX):
        z = land(X0 + i * S, Y0 + j * S)
        hs.append(round(z, 1) if z is not None else 0.0)
json.dump({"x0": X0, "y0": Y0, "step": S, "nx": NX, "ny": NY, "h": hs}, open(r"C:/agentpy/rockfall_grid.json", "w"))
unreal.log_warning("%s grid %dx%d min %.0f max %.0f" % (TAG, NX, NY, min(hs), max(hs)))
