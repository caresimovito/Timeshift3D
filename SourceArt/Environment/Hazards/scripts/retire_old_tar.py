# Editor Python: the new Swamp_TarPit replaces the old Hazard_TarPit (BP_HazardZone "Deep Water", 0.4 speed, 2 dmg/s) whose
# speed call overrode the tar's. Not deleted: collision off, hidden, relabelled, moved to Swamp/Hazards/Retired.
import unreal

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    if a.get_actor_label() == "Hazard_TarPit":
        a.modify()
        a.set_actor_enable_collision(False)
        a.set_actor_hidden_in_game(True)
        a.set_actor_label("Hazard_TarPit_RETIRED")
        a.set_folder_path("Swamp/Hazards/Retired")
        unreal.log_warning("[RETIRE] %s collision=%s" % (a.get_actor_label(), a.get_actor_enable_collision()))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
