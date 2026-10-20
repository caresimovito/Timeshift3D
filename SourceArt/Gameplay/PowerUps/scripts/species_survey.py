# Editor Python: one placed BP_EnemyBase per ground species: Body skeletal mesh, Body relative transform, root (collider)
# scale, net body scale, mesh bounds (net size), and the stats on the instance.
import unreal
TAG = "[SPS]"
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
FLY = ("Pteranodon", "Tupandactylus", "Dimorphodon", "Pterosaur")
seen = {}
for a in EAS.get_all_level_actors():
    if a.get_class().get_name() != "BP_EnemyBase_C":
        continue
    sp = str(a.get_editor_property("Species"))
    if sp in FLY or sp in seen:
        continue
    seen[sp] = a
for sp, a in sorted(seen.items()):
    body = a.get_editor_property("Body")
    root = a.root_component
    rs = root.get_editor_property("relative_scale3d")
    bs = body.get_editor_property("relative_scale3d")
    bl = body.get_editor_property("relative_location")
    br = body.get_editor_property("relative_rotation")
    sk = body.get_editor_property("skeletal_mesh_asset") if hasattr(body, "skeletal_mesh_asset") else body.get_editor_property("skeletal_mesh")
    bb = sk.get_bounds().box_extent if sk else None
    stats = []
    for p in ("MaxHealthOverride", "AttackDamage", "MoveSpeed", "AttackRange", "AttackCooldown", "bUseSpeciesDefaults"):
        try:
            stats.append("%s=%s" % (p, a.get_editor_property(p)))
        except Exception:
            pass
    unreal.log_warning("%s %s | %s | body loc=(%.0f,%.0f,%.0f) rot=(p%.0f y%.0f r%.0f) | root=(%.2f,%.2f,%.2f) body=(%.3f,%.3f,%.3f) net=(%.2f,%.2f,%.2f) | ext=%s | %s" % (
        TAG, sp, sk.get_path_name() if sk else None, bl.x, bl.y, bl.z, br.pitch, br.yaw, br.roll, rs.x, rs.y, rs.z, bs.x, bs.y, bs.z,
        rs.x * bs.x, rs.y * bs.y, rs.z * bs.z, ("(%.0f,%.0f,%.0f)" % (bb.x, bb.y, bb.z)) if bb else None, " ".join(stats)))
