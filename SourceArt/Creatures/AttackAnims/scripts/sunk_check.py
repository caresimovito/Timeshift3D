# Editor Python, during PIE: which dinosaurs are sunk into the ground? For every ground enemy: ground height under it
# (trace from +300 cm ignoring itself), its actor origin vs that ground, and its lowest foot / toe bone vs that ground.
# Summarised per species (median foot offset) plus the worst individuals.
import unreal
TAG = "[SNK]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
rows = []
for e in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
    if e.get_class().get_name() != "BP_EnemyBase_C" or e.get_editor_property("bIsFlying") or e.get_editor_property("bDying"):
        continue
    l = e.get_actor_location()
    h = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(l.x, l.y, l.z + 300), unreal.Vector(l.x, l.y, l.z - 3000),
                                               unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [e], unreal.DrawDebugTrace.NONE, True)
    t = h.to_tuple() if h else None
    if not t or not t[0]:
        continue
    gz = t[4].z
    surf = t[10].get_name() if t[10] else "?"
    body = e.get_editor_property("Body")
    feet = []
    for b in body.get_all_socket_names():
        n = str(b).lower()
        if ("foot" in n or "toe" in n) and "arm" not in n:
            feet.append(body.get_socket_location(b).z)
    fz = min(feet) if feet else None
    rows.append((str(e.get_editor_property("Species")), e.get_actor_label(), l.z - gz, (fz - gz) if fz is not None else None, surf, l))
by = {}
for sp, lab, oz, fz, surf, l in rows:
    by.setdefault(sp, []).append(fz if fz is not None else 0)
for sp, v in sorted(by.items()):
    v = sorted(v)
    unreal.log_warning("%s %-15s n=%d lowest foot vs ground: median %+.0f cm, worst %+.0f cm" % (TAG, sp, len(v), v[len(v) // 2], v[0]))
for sp, lab, oz, fz, surf, l in sorted([r for r in rows if r[3] is not None], key=lambda r: r[3])[:10]:
    unreal.log_warning("%s   worst: %-12s %-24s origin %+.0f, feet %+.0f vs ground (%s) at (%.0f, %.0f, %.0f)" % (TAG, sp, lab, oz, fz, surf[:40], l.x, l.y, l.z))
unreal.log_warning("%s done" % TAG)
