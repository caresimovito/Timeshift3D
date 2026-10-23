# Editor Python, during PIE: equip the spear, give stones, throw one, and take a screenshot mid-throw (HighResShot) at
# T1 and T2 seconds after the throw starts, to see where the spear is. Screenshots land in Saved/Screenshots/WindowsEditor.
import unreal
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
T = globals().get("SHOTS_AT") or [0.35, 0.7]
# pick up the level's spear for real (bHasSpear is not editable from Python)
sp = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_actor_label() == "Pickup_Spear"]
if sp:
    l = sp[0].get_actor_location()
    pawn.set_actor_location(unreal.Vector(l.x, l.y, l.z + 95), False, False)   # stand on it: Interact needs the overlap
pawn.call_method("DebugGiveStones")
pc = unreal.GameplayStatics.get_player_controller(w, 0)
SIDE = globals().get("CAM_SIDE", 75.0)
st = {"h": None, "t0": None, "i": 0}


def tick(dt):
    try:
        if st["t0"] is None:
            if "w0" not in st:
                st["w0"] = gt()
            if sp and not st.get("picked") and gt() - st["w0"] > 0.6:
                sp[0].call_method("Interact")
                st["picked"] = True
                unreal.log_warning("[THR] picked up the spear")
            if gt() - st["w0"] < 2.0:                     # let the pickup / weapon swap settle
                return
            pawn.call_method("QuickThrow")
            r = pawn.get_actor_rotation()
            pc.set_control_rotation(unreal.Rotator(pitch=-8, yaw=r.yaw + SIDE, roll=0))
            st["t0"] = gt()
            unreal.log_warning("[THR] throw started, ranged=%s" % pawn.get_editor_property("bIsRangedAttacking"))
            return
        r = pawn.get_actor_rotation()
        pc.set_control_rotation(unreal.Rotator(pitch=-8, yaw=r.yaw + SIDE, roll=0))
        if st["i"] < len(T) and gt() - st["t0"] >= T[st["i"]]:
            unreal.SystemLibrary.execute_console_command(w, "HighResShot 1280x720")
            unreal.log_warning("[THR] shot %d at %.2fs" % (st["i"], gt() - st["t0"]))
            st["i"] += 1
        if st["i"] >= len(T):
            unreal.log_warning("[THR] done")
            unreal.unregister_slate_post_tick_callback(st["h"])
    except Exception as ex:
        unreal.log_warning("[THR] error %s" % ex)
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
