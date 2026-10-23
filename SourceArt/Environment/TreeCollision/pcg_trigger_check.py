# Editor Python: for every PCG volume - its graph, generation trigger, and for each static-mesh spawner the tree-mesh entries
# with their collision setting (per-entry descriptor), so we know whether component edits would survive a regenerate.
import unreal
TAG = "[PCGT]"
TREES = ("SM_IslandTree_01", "SM_FirTree_01", "SM_TreeFern", "SM_BurntTrunk", "SM_TreeCycad", "SM_Cycad_01", "SM_DeadTree_01")
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
seen = set()
for a in eas.get_all_level_actors():
    if a.get_class().get_name() != "PCGVolume":
        continue
    pc = a.get_component_by_class(unreal.PCGComponent)
    g = pc.get_editor_property("graph_instance").get_editor_property("graph") if pc else None
    unreal.log_warning("%s volume %s graph=%s trigger=%s" % (TAG, a.get_actor_label(), g.get_name() if g else None,
                                                         pc.get_editor_property("generation_trigger") if pc else None))
    if not g or g.get_name() in seen:
        continue
    seen.add(g.get_name())
    for n in g.get_editor_property("nodes"):
        st = n.get_editor_property("settings_interface")
        st = st.get_settings() if hasattr(st, "get_settings") else st
        if not st or "StaticMeshSpawner" not in st.get_class().get_name():
            continue
        try:
            sel = st.get_editor_property("mesh_selector_parameters")
            for e in sel.get_editor_property("mesh_entries"):
                d = e.get_editor_property("descriptor")
                mesh = d.get_editor_property("static_mesh")
                mn = mesh.get_asset_name() if hasattr(mesh, "get_asset_name") else str(mesh)
                if any(t in str(mn) for t in TREES):
                    bi = d.get_editor_property("body_instance")
                    unreal.log_warning("%s   %s entry %s collision=%s profile=%s" % (TAG, g.get_name(), mn, bi.get_editor_property("collision_enabled"),
                                                                                  bi.get_editor_property("collision_profile_name")))
        except Exception as ex:
            unreal.log_warning("%s   %s spawner read failed: %s" % (TAG, g.get_name(), ex))
unreal.log_warning("%s done" % TAG)
