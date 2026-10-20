# Editor Python, during PIE:
#  A) aimed throw: hero aiming (bIsAiming forced on for one call - real RMB can't be pressed from here), QuickBola,
#     then compare the bola's flight direction with the camera's forward / the aim point.
#  B) flyer snare: fire a bola straight at the nearest pterosaur from 3 m; log its height above ground, its root's
#     Pawn response while snared and after release.
import math
import unreal

TAG = "[BAT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
BOLA = unreal.load_class(None, "/Game/Timeshift/Weapons/BP_BolaProjectile.BP_BolaProjectile_C")
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
cam = pawn.get_editor_property("FollowCamera")
pawn.set_editor_property("BolaCount", 20)
pawn.set_editor_property("bIsAiming", True)
pawn.call_method("QuickBola")
pawn.set_editor_property("bIsAiming", False)
fw = cam.get_forward_vector()
unreal.log_warning("%s A: aimed=%s aimpoint=%s camfwd=(%.2f,%.2f,%.2f) target=%s" % (TAG, pawn.get_editor_property("bAimedThrow"),
                   pawn.get_editor_property("AimPoint"), fw.x, fw.y, fw.z, pawn.get_editor_property("ThrowTarget")))
bt = {"h": None, "t0": gt(), "phase": "A", "last": -1}


def ground_below(a):
    l = a.get_actor_location()
    h = unreal.SystemLibrary.line_trace_single(w, l, unreal.Vector(l.x, l.y, l.z - 5000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                               False, [a], unreal.DrawDebugTrace.NONE, True).to_tuple()
    return l.z - h[4].z if h[0] else None


def tick(dt):
    try:
        now = gt() - bt["t0"]
        if bt["phase"] == "A" and now > 1.15:
            bolas = unreal.GameplayStatics.get_all_actors_of_class(w, BOLA)
            if bolas:
                b = bolas[-1]
                v = b.get_velocity()
                n = max(1.0, v.length())
                unreal.log_warning("%s A: bola vel dir=(%.2f,%.2f,%.2f) speed=%.0f at %s" % (TAG, v.x / n, v.y / n, v.z / n, n, b.get_actor_location()))
            else:
                unreal.log_warning("%s A: no bola in flight" % TAG)
            # B: pick nearest flyer, hold it still, stand 8 m from it, look at it, aim + throw (as a player would)
            fl = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_EnemyBase_C"
                  and str(a.get_editor_property("Species")) in ("Pteranodon", "Tupandactylus")]
            f = min(fl, key=lambda a: (a.get_actor_location() - pawn.get_actor_location()).length())
            f.set_actor_tick_enabled(False)
            fl_ = f.get_actor_location()
            gz = fl_.z - (ground_below(f) or 0)
            pawn.set_actor_location(unreal.Vector(fl_.x - 800, fl_.y, gz + 100), False, True)
            look = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(fl_.x - 800, fl_.y, gz + 170), unreal.Vector(fl_.x, fl_.y, fl_.z + 60))
            unreal.GameplayStatics.get_player_controller(w, 0).set_control_rotation(look)
            bt.update(phase="B0", t0=gt(), f=f, last=-1)
            unreal.log_warning("%s B: flyer %s %.0f above ground, hero placed 8 m away" % (TAG, f.get_actor_label(), ground_below(f) or -1))
            return
        if bt["phase"] == "B0" and now > 0.6:
            # quick (non-aimed) throw, then force its target to the flyer before LaunchStone fires (0.97 s in)
            pawn.call_method("QuickBola")
            pawn.set_editor_property("ThrowTarget", bt["f"])
            pawn.set_editor_property("bAimedThrow", False)
            bt.update(phase="B", t0=gt(), last=-1)
            return
        HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")
        for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
            if a != pawn and a != bt.get("f") and a.is_actor_tick_enabled() and a.get_component_by_class(HCC) and (a.get_actor_location() - pawn.get_actor_location()).length() < 3000:
                a.set_actor_tick_enabled(False)
        if bt["phase"] == "B" and now - bt["last"] >= 0.5:
            bt["last"] = now
            f = bt["f"]
            root = f.get_component_by_class(unreal.StaticMeshComponent)
            unreal.log_warning("%s B t=%.1f %s above_ground=%s tick=%s pawn_resp=%s" % (TAG, now, f.get_actor_label(), ground_below(f),
                               f.is_actor_tick_enabled(), str(root.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)).split(".")[-1]))
            if now > 6.5:
                unreal.unregister_slate_post_tick_callback(bt["h"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(bt["h"])


bt["h"] = unreal.register_slate_post_tick_callback(tick)
