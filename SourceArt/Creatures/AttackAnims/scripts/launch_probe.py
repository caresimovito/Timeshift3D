# Editor Python, during PIE: does LaunchCharacter on the player survive? 1) a plain launch, 2) damage then launch (what a move
# hit does). Logs velocity and movement mode for 12 frames after each.
import unreal
TAG = "[LNP]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")
hc = pawn.get_component_by_class(HCC)
cmc = pawn.get_component_by_class(unreal.CharacterMovementComponent)
st = {"h": None, "n": 0, "case": 0}
CASES = [("plain 500 fwd + 250 up", False), ("damage 5 then launch", True), ("jump", None)]


def tick(dt):
    try:
        st["n"] += 1
        if st["n"] == 5:
            name, dmg = CASES[st["case"]]
            if dmg is None:
                pawn.jump()
            else:
                if dmg:
                    hc.call_method("ApplyDamage", (5.0,))
                f = pawn.get_actor_forward_vector()
                pawn.launch_character(unreal.Vector(f.x * 500, f.y * 500, 250), True, True)
            unreal.log_warning("%s --- %s | cmc active=%s tick=%s ctrl=%s jumpZ=%.0f gravity=%.2f" % (
                TAG, name, cmc.is_active(), cmc.is_component_tick_enabled(), pawn.get_controller().get_name() if pawn.get_controller() else None,
                cmc.jump_z_velocity, cmc.gravity_scale))
        elif 5 < st["n"] <= 17:
            v = pawn.get_velocity()
            unreal.log_warning("%s   +%d v=(%.0f,%.0f,%.0f) mode=%s dil=%.2f" % (TAG, st["n"] - 5, v.x, v.y, v.z, cmc.movement_mode, pawn.custom_time_dilation))
        elif st["n"] > 40:
            st["case"] += 1
            st["n"] = 0
            if st["case"] >= len(CASES):
                unreal.log_warning("%s done" % TAG)
                unreal.unregister_slate_post_tick_callback(st["h"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
