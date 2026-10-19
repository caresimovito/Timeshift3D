# Editor Python: trace columns across the cliff front: for each x, going south (y decreasing) find the last y where the
# top hit is still high (>250) — that's the lip. Logs per-x: lip y, lip z, what was hit; plus floor z just south of it.
import unreal

TAG = "[LIP]"
W = unreal.EditorLevelLibrary.get_editor_world()


def top(x, y):
    h = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, 5000), unreal.Vector(x, y, -3000),
                                               unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True).to_tuple()
    return (h[4].z, h[9].get_actor_label() if h[9] else "?") if h[0] else (None, None)


for x in range(49000, 52001, 400):
    prof = []
    lip = None
    for y in range(2600, 599, -100):
        z, who = top(x, y)
        prof.append((y, z, who))
    for i, (y, z, who) in enumerate(prof):
        if z is not None and z > 250 and (i + 1 < len(prof)) and (prof[i + 1][1] is None or prof[i + 1][1] < 250):
            lip = (y, z, who, prof[i + 1][1], prof[i + 1][2])
            break
    unreal.log_warning("%s x=%d lip=%s | profile %s" % (TAG, x, lip, " ".join("%d:%s:%s" % (y, "-" if z is None else int(z), (who or "")[:22]) for y, z, who in prof[::2])))
