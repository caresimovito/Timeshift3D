# Editor Python: candidate falling-rock meshes: path, bounds, simple collision count (physics needs simple shapes), nanite.
import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
seen = set()
for a in EAS.get_all_level_actors():
    smc = a.get_component_by_class(unreal.StaticMeshComponent)
    if not smc or not smc.static_mesh:
        continue
    m = smc.static_mesh
    n = m.get_name()
    if n in seen or not any(k in n for k in ("Boulder", "Scree", "RiverBoulder", "Rock")):
        continue
    seen.add(n)
    bs = m.get_editor_property("body_setup")
    agg = bs.get_editor_property("agg_geom") if bs else None
    cnt = (len(agg.get_editor_property("convex_elems")), len(agg.get_editor_property("box_elems")), len(agg.get_editor_property("sphere_elems"))) if agg else None
    b = m.get_bounding_box()
    unreal.log_warning("[RMC] %s | %s | size=(%.0f,%.0f,%.0f) | convex/box/sphere=%s | flag=%s" % (n, m.get_path_name(), b.max.x - b.min.x, b.max.y - b.min.y,
                       b.max.z - b.min.z, cnt, bs.get_editor_property("collision_trace_flag") if bs else None))
