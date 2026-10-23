# Editor Python, during PIE: does anything come to investigate? The (invulnerable) player walks small circles at SPOT for
# PER seconds (walking = noise 1); every 2 s log each ground enemy within 40 m: distance, Investigating flag, AnimState.
import math
import unreal
TAG = "[INV]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")
AVC = unreal.load_class(None, "/Game/Timeshift/Enemies/BP_AttackVariety.BP_AttackVariety_C")
hc = pawn.get_component_by_class(HCC)
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
PER = globals().get("PER", 24.0)
SPOT = globals().get("SPOT")
if SPOT:
    pawn.set_actor_location(unreal.Vector(SPOT[0], SPOT[1], SPOT[2]), False, True)
home = pawn.get_actor_location()
ENS = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_EnemyBase_C"]
st = {"h": None, "t0": gt(), "last": -9.0, "first": {}}


def tick(dt):
    try:
        now = gt() - st["t0"]
        try:
            hc.set_editor_property("bIsInvulnerable", True)
        except Exception:
            pass
        a = now * 1.2                                          # walk a ~4 m circle
        tgt = unreal.Vector(home.x + 200 * math.cos(a), home.y + 200 * math.sin(a), home.z)
        d = tgt - pawn.get_actor_location()
        n = math.hypot(d.x, d.y) or 1.0
        pawn.add_movement_input(unreal.Vector(d.x / n, d.y / n, 0), 0.6, False)
        if now - st["last"] >= 2.0:
            st["last"] = now
            p = pawn.get_actor_location()
            rows = []
            for e in ENS:
                if not unreal.SystemLibrary.is_valid(e):
                    continue
                dist = math.hypot(e.get_actor_location().x - p.x, e.get_actor_location().y - p.y)
                if dist > 4000:
                    continue
                c = e.get_component_by_class(AVC)
                inv = c.get_editor_property("Investigating") if c else None
                k = e.get_actor_label()
                if inv and k not in st["first"]:
                    st["first"][k] = (now, dist)
                rows.append((dist, "%s(%s) %.0fm%s st%d" % (k[:16], str(e.get_editor_property("Species"))[:6], dist / 100, " INV" if inv else "",
                                                           e.get_editor_property("AnimState"))))
            rows.sort()
            unreal.log_warning("%s t=%.0f speed=%.0f | %s" % (TAG, now, pawn.get_velocity().length(), " | ".join(r[1] for r in rows[:7])))
        if now > PER:
            unreal.log_warning("%s done; started investigating: %s" % (TAG, {k: "%.0fs at %.0fm" % (v[0], v[1] / 100) for k, v in st["first"].items()}))
            unreal.unregister_slate_post_tick_callback(st["h"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
