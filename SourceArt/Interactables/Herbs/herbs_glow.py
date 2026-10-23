# Editor Python: the healing herbs glow softly in their own colours (emissive = base colour texture x a green tint), get a
# simple box collision (so walking over them overlaps - eggs taught us a complex-only mesh may not), and list the
# glTF master material's parameter names (step 'names').
import unreal
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
step = globals().get("STEP", "names")
mi = EAL.load_asset("/Game/Timeshift/Interactables/Herbs/SM_HealingHerbs/Materials/tripo_material_59310334-a5fa-49fe-8320-6067d4083f8e")
parent = mi.get_editor_property("parent")
if step == "names":
    unreal.log_warning("[HGLOW] tex %s" % [str(n) for n in MEL.get_texture_parameter_names(parent)])
    unreal.log_warning("[HGLOW] vec %s" % [str(n) for n in MEL.get_vector_parameter_names(parent)])
    unreal.log_warning("[HGLOW] scal %s" % [str(n) for n in MEL.get_scalar_parameter_names(parent)])
else:
    tex = EAL.load_asset("/Game/Timeshift/Interactables/Herbs/SM_HealingHerbs/Textures/parsley_bundle_3d_model_basecolor")
    MEL.set_material_instance_texture_parameter_value(mi, "EmissiveTexture", tex)
    g = float(globals().get("GLOW", 1.2))
    MEL.set_material_instance_vector_parameter_value(mi, "EmissiveFactor", unreal.LinearColor(0.45 * g, 1.0 * g, 0.45 * g, 1.0))
    EAL.save_asset(mi.get_path_name(), only_if_is_dirty=False)
    m = EAL.load_asset("/Game/Timeshift/Interactables/Herbs/SM_HealingHerbs/StaticMeshes/SM_HealingHerbs")
    if unreal.EditorStaticMeshLibrary.get_simple_collision_count(m) == 0:
        unreal.EditorStaticMeshLibrary.add_simple_collisions(m, unreal.ScriptCollisionShapeType.BOX)
    EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)
    unreal.log_warning("[HGLOW] glow %.2f set, collision shapes %d" % (g, unreal.EditorStaticMeshLibrary.get_simple_collision_count(m)))
