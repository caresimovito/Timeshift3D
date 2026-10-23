# Editor Python, during PIE: is the game paused, and do the dinosaurs animate when ON SCREEN? For each species in SP, stand
# the (invulnerable) player 5 m from one individual looking at it, wait 1 s, then sample head / foot / tail positions in
# the actor's frame for 3 s. Bone spread ~0 = statue; a walking or idling dinosaur moves its bones several cm or more.
import math
import time
import unreal
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
pc = unreal.GameplayStatics.get_player_controller(w, 0)
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
SP = globals().get("SP") or ["Kulindadromeus", "Psittacosaurus", "Caudipteryx", "Archaeoceratops", "Raptor"]
unreal.log_warning("[AA2] paused=%s time dilation=%s" % (unreal.GameplayStatics.is_game_paused(w), unreal.GameplayStatics.get_global_time_dilation(w)))
pick = []
for s in SP:
    for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
        if a.get_class().get_name() == "BP_EnemyBase_C" and str(a.get_editor_property("Species")) == s:
            pick.append((s, a))
            break
st = {"h": None, "i": -1, "t0": 0.0, "rel": [], "w0": time.time(), "g0": gt(), "pos": []}


def frame_pts(e):
    b = e.get_editor_property("Body")
    l = e.get_actor_location()
    yaw = math.radians(e.get_actor_rotation().yaw)
    out = []
    for n in ("head", "leg_L_foot", "tail_06"):
        p = b.get_socket_location(n)
        x, y, z = p.x - l.x, p.y - l.y, p.z - l.z
        out.append((x * math.cos(-yaw) - y * math.sin(-yaw), x * math.sin(-yaw) + y * math.cos(-yaw), z))
    return out


def start(i):
    s, e = pick[i]
    l = e.get_actor_location()
    pawn.set_actor_location(unreal.Vector(l.x - 450, l.y - 150, l.z + 150), False, True)
    st["shot"] = False
    st.update(t0=gt(), rel=[], pos=[])


def tick(dt):
    try:
        try:
            pawn.get_component_by_class(unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")).set_editor_property("bIsInvulnerable", True)
        except Exception:
            pass
        if st["i"] < 0:
            st["i"] = 0
            start(0)
            return
        s, e = pick[st["i"]]
        el = gt() - st["t0"]
        lk = unreal.MathLibrary.find_look_at_rotation(pawn.get_actor_location(), e.get_actor_location())
        pc.set_control_rotation(unreal.Rotator(pitch=-12, yaw=lk.yaw, roll=0))
        if globals().get("SHOOT") and el > 2.5 and not st["shot"]:
            unreal.SystemLibrary.execute_console_command(w, "HighResShot 1280x720")
            st["shot"] = True
        if el > 1.0:
            st["rel"].append(frame_pts(e))
            l = e.get_actor_location()
            st["pos"].append((l.x, l.y))
        if el > 4.0:
            spread = max(max(math.dist(a[k], b[k]) for a in st["rel"] for b in st["rel"]) for k in range(3)) if st["rel"] else -1
            b = e.get_editor_property("Body")
            unreal.log_warning("[AA2] %-15s on screen: bone spread %.1f cm over %d samples | moved %.0f cm | AnimState %s | body visible %s rel z %.1f" % (
                s, spread, len(st["rel"]), math.dist(st["pos"][0], st["pos"][-1]) if st["pos"] else -1, e.get_editor_property("AnimState"),
                b.is_visible(), b.get_editor_property("relative_location").z))
            st["i"] += 1
            if st["i"] >= len(pick):
                unreal.log_warning("[AA2] done; game time ran %.1f s in %.1f s real" % (gt() - st["g0"], time.time() - st["w0"]))
                unreal.unregister_slate_post_tick_callback(st["h"])
                return
            start(st["i"])
    except Exception as ex:
        unreal.log_warning("[AA2] error %s" % ex)
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
