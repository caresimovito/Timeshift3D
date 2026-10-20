# Editor Python, during PIE: for Compy and Kulindadromeus - morph until we get it, put the hero back on the ground,
# let the idle play ~1 s of frames, then check the pose is spread out (head / tail away from the pelvis).
import unreal
TAG = "[SMT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
home = pawn.get_actor_location()
st = {"h": None, "todo": ["Compy", "Kulindadromeus"], "n": 0, "cur": None}


def morph_into(sp):
    for i in range(60):
        pawn.call_method("AddMorphCharge")
        pawn.call_method("StartMorph")
        if str(pawn.get_editor_property("MorphName")) == sp:
            pawn.set_actor_location(unreal.Vector(home.x, home.y, home.z + 10), False, True)
            return True
        pawn.call_method("EndMorph")
    return False


def tick(dt):
    try:
        if st["cur"] is None:
            if not st["todo"]:
                unreal.unregister_slate_post_tick_callback(st["h"])
                return
            st["cur"] = st["todo"].pop(0)
            ok = morph_into(st["cur"])
            st["n"] = 0
            if not ok:
                unreal.log_warning("%s never rolled %s" % (TAG, st["cur"]))
                st["cur"] = None
            return
        st["n"] += 1
        if st["n"] == 8:
            mb = pawn.get_editor_property("MorphBody")
            al = pawn.get_actor_location()
            pts = []
            for bn in ("pelvis", "head", "tail_04", "leg_L_lower"):
                if mb.get_bone_index(bn) >= 0:
                    p = mb.get_socket_location(bn)
                    pts.append("%s(%.0f,%.0f,%.0f)" % (bn, p.x - al.x, p.y - al.y, p.z - al.z))
            unreal.log_warning("%s %s anim=%s vis=%s cap=(%.0f,%.0f) | %s" % (TAG, st["cur"], mb.get_animation_mode(), mb.is_visible(),
                               pawn.get_editor_property("CapsuleComponent").get_unscaled_capsule_radius(),
                               pawn.get_editor_property("CapsuleComponent").get_unscaled_capsule_half_height(), " ".join(pts)))
            pawn.call_method("EndMorph")
            st["cur"] = None
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
