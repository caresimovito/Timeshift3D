# Editor Python, during PIE (morphed into Psittacosaurus): sample the morph body's pose with forced LOD 1..3 and 0, and
# the enemy Psittacosaurus with forced LOD 1 (=LOD0) - is the collapse an LOD0 problem?
import unreal
TAG = "[PSL]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
mb = pawn.get_editor_property("MorphBody")
enemy = [e for e in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if e.get_class().get_name() == "BP_EnemyBase_C"
         and str(e.get_editor_property("Species")) == "Psittacosaurus"][0].get_editor_property("Body")
sk = mb.get_editor_property("skeletal_mesh_asset")
unreal.log_warning("%s LODs=%d" % (TAG, sk.get_lod_num() if hasattr(sk, "get_lod_num") else -1))
st = {"h": None, "n": 0, "lods": [1, 2, 3, 4, 0], "i": 0}


def pose(c, owner_loc):
    out = []
    for bn in ("pelvis", "head", "tail_04"):
        p = c.get_socket_location(bn)
        out.append("%s(%.0f,%.0f,%.0f)" % (bn, p.x - owner_loc.x, p.y - owner_loc.y, p.z - owner_loc.z))
    return " ".join(out)


def tick(dt):
    try:
        st["n"] += 1
        if st["n"] % 4 == 1:
            if st["i"] > 0:
                l = st["lods"][st["i"] - 1]
                unreal.log_warning("%s forced=%d predicted=%s morph: %s | enemy: %s" % (TAG, l, "-",
                                   pose(mb, pawn.get_actor_location()), pose(enemy, enemy.get_owner().get_actor_location())))
            if st["i"] >= len(st["lods"]):
                unreal.unregister_slate_post_tick_callback(st["h"])
                return
            l = st["lods"][st["i"]]
            mb.set_forced_lod(l)
            enemy.set_forced_lod(l)
            st["i"] += 1
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
