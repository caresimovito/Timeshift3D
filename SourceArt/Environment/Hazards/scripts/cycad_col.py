# Editor Python: do the RC cycad trees block the player? Mesh simple-collision shapes + per-instance Pawn/Visibility response.
import unreal
TAG = "[CYC]"
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
seen = set()
blockers = []
for a in EAS.get_all_level_actors():
    lab = a.get_actor_label()
    if not lab.startswith("RCTree"):
        continue
    smc = a.get_component_by_class(unreal.StaticMeshComponent)
    m = smc.static_mesh
    if m.get_name() not in seen:
        seen.add(m.get_name())
        bs = m.get_editor_property("body_setup")
        agg = bs.get_editor_property("agg_geom")
        b = m.get_bounding_box()
        unreal.log_warning("%s mesh %s convex=%d box=%d sphyl=%d flag=%s size=(%.0f,%.0f,%.0f)" % (TAG, m.get_name(), len(agg.get_editor_property("convex_elems")),
                           len(agg.get_editor_property("box_elems")), len(agg.get_editor_property("sphyl_elems")), bs.get_editor_property("collision_trace_flag"),
                           b.max.x - b.min.x, b.max.y - b.min.y, b.max.z - b.min.z))
    pawn = smc.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)
    if str(pawn).find("BLOCK") >= 0 and str(smc.get_collision_enabled()).find("NO_COLLISION") < 0:
        l = a.get_actor_location()
        blockers.append("%s(%.0f,%.0f s%.1f)" % (lab, l.x, l.y, a.get_actor_scale3d().x))
    if lab == "RCTree_14":
        unreal.log_warning("%s RCTree_14 profile=%s pawn=%s vis=%s enabled=%s" % (TAG, smc.get_collision_profile_name(), pawn,
                           smc.get_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY), smc.get_collision_enabled()))
unreal.log_warning("%s %d RCTree actors block Pawn: %s" % (TAG, len(blockers), " ".join(blockers)))
