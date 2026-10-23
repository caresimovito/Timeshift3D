# Editor Python, during PIE: drive the settings menu's SetDifficulty (console "ke * SetDifficulty N", what the buttons call)
# and log, ~1.5 s later, the hero's level, a Raptor's damage / detection / cooldown / health and the saved value. Steps
# through HARD, EASY, MEDIUM, and opens the menu at the end for a look at the new row.
import unreal
TAG = "[DIF]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
rap = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_EnemyBase_C"
       and str(a.get_editor_property("Species")) == "Raptor"][0]
STEPS = globals().get("STEPS") or [2, 0, 1]
st = {"h": None, "i": -1, "t": gt() + 2.0}


def show(label):
    hc = rap.get_component_by_class(HCC)
    sv = unreal.GameplayStatics.load_game_from_slot("ChronoshiftSettings", 0)
    unreal.log_warning("%s %s | hero level=%s | Raptor dmg=%.1f detect=%.0f cooldown=%.2f health %.0f/%.0f | saved=%s" % (
        TAG, label, pawn.get_editor_property("AttackVariety").get_editor_property("Difficulty"),
        rap.get_editor_property("AttackDamage"), rap.get_editor_property("DetectionRange"), rap.get_editor_property("AttackCooldown"),
        hc.get_editor_property("CurrentHealth"), hc.get_editor_property("MaxHealth"),
        sv.get_editor_property("Difficulty") if sv else None))


def tick(dt):
    try:
        if gt() < st["t"]:
            return
        if st["i"] < 0:
            show("start")
        else:
            show("after SetDifficulty %d" % STEPS[st["i"]])
        st["i"] += 1
        if st["i"] >= len(STEPS):
            unreal.SystemLibrary.execute_console_command(w, "ke * OpenMenu")
            unreal.log_warning("%s done" % TAG)
            unreal.unregister_slate_post_tick_callback(st["h"])
            return
        unreal.SystemLibrary.execute_console_command(w, "ke * SetDifficulty %d" % STEPS[st["i"]])
        st["t"] = gt() + 1.6
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
