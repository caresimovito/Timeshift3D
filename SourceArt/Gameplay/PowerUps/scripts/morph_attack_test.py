# Editor Python, during PIE: morph, stand 2 m from a frozen ground dinosaur facing it, attack (PerformAttack = what LMB
# does); expect the dinosaur's DMG line = MorphDmg and MorphAnimState 2 (attack clip).
import unreal
TAG = "[MAT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
en = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_EnemyBase_C"
      and str(a.get_editor_property("Species")) in ("Stegosaurus", "Parasaurolophus", "Triceratops")]
e = en[0]
e.set_actor_tick_enabled(False)
l = e.get_actor_location()
br = e.get_editor_property("BodyRadius")
pawn.call_method("AddMorphCharge")
pawn.call_method("StartMorph")
pawn.set_actor_location(unreal.Vector(l.x - br - 60, l.y, l.z + pawn.get_editor_property("MorphHalf") + 10), False, True)
pawn.set_actor_rotation(unreal.Rotator(0, 0, 0), True)
ma = {"h": None, "n": 0}


def tick(dt):
    try:
        ma["n"] += 1
        if ma["n"] == 5:
            pawn.call_method("PerformAttack")
        if ma["n"] in (8, 20):
            unreal.log_warning("%s %s vs %s: animstate=%s isattacking=%s atkdmg=%s" % (TAG, pawn.get_editor_property("MorphName"), e.get_actor_label(),
                               pawn.get_editor_property("MorphAnimState"), pawn.get_editor_property("bIsAttacking"), pawn.get_editor_property("AttackDamage")))
        if ma["n"] > 20:
            unreal.unregister_slate_post_tick_callback(ma["h"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(ma["h"])


ma["h"] = unreal.register_slate_post_tick_callback(tick)
