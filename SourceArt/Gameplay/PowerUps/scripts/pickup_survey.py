# Editor Python: pickup visuals (components, meshes, materials, lights) per pickup class + how many of each are placed.
import unreal
TAG = "[PKS]"
EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
counts = {}
first = {}
for a in EAS.get_all_level_actors():
    n = a.get_class().get_name()
    if n.startswith("BP_Pickup_"):
        counts[n] = counts.get(n, 0) + 1
        first.setdefault(n, a)
unreal.log_warning("%s placed: %s" % (TAG, sorted(counts.items())))
for n in ("BP_Pickup_Adrenaline_C", "BP_Pickup_Health_C", "BP_Pickup_Hide_C"):
    a = first.get(n)
    if not a:
        continue
    parts = []
    for c in a.get_components_by_class(unreal.SceneComponent):
        d = c.get_class().get_name() + ":" + c.get_name()
        if isinstance(c, unreal.StaticMeshComponent) and c.static_mesh:
            d += "[%s | %s | scale %s]" % (c.static_mesh.get_name(), [m.get_name() for m in c.get_materials() if m], c.get_editor_property("relative_scale3d"))
        if isinstance(c, unreal.LightComponent):
            d += "[col %s int %.0f]" % (c.get_light_color(), c.intensity)
        parts.append(d)
    unreal.log_warning("%s %s at %s: %s" % (TAG, n, a.get_actor_location(), " ; ".join(parts)))
for p in EAL.list_assets("/Game/Timeshift/UI", False):
    unreal.log_warning("%s ui %s" % (TAG, p))
