# Editor Python, during PIE (morphed into Psittacosaurus): play the morph's own anim objects (MorphIdle/Walk/Run/Attack)
# on the morph body and sample the pose; and read what the enemy Psittacosaurus is actually playing.
import unreal
TAG = "[PSC]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
mb = pawn.get_editor_property("MorphBody")
enemy = [e for e in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if e.get_class().get_name() == "BP_EnemyBase_C"
         and str(e.get_editor_property("Species")) == "Psittacosaurus"][0].get_editor_property("Body")
sni = enemy.get_single_node_instance() if hasattr(enemy, "get_single_node_instance") else None
ea = sni.get_animation_asset() if sni and hasattr(sni, "get_animation_asset") else None
unreal.log_warning("%s enemy plays %s (%s)" % (TAG, ea.get_path_name() if ea else None, type(ea).__name__ if ea else None))
clips = [(n, pawn.get_editor_property(n)) for n in ("MorphIdle", "MorphWalk", "MorphRun", "MorphAttack")]
if ea:
    clips.append(("enemy's", ea))
st = {"h": None, "n": 0, "i": 0}


def tick(dt):
    try:
        st["n"] += 1
        if st["n"] % 4 == 1:
            if st["i"] > 0:
                n, a = clips[st["i"] - 1]
                al = pawn.get_actor_location()
                pts = []
                for bn in ("pelvis", "head", "tail_04"):
                    p = mb.get_socket_location(bn)
                    pts.append("%s(%.0f,%.0f,%.0f)" % (bn, p.x - al.x, p.y - al.y, p.z - al.z))
                unreal.log_warning("%s %s=%s | %s" % (TAG, n, a.get_name() if a else None, " ".join(pts)))
            if st["i"] >= len(clips):
                unreal.unregister_slate_post_tick_callback(st["h"])
                return
            mb.play_animation(clips[st["i"]][1], True)
            st["i"] += 1
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
