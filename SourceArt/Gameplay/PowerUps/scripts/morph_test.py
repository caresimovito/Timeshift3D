# Editor Python, during PIE: give a morph charge, StartMorph (what M does), then log the morph state; walk forward a bit
# (anim state), take 50 damage (should come off armour = dino HP, not health), force EndMorph and check everything
# is restored; then a 2nd morph killed by damage (armour -> 0 ends it early, overflow hits health).
import unreal
TAG = "[MOT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")
hc = pawn.get_component_by_class(HCC)
cap = pawn.get_editor_property("CapsuleComponent")
mesh = pawn.get_editor_property("Mesh")
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
mt = {"h": None, "t0": gt(), "phase": "start"}


def snap(what):
    mb = pawn.get_editor_property("MorphBody")
    unreal.log_warning("%s %s morphed=%s name=%s cap=(%.0f,%.0f) meshscale=%.3f body=%s vis=%s armour=%.0f/%.0f hp=%.0f speed=%.0f atkdmg=%.0f range=%.0f anim=%s z=%.0f" % (
        TAG, what, pawn.get_editor_property("bMorphed"), pawn.get_editor_property("MorphName"), cap.get_unscaled_capsule_radius(),
        cap.get_unscaled_capsule_half_height(), mesh.get_editor_property("relative_scale3d").x,
        mb.get_editor_property("skeletal_mesh_asset").get_name() if mb and mb.get_editor_property("skeletal_mesh_asset") else None,
        mb.is_visible() if mb else None, hc.get_editor_property("Armour"), hc.get_editor_property("MaxArmour"), hc.get_editor_property("CurrentHealth"),
        pawn.get_editor_property("CharacterMovement").get_editor_property("max_walk_speed"), pawn.get_editor_property("AttackDamage"),
        pawn.get_editor_property("AttackRange"), pawn.get_editor_property("MorphAnimState"), pawn.get_actor_location().z))


def tick(dt):
    try:
        now = gt() - mt["t0"]
        ph = mt["phase"]
        for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
            if a != pawn and a.is_actor_tick_enabled() and a.get_component_by_class(HCC) and (a.get_actor_location() - pawn.get_actor_location()).length() < 3000:
                a.set_actor_tick_enabled(False)
        if ph == "start":
            snap("before")
            pawn.call_method("AddMorphCharge")
            pawn.call_method("StartMorph")
            mt.update(phase="m1", t0=gt())
        elif ph == "m1" and now > 0.6:
            snap("morphed")
            mt.update(phase="walk", t0=gt())
        elif ph == "walk":
            pawn.add_movement_input(pawn.get_actor_forward_vector(), 1.0, True)
            if now > 1.5:
                snap("walking")
                hc.call_method("ApplyDamage", (50.0,))
                mt.update(phase="hit", t0=gt())
        elif ph == "hit" and now > 0.5:
            snap("after 50 dmg")
            pawn.call_method("EndMorph")
            mt.update(phase="end", t0=gt())
        elif ph == "end" and now > 0.5:
            snap("ended")
            pawn.call_method("AddMorphCharge")
            pawn.call_method("StartMorph")
            mt.update(phase="m2", t0=gt())
        elif ph == "m2" and now > 0.5:
            snap("morph 2")
            hc.call_method("ApplyDamage", (pawn.get_editor_property("MorphHP") + 10.0,))
            mt.update(phase="kill", t0=gt())
        elif ph == "kill" and now > 0.8:
            snap("after lethal dino dmg")
            unreal.unregister_slate_post_tick_callback(mt["h"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(mt["h"])


mt["h"] = unreal.register_slate_post_tick_callback(tick)
