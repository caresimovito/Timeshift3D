# Editor Python: tar zone component overrides via the component setters (set_editor_property("static_mesh") is protected), save, re-check.
import unreal

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    if a.get_actor_label() != "Swamp_TarPit":
        continue
    a.modify()
    for c in a.get_components_by_class(unreal.ActorComponent):
        n = c.get_name()
        c.modify()
        if n.startswith("MudDecal"):
            c.set_visibility(False, False)
        elif n.startswith("TarSurface"):
            c.set_static_mesh(EAL.load_asset("/Game/Timeshift/Hazards/Meshes/SM_TarPit"))
            c.set_material(0, EAL.load_asset("/Game/Timeshift/Hazards/Materials/M_Tar"))
            c.set_visibility(True, False)
            c.set_hidden_in_game(False)
            unreal.log_warning("[SINKCHK] pre-save tar vis=%s" % c.is_visible())
unreal.EditorLoadingAndSavingUtils.save_current_level()
exec(open(r'C:/agentpy/check_sinkzones.py').read())
