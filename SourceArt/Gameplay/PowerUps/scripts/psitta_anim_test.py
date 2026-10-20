# Editor Python, during PIE: morph until Psittacosaurus, let MorphTick run its idle for ~1.5 s of frames, then sample the
# pose (bones relative to the actor), the anim mode and what single-node anim is playing.
import unreal
TAG = "[PSA]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
for i in range(40):
    pawn.call_method("AddMorphCharge")
    pawn.call_method("StartMorph")
    if str(pawn.get_editor_property("MorphName")) == "Psittacosaurus":
        break
    pawn.call_method("EndMorph")
pa = {"h": None, "n": 0}


def sample(tag):
    mb = pawn.get_editor_property("MorphBody")
    al = pawn.get_actor_location()
    pts = []
    for b in ("SK_Psittacosaurus1", "root", "pelvis", "head", "tail_04", "leg_L_lower"):
        p = mb.get_socket_location(b)
        pts.append("%s(%.0f,%.0f,%.0f)" % (b, p.x - al.x, p.y - al.y, p.z - al.z))
    unreal.log_warning("%s %s mode=%s state=%s pos=%s scale=%s | %s" % (TAG, tag, mb.get_animation_mode(), pawn.get_editor_property("MorphAnimState"),
                       mb.get_position() if hasattr(mb, "get_position") else "?", mb.get_world_scale(), " ".join(pts)))


def tick(dt):
    try:
        pa["n"] += 1
        if pa["n"] in (1, 6, 15):
            sample("frame %d" % pa["n"])
        if pa["n"] > 15:
            unreal.unregister_slate_post_tick_callback(pa["h"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(pa["h"])


pa["h"] = unreal.register_slate_post_tick_callback(tick)
