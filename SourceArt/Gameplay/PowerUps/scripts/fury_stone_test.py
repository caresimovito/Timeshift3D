# Editor Python, during PIE: Fury on, stones given, hero placed 6 m from a (frozen) ground dinosaur facing it, quick throw.
# Expect a "DMG 44" line for the dinosaur.
import math
import unreal
TAG = "[FST]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
en = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_EnemyBase_C"
      and str(a.get_editor_property("Species")) in ("Stegosaurus", "Parasaurolophus", "Triceratops")]
e = en[0]
e.set_actor_tick_enabled(False)
l = e.get_actor_location()
pawn.set_actor_location(unreal.Vector(l.x - 600, l.y, l.z + 100), False, True)
pawn.set_actor_rotation(unreal.Rotator(0, 0, 0), True)
unreal.GameplayStatics.get_player_controller(w, 0).set_control_rotation(unreal.Rotator(0, -5, 0))
pawn.call_method("StartFury", (15.0,))
pawn.call_method("DebugGiveStones")
unreal.log_warning("%s target %s fury=%s stones=%s" % (TAG, e.get_actor_label(), pawn.get_editor_property("bFuryActive"), pawn.get_editor_property("StoneAmmo")))
pawn.call_method("QuickThrow")
