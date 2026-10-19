# Editor Python: the old moss basin under the tar is up to 1.5 m deep, which buried the hero before he even sank.
# Hidden blocking floor 40 cm under the tar surface (SM_TarPit shape, complex-as-simple collision), so he starts thigh-deep.
import unreal

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
m = EAL.load_asset("/Game/Timeshift/Hazards/Meshes/SM_TarPit")
m.get_editor_property("body_setup").set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)
for a in EAS.get_all_level_actors():
    if a.get_actor_label() == "Swamp_TarFloor":
        EAS.destroy_actor(a)
tar = [a for a in EAS.get_all_level_actors() if a.get_actor_label() == "Swamp_TarPit"][0]
l = tar.get_actor_location()
f = EAS.spawn_actor_from_object(m, unreal.Vector(l.x, l.y, l.z - 40), unreal.Rotator(0, 0, 0))
f.set_actor_label("Swamp_TarFloor")
f.set_folder_path("Swamp/Hazards")
c = f.static_mesh_component
c.set_collision_profile_name("BlockAll")
c.set_editor_property("hidden_in_game", True)
c.set_editor_property("cast_shadow", False)
c.set_visibility(False, False)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log_warning("[TARFLOOR] at %s profile=%s" % (f.get_actor_location(), c.get_collision_profile_name()))
