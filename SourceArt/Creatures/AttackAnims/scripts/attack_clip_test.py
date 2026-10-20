# Editor Python, during PIE: morph until Raptor, then play each new clip on the morph body for ~0.5 s and sample the pose
# (head / tail_06 / pelvis vs actor) - spread out and moving, not collapsed.
import unreal
TAG = "[ACT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
SP = globals().get("TEST_SP", "Raptor")
home = pawn.get_actor_location()
for i in range(80):
    pawn.call_method("AddMorphCharge")
    pawn.call_method("StartMorph")
    if str(pawn.get_editor_property("MorphName")) == SP:
        break
    pawn.call_method("EndMorph")
pawn.set_actor_location(unreal.Vector(home.x, home.y, home.z + 10), False, True)
mb = pawn.get_editor_property("MorphBody")
clips = []
for m in ("TailSwipe", "Charge", "Pounce", "Roar"):
    n = "SK_%s_Anim_SK_%s_%s" % (SP, SP, m)
    a = unreal.load_object(None, "/Game/Timeshift/Enemies/%s/%s.%s" % (SP, n, n))
    clips.append((m, a))
st = {"h": None, "n": 0, "i": 0}


def tick(dt):
    try:
        pawn.set_editor_property("MorphAttackEnd", 1e9) if False else None
        st["n"] += 1
        if st["n"] % 5 == 1:
            if st["i"] > 0:
                m, a = clips[st["i"] - 1]
                al = pawn.get_actor_location()
                pts = ["%s(%.0f,%.0f,%.0f)" % (b, *(lambda p: (p.x - al.x, p.y - al.y, p.z - al.z))(mb.get_socket_location(b))) for b in ("pelvis", "head", "tail_06")]
                unreal.log_warning("%s %s %s loaded=%s len=%.2f | %s" % (TAG, SP, m, a is not None, a.get_play_length() if a else -1, " ".join(pts)))
            if st["i"] >= len(clips):
                pawn.call_method("EndMorph")
                unreal.unregister_slate_post_tick_callback(st["h"])
                return
            if clips[st["i"]][1]:
                mb.play_animation(clips[st["i"]][1], True)
            st["i"] += 1
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
