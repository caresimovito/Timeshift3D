# Editor Python: give tree meshes a trunk-only capsule (user 2026-10-21: "add trunk collision to those trees").
# FirTree / IslandTree had NO simple collision (everyone walked through); TreeFern and the BurntTrunks had one hull wrapped
# round branches / fronds (invisible walls). Sizes from tree_trunks_measure.py (lower-band vertex radii, trunk top = where
# the radius jumps). Same method as cycad_capsules.py. The old simple shapes are logged first, for undo.
import unreal
TAG = "[TCAP]"
EAL = unreal.EditorAssetLibrary
# name: (path, trunk radius, trunk top as a fraction of mesh height above zmin)
TRUNKS = {"SM_FirTree_01": ("/Game/Timeshift/Environment/Meshes/FirTree/SM_FirTree_01", 22, 0.30),
          "SM_IslandTree_01": ("/Game/Timeshift/Environment/Meshes/IslandTree/SM_IslandTree_01", 35, 0.36),
          "SM_TreeFern": ("/Game/Timeshift/Environment/Meshes/Jungle/TreeFern/TreeFern/StaticMeshes/SM_TreeFern", 22, 0.70),
          "SM_BurntTrunk_01": ("/Game/Timeshift/Environment/Meshes/AshForest/SM_BurntTrunk_01", 80, 0.35),
          "SM_BurntTrunk_02": ("/Game/Timeshift/Environment/Meshes/AshForest/SM_BurntTrunk_02", 70, 0.30),
          "SM_BurntTrunk_03": ("/Game/Timeshift/Environment/Meshes/AshForest/SM_BurntTrunk_03", 95, 0.30)}
AXIS = {"SM_FirTree_01": (-3, 0), "SM_IslandTree_01": (1, -8), "SM_TreeFern": (4, -3), "SM_BurntTrunk_01": (-5, 6),
        "SM_BurntTrunk_02": (7, 0), "SM_BurntTrunk_03": (9, 20)}
for name, (path, r, topf) in TRUNKS.items():
    m = EAL.load_asset(path)
    bs = m.get_editor_property("body_setup")
    agg = bs.get_editor_property("agg_geom")
    unreal.log_warning("%s %s before: convex=%d sphyl=%d box=%d sphere=%d" % (TAG, name, len(agg.get_editor_property("convex_elems")),
                       len(agg.get_editor_property("sphyl_elems")), len(agg.get_editor_property("box_elems")), len(agg.get_editor_property("sphere_elems"))))
    b = m.get_bounding_box()
    zmin, h = b.min.z, b.max.z - b.min.z
    top = zmin + topf * h
    hh = max(2.0 * r, top - zmin)
    e = unreal.KSphylElem()
    e.set_editor_property("center", unreal.Vector(AXIS[name][0], AXIS[name][1], zmin + hh / 2))
    e.set_editor_property("rotation", unreal.Rotator(0, 0, 0))
    e.set_editor_property("radius", float(r))
    e.set_editor_property("length", float(max(0.0, hh - 2 * r)))
    m.modify()
    agg.set_editor_property("convex_elems", [])
    agg.set_editor_property("box_elems", [])
    agg.set_editor_property("sphere_elems", [])
    agg.set_editor_property("sphyl_elems", [e])
    bs.set_editor_property("agg_geom", agg)
    bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
    m.set_editor_property("body_setup", bs)
    EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)
    s = m.get_editor_property("body_setup").get_editor_property("agg_geom").get_editor_property("sphyl_elems")
    unreal.log_warning("%s %s after: capsule r=%.0f, from z %.0f to %.0f" % (TAG, name, s[0].get_editor_property("radius") if s else -1, zmin, zmin + hh))
unreal.log_warning("%s done" % TAG)
