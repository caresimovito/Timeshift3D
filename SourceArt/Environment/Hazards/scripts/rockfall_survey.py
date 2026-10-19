# Editor Python: what's in the rockfall area (x 48000-53000, y -2000..3500): actors with mesh, location, bounds, collision;
# plus a coarse landscape height grid so we can see the cliff and the path below it.
import unreal

TAG = "[RFS]"
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()
rows = []
for a in EAS.get_all_level_actors():
    l = a.get_actor_location()
    if 48000 < l.x < 53000 and -2000 < l.y < 3500:
        mesh = ""
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        if smc and smc.static_mesh:
            mesh = smc.static_mesh.get_name() + " col=" + str(smc.get_collision_enabled()).split(".")[-1].split(":")[0]
        o, e = a.get_actor_bounds(False)
        rows.append("%s | %s | (%.0f,%.0f,%.0f) ext=(%.0f,%.0f,%.0f) | %s | %s" % (a.get_actor_label(), a.get_class().get_name(), l.x, l.y, l.z,
                    e.x, e.y, e.z, mesh, a.get_folder_path()))
for r in sorted(rows):
    unreal.log_warning("%s %s" % (TAG, r))
unreal.log_warning("%s %d actors" % (TAG, len(rows)))


def ground(x, y):
    ign = []
    for _ in range(10):
        h = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, 8000), unreal.Vector(x, y, -3000),
                                                   unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ign, unreal.DrawDebugTrace.NONE, True)
        t = h.to_tuple() if h else None
        if not t or not t[0] or not t[9]:
            return None
        if "Landscape" in type(t[9]).__name__:
            return t[4].z
        ign.append(t[9])


for y in range(3000, -2001, -500):
    zs = []
    for x in range(48000, 53001, 500):
        g = ground(x, y)
        zs.append("%5s" % ("-" if g is None else int(g)))
    unreal.log_warning("%s y=%5d %s" % (TAG, y, " ".join(zs)))
unreal.log_warning("%s x cols 48000..53000 step 500" % TAG)
