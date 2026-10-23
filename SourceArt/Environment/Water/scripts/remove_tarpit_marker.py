# Editor Python: delete the temporary MARKER_TarPit beacon (glowing cylinder over the tar pit, added while building the swamp
# hazards; user 2026-10-21: "remove yellow beam") and save the level.
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
gone = [a for a in eas.get_all_level_actors() if a.get_actor_label() == "MARKER_TarPit"]
for a in gone:
    eas.destroy_actor(a)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
left = [a for a in eas.get_all_level_actors() if a.get_actor_label() == "MARKER_TarPit"]
unreal.log_warning("[RTM] removed %d, remaining %d" % (len(gone), len(left)))
