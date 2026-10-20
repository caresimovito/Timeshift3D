# Editor Python: (1) components of one ground + one flying BP_EnemyBase (which StaticMeshComponents exist, root first?)
# (2) compile status of the hero + bola blueprints.
import unreal
TAG = "[AIMCHK]"
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
done = set()
for a in EAS.get_all_level_actors():
    if a.get_class().get_name() != "BP_EnemyBase_C":
        continue
    sp = str(a.get_editor_property("Species"))
    kind = "fly" if sp in ("Pteranodon", "Tupandactylus") else "ground"
    if kind in done:
        continue
    done.add(kind)
    root = a.root_component
    smcs = [c.get_name() for c in a.get_components_by_class(unreal.StaticMeshComponent)]
    unreal.log_warning("%s %s %s root=%s smcs=%s first=%s" % (TAG, kind, a.get_actor_label(), root.get_name(), smcs,
                       a.get_component_by_class(unreal.StaticMeshComponent).get_name()))
for p in ("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter", "/Game/Timeshift/Weapons/BP_BolaProjectile"):
    bp = unreal.EditorAssetLibrary.load_asset(p)
    unreal.log_warning("%s %s status=%s" % (TAG, p.split("/")[-1], bp.get_editor_property("status")))
