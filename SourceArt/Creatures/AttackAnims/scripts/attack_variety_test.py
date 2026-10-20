# Editor Python, during PIE: hero invulnerable, placed beside the nearest group of ground dinosaurs; every ~1 s log, for
# enemies within 25 m: species, AnimState and the AttackVariety component's WasProvoked / Pick; tally how many attacks
# started, how many swapped in an authored move, how many roars fired.
import unreal
TAG = "[AVT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")
AVC = unreal.load_class(None, "/Game/Timeshift/Enemies/BP_AttackVariety.BP_AttackVariety_C")
hc = pawn.get_component_by_class(HCC)
try:
    hc.set_editor_property("bIsInvulnerable", True)
except Exception as e:
    unreal.log_warning("%s invuln: %s" % (TAG, e))
FLY = ("Pteranodon", "Tupandactylus", "Dimorphodon", "Pterosaur")
target = globals().get("TARGET_SP", "Raptor")
en = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_EnemyBase_C"
      and str(a.get_editor_property("Species")) == target]
e0 = en[0]
l = e0.get_actor_location()
pawn.set_actor_location(unreal.Vector(l.x - 600, l.y, l.z + 120), False, True)
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
st = {"h": None, "t0": gt(), "last": -1, "prev": {}, "attacks": 0, "swaps": 0, "roars": 0}


def tick(dt):
    try:
        now = gt() - st["t0"]
        if hc.get_editor_property("CurrentHealth") < 60:
            hc.call_method("Heal", (100.0,))
        near = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_EnemyBase_C"
                and str(a.get_editor_property("Species")) not in FLY and (a.get_actor_location() - pawn.get_actor_location()).length() < 2500]
        for a in near:
            c = a.get_component_by_class(AVC)
            if not c:
                continue
            k = a.get_actor_label()
            s = a.get_editor_property("AnimState")
            pv = st["prev"].get(k, (s, False))
            prov = c.get_editor_property("WasProvoked")
            if s == 2 and pv[0] != 2:
                st["attacks"] += 1
                if c.get_editor_property("Pick") > 0:
                    st["swaps"] += 1
            if prov and not pv[1]:
                st["roars"] += 1
            st["prev"][k] = (s, prov)
        if now - st["last"] >= 3.0:
            st["last"] = now
            unreal.log_warning("%s t=%.0f near=%d attacks=%d swapped=%d roars=%d | %s" % (TAG, now, len(near), st["attacks"], st["swaps"], st["roars"],
                               ", ".join("%s:st%d p%d" % (str(a.get_editor_property("Species"))[:6], a.get_editor_property("AnimState"),
                                                         a.get_component_by_class(AVC).get_editor_property("Pick")) for a in near[:6] if a.get_component_by_class(AVC))))
        if now > 40:
            unreal.unregister_slate_post_tick_callback(st["h"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
