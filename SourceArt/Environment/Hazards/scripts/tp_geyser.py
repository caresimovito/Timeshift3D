# Editor Python, during PIE: put the hero on dry-ish ground 7 m south of Swamp_Geyser_0, facing it (camera too).
import math
import unreal

w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
g = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.load_class(None, "/Game/Timeshift/Hazards/BP_GeyserVent.BP_GeyserVent_C"))
     if a.get_actor_label() == "Swamp_Geyser_0"][0]
l = g.get_actor_location()
x, y = l.x, l.y - 700
h = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x, y, 3000), unreal.Vector(x, y, -3000),
                                           unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [pawn], unreal.DrawDebugTrace.NONE, True).to_tuple()
pawn.set_actor_location(unreal.Vector(x, y, (h[4].z if h[0] else l.z) + 100), False, True)
yaw = math.degrees(math.atan2(l.y - y, l.x - x))
pawn.set_actor_rotation(unreal.Rotator(0, 0, yaw), True)
pc = unreal.GameplayStatics.get_player_controller(w, 0)
pc.set_control_rotation(unreal.Rotator(0, -8, yaw))
unreal.log_warning("[TP] hero at (%.0f,%.0f) facing geyser, phase=%s" % (x, y, g.get_editor_property("Phase")))
