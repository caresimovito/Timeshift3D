# Editor Python (not PIE): which tree-like meshes in the level block movement? Groups every static mesh (plain actors,
# instanced / PCG components) whose mesh name looks like a tree / palm / cycad / trunk / log by mesh, with its collision
# setup: instance count, collision enabled, whether the mesh has simple collision bodies, and whether it blocks Pawn.
import json
import unreal
TAG = "[TCS]"
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
KEYS = ("tree", "palm", "cycad", "trunk", "log", "fern", "conifer", "ginkgo", "araucaria", "sequoia", "bush", "shrub", "stump")
agg = {}
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        if not m:
            continue
        n = m.get_name()
        if not any(k in n.lower() for k in KEYS):
            continue
        cnt = c.get_instance_count() if isinstance(c, unreal.InstancedStaticMeshComponent) else 1
        e = agg.setdefault(n, {"n": 0, "coll": set(), "pawn": set(), "simple": None, "complex_as_simple": None})
        e["n"] += cnt
        e["coll"].add(str(c.get_collision_enabled()).split(".")[-1].split(":")[0])
        e["pawn"].add(str(c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)).split(".")[-1].split(":")[0])
        if e["simple"] is None:
            try:
                bs = m.get_editor_property("body_setup")
                ag = bs.get_editor_property("agg_geom")
                e["simple"] = len(ag.get_editor_property("convex_elems")) + len(ag.get_editor_property("box_elems")) + \
                    len(ag.get_editor_property("sphyl_elems")) + len(ag.get_editor_property("sphere_elems"))
                e["complex_as_simple"] = str(bs.get_editor_property("collision_trace_flag")).split(".")[-1].split(":")[0]
            except Exception as ex:
                e["simple"] = "?%s" % ex
out = {k: dict(v, coll=sorted(v["coll"]), pawn=sorted(v["pawn"])) for k, v in agg.items()}
json.dump(out, open(r"C:/agentpy/tree_collision.json", "w"), indent=1)
for k, v in sorted(out.items(), key=lambda kv: -kv[1]["n"]):
    unreal.log_warning("%s %-34s x%-5d collision=%s pawn=%s simpleShapes=%s trace=%s" % (TAG, k, v["n"], v["coll"], v["pawn"], v["simple"], v["complex_as_simple"]))
unreal.log_warning("%s done %d meshes" % (TAG, len(out)))
