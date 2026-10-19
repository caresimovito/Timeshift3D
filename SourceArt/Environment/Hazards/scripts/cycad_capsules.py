# Editor Python: SM_TreeCycad_01/02/03 had ONE convex hull around the whole crown (up to ~19 m across once scaled) set to
# BlockAll - invisible walls under every cycad (34 RCTree actors alone, incl. the whole rockfall path). Replace with a
# trunk capsule sized from the mesh (cycad_trunk.py): you bump the trunk, walk under the fronds. Originals logged for undo.
import unreal
TAG = "[CAPS]"
EAL = unreal.EditorAssetLibrary
D = "/Game/Timeshift/Environment/Meshes/TreeCycad/"
# name: (axis x, axis y, trunk radius, trunk top z) ; trunk bottom = mesh zmin
TRUNKS = {"SM_TreeCycad_01": (-3, -8, 58, 390), "SM_TreeCycad_02": (-3, -2, 62, 240), "SM_TreeCycad_03": (0, -2, 56, 520)}
for name, (ax, ay, r, top) in TRUNKS.items():
    m = EAL.load_asset(D + name)
    bs = m.get_editor_property("body_setup")
    agg = bs.get_editor_property("agg_geom")
    unreal.log_warning("%s %s before: convex=%d sphyl=%d box=%d" % (TAG, name, len(agg.get_editor_property("convex_elems")),
                       len(agg.get_editor_property("sphyl_elems")), len(agg.get_editor_property("box_elems"))))
    zmin = m.get_bounding_box().min.z
    h = top - zmin
    e = unreal.KSphylElem()
    e.set_editor_property("center", unreal.Vector(ax, ay, zmin + h / 2))
    e.set_editor_property("rotation", unreal.Rotator(0, 0, 0))
    e.set_editor_property("radius", float(r))
    e.set_editor_property("length", float(max(0.0, h - 2 * r)))
    m.modify()
    agg.set_editor_property("convex_elems", [])
    agg.set_editor_property("box_elems", [])
    agg.set_editor_property("sphere_elems", [])
    agg.set_editor_property("sphyl_elems", [e])
    bs.set_editor_property("agg_geom", agg)
    m.set_editor_property("body_setup", bs)
    EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)
    agg2 = m.get_editor_property("body_setup").get_editor_property("agg_geom")
    s = agg2.get_editor_property("sphyl_elems")
    unreal.log_warning("%s %s after: convex=%d sphyl=%d r=%.0f len=%.0f centre z=%.0f" % (TAG, name, len(agg2.get_editor_property("convex_elems")), len(s),
                       s[0].get_editor_property("radius") if s else -1, s[0].get_editor_property("length") if s else -1,
                       s[0].get_editor_property("center").z if s else -1))
