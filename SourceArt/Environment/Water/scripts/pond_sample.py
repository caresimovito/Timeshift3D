# Editor Python: sample ground height (ignoring the pond's own water mesh) on a grid over each pond's bounds + MARGIN cm,
# plus whether each grid point is under the current water mesh. Writes C:/agentpy/pond_<label>.json for the Blender builder.
import json
import unreal

TAG = "[PSAMP]"
W = unreal.EditorLevelLibrary.get_editor_world()
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
CFG = {"Swamp_Pond_Water": 100.0}
MARGIN = 600.0
for a in EAS.get_all_level_actors():
    lab = a.get_actor_label()
    if lab not in CFG:
        continue
    cell = CFG[lab]
    o, e = a.get_actor_bounds(False)
    surf = o.z + e.z
    x0, y0 = o.x - e.x - MARGIN, o.y - e.y - MARGIN
    nx, ny = int((2 * e.x + 2 * MARGIN) / cell) + 1, int((2 * e.y + 2 * MARGIN) / cell) + 1
    comp = a.static_mesh_component
    hs, inside = [], []
    for j in range(ny):
        for i in range(nx):
            x, y = x0 + i * cell, y0 + j * cell
            # terrain only: walk the multi-trace hits and take the first landscape hit (props like lily pads, logs and
            # cattails sit at/above the waterline and must not count as ground)
            ign = [a]
            gz = None
            top = surf + 3000
            for _ in range(10):
                hh = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, top), unreal.Vector(x, y, surf - 3000),
                                                            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ign, unreal.DrawDebugTrace.NONE, True)
                tt = hh.to_tuple() if hh else None
                if not tt or not tt[0]:
                    break
                if tt[9] and "Landscape" in type(tt[9]).__name__:
                    gz = tt[4].z
                    break
                if tt[9]:
                    ign.append(tt[9])
                else:
                    break
            hs.append(round(gz, 1) if gz is not None else None)
            wh = comp.line_trace_component(unreal.Vector(x, y, surf + 50), unreal.Vector(x, y, surf - 50), True, False, False)
            inside.append(1 if (wh and wh[0]) else 0)
    json.dump({"label": lab, "surf": surf, "x0": x0, "y0": y0, "cell": cell, "nx": nx, "ny": ny, "h": hs, "inside": inside},
              open(r"C:/agentpy/pond_%s.json" % lab, "w"))
    unreal.log_warning("%s %s grid %dx%d cell %.0f surf %.1f inside=%d" % (TAG, lab, nx, ny, cell, surf, sum(inside)))
