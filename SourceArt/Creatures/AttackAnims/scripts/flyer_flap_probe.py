# Editor Python (during PIE): per flyer - AnimState, the attack component's FlyFlapping, and the left humerus angle in
# component space. Run a few times a second or two apart: a flapping wing changes angle between samples (2026-10-22).
import math
import unreal
W = unreal.EditorLevelLibrary.get_game_world()
TAG = "[FLAP]"
if not W:
    unreal.log_warning("%s no PIE world" % TAG)
else:
    for a in unreal.GameplayStatics.get_all_actors_of_class(W, unreal.Actor):
        if not a.get_class().get_name().startswith("BP_Enemy"):
            continue
        try:
            sp = str(a.get_editor_property("Species"))
        except Exception:
            continue
        if sp not in ("Pteranodon", "Tupandactylus", "Dimorphodon", "Pterosaur"):
            continue
        body = [c for c in a.get_components_by_class(unreal.SkeletalMeshComponent)]
        av = [c for c in a.get_components_by_class(unreal.ActorComponent) if "AttackVariety" in c.get_class().get_name()]
        ang = None
        if body:
            bn = "wing_l_humerus" if body[0].get_bone_index("wing_l_humerus") >= 0 else "wing_l_upper"
            r = body[0].get_socket_transform(bn, unreal.RelativeTransformSpace.RTS_COMPONENT).rotation.rotator()
            ang = (round(r.roll), round(r.pitch), round(r.yaw))
        fl = av[0].get_editor_property("FlyFlapping") if av else None
        pl = unreal.GameplayStatics.get_player_pawn(W, 0)
        dist = a.get_distance_to(pl) / 100.0 if pl else -1
        rend = body[0].was_recently_rendered(0.5) if body else None
        unreal.log_warning("%s %-12s %-14s state %2d flapping %s humerus %s on-screen %s dist %.0f m t=%.1f" % (TAG,
                           a.get_actor_label()[:12], sp, a.get_editor_property("AnimState"), fl, ang, rend, dist,
                           unreal.GameplayStatics.get_time_seconds(W)))
