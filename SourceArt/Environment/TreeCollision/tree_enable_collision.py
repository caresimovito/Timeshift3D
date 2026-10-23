# Editor Python: switch collision ON (BlockAll) for every placed copy of the trunk-capsule trees that had it off -
# PCG-scattered instanced components and plain placed StaticMeshActors. With trunk-only capsules this blocks trunks, not
# crowns. MODE='list' only counts. Logs each change (owner, component, instances) for undo.
import unreal
TAG = "[TEN]"
TREES = ("SM_FirTree_01", "SM_IslandTree_01", "SM_TreeFern", "SM_TreeCycad_01", "SM_TreeCycad_02", "SM_TreeCycad_03")
mode = globals().get("MODE", "apply")
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
n_comp = n_inst = 0
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        if not m or m.get_name() not in TREES or "NO_COLLISION" not in str(c.get_collision_enabled()):
            continue
        k = c.get_instance_count() if isinstance(c, unreal.InstancedStaticMeshComponent) else 1
        n_comp += 1
        n_inst += k
        unreal.log_warning("%s %s %s / %s (%s) x%d" % (TAG, "would enable" if mode == "list" else "enable", a.get_actor_label(), c.get_name(), m.get_name(), k))
        if mode != "list":
            a.modify()
            c.modify()
            c.set_collision_profile_name("BlockAll")
            c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
unreal.log_warning("%s done: %d components, %d tree copies" % (TAG, n_comp, n_inst))
