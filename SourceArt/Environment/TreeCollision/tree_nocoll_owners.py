# Editor Python: for each tree mesh - its simple collision (convex / capsule / box counts) and, for every placed copy with
# collision OFF, which actor / component class owns it (PCG output, foliage, placed actor), with instance counts.
import unreal
TAG = "[TNC]"
TREES = ("SM_ScorchedTree_01", "SM_BurntTrunk_01", "SM_BurntTrunk_02", "SM_BurntTrunk_03", "SM_DeadTree_01", "SM_IslandTree_01",
         "SM_FirTree_01", "SM_TreeFern", "SM_Cycad_01", "SM_TreeCycad_01", "SM_TreeCycad_02", "SM_TreeCycad_03")
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
meshes, off, on = {}, {}, {}
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        if not m or m.get_name() not in TREES:
            continue
        meshes[m.get_name()] = m
        n = c.get_instance_count() if isinstance(c, unreal.InstancedStaticMeshComponent) else 1
        key = (m.get_name(), a.get_class().get_name(), c.get_class().get_name())
        bucket = off if "NO_COLLISION" in str(c.get_collision_enabled()) else on
        bucket[key] = bucket.get(key, 0) + n
for name, m in sorted(meshes.items()):
    ag = m.get_editor_property("body_setup").get_editor_property("agg_geom")
    b = m.get_bounding_box()
    unreal.log_warning("%s %-20s %s | convex=%d capsule=%d box=%d | size %.0fx%.0fx%.0f" % (
        TAG, name, m.get_path_name().split(".")[0], len(ag.get_editor_property("convex_elems")), len(ag.get_editor_property("sphyl_elems")),
        len(ag.get_editor_property("box_elems")), b.max.x - b.min.x, b.max.y - b.min.y, b.max.z - b.min.z))
for (name, ac, cc), n in sorted(off.items()):
    unreal.log_warning("%s OFF %-20s x%-5d owner=%s comp=%s" % (TAG, name, n, ac, cc))
for (name, ac, cc), n in sorted(on.items()):
    unreal.log_warning("%s ON  %-20s x%-5d owner=%s comp=%s" % (TAG, name, n, ac, cc))
unreal.log_warning("%s done" % TAG)
