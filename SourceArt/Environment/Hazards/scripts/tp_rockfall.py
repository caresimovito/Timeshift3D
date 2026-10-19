# Editor Python, during PIE: put the hero just south of Rockfall_Trap's trigger (so it doesn't fire on arrival), facing
# north at the cliff with the camera tilted up. Walking ~4 m forward sets it off.
import unreal

w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
x, y = 50100, -750
h = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x, y, 400), unreal.Vector(x, y, -500),
                                           unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [pawn], unreal.DrawDebugTrace.NONE, True).to_tuple()
pawn.set_actor_location(unreal.Vector(x, y, (h[4].z if h[0] else 15) + 100), False, True)
pawn.set_actor_rotation(unreal.Rotator(0, 0, 90), True)          # Rotator(roll, pitch, yaw): face +Y (the cliff)
unreal.GameplayStatics.get_player_controller(w, 0).set_control_rotation(unreal.Rotator(0, 12, 90))
unreal.log_warning("[TP] hero at (%d,%d) facing the cliff" % (x, y))
