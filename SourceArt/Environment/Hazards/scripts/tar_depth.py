# Editor Python: landscape height under each tar cell -> depth below the tar surface (-3.5); histogram.
import json
import unreal

W = unreal.EditorLevelLibrary.get_editor_world()
cells = json.load(open(r"C:/agentpy/tar_cells.json"))["cells"]


def ground(x, y):
    ign = []
    for _ in range(10):
        h = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, 3000), unreal.Vector(x, y, -3000),
                                                   unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ign, unreal.DrawDebugTrace.NONE, True)
        t = h.to_tuple() if h else None
        if not t or not t[0] or not t[9]:
            return None
        if "Landscape" in type(t[9]).__name__:
            return t[4].z
        ign.append(t[9])
    return None


deps = [(-3.5 - g) for g in (ground(x, y) for x, y in cells) if g is not None]
deps.sort()
n = len(deps)
unreal.log_warning("[TARD] n=%d min=%.0f p25=%.0f median=%.0f p75=%.0f max=%.0f" % (n, deps[0], deps[n // 4], deps[n // 2], deps[3 * n // 4], deps[-1]))
