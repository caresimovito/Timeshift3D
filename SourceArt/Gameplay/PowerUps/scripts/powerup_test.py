# Editor Python, during PIE: grab a Fury pickup (teleport onto it + Interact), check bFuryActive / AttackDamage doubling,
# quick-throw a stone at the nearest enemy (expect a 44 DMG log line); then take 50 damage, grab a Regen herb and log
# health rising. Freezes creatures near the hero so they don't interfere.
import unreal

TAG = "[PUT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")
hc = pawn.get_component_by_class(HCC)
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
pk = {"h": None, "t0": gt(), "phase": "fury0", "last": -1}


def hp():
    for n in ("CurrentHealth", "Health"):
        try:
            return hc.get_editor_property(n)
        except Exception:
            pass


def pick(kind):
    ps = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_Pickup_%s_C" % kind]
    p = min(ps, key=lambda a: (a.get_actor_location() - pawn.get_actor_location()).length())
    l = p.get_actor_location()
    pawn.set_actor_location(unreal.Vector(l.x, l.y, l.z + 100), False, True)
    return p


def freeze():
    for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
        if a != pawn and a.is_actor_tick_enabled() and a.get_component_by_class(HCC) and (a.get_actor_location() - pawn.get_actor_location()).length() < 2500:
            a.set_actor_tick_enabled(False)


def tick(dt):
    try:
        now = gt() - pk["t0"]
        ph = pk["phase"]
        if ph == "fury0":
            pk["p"] = pick("Fury")
            pk.update(phase="fury1", t0=gt())
        elif ph == "fury1" and now > 0.4:
            freeze()
            dmg0 = pawn.get_editor_property("AttackDamage")
            pk["p"].call_method("Interact")
            pk.update(phase="fury2", t0=gt(), dmg0=dmg0)
        elif ph == "fury2" and now > 0.5:
            unreal.log_warning("%s fury active=%s attack %s -> %s light=%s" % (TAG, pawn.get_editor_property("bFuryActive"), pk["dmg0"],
                               pawn.get_editor_property("AttackDamage"), pawn.get_editor_property("FuryLight")))
            # stone throw at the nearest enemy (unfreeze nothing; it's a static target)
            pawn.call_method("QuickThrow")
            pk.update(phase="regen0", t0=gt())
        elif ph == "regen0" and now > 2.5:
            pk["p"] = pick("Regen")
            pk.update(phase="regen1", t0=gt())
        elif ph == "regen1" and now > 0.4:
            freeze()
            hc.call_method("ApplyDamage", (50.0,))
            pk["hp0"] = hp()
            pk["p"].call_method("Interact")
            pk.update(phase="regen2", t0=gt())
        elif ph == "regen2" and now - pk["last"] >= 2.0:
            pk["last"] = now
            unreal.log_warning("%s regen t=%.1f active=%s hp=%s (after hit %s)" % (TAG, now, pawn.get_editor_property("bRegenActive"), hp(), pk["hp0"]))
            if now > 22:
                unreal.log_warning("%s done fury=%s" % (TAG, pawn.get_editor_property("bFuryActive")))
                unreal.unregister_slate_post_tick_callback(pk["h"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(pk["h"])


pk["h"] = unreal.register_slate_post_tick_callback(tick)
