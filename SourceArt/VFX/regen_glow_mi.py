# Editor Python: MI_RegenGlow - REGEN look = the Fury glow in green (user 2026-10-23: "just use the same as fury but
# with a green glow, it's taking too long"). Instance of M_FuryGlow (fresnel rim + faint inner warmth, gentle pulse).
import unreal
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
PATH, MI = "/Game/Timeshift/VFX/Regen", "MI_RegenGlow"
mi = unreal.load_object(None, "%s/%s.%s" % (PATH, MI, MI))
if not mi:
    mi = AT.create_asset(MI, PATH, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, unreal.load_object(None, "/Game/Timeshift/VFX/Fury/M_FuryGlow.M_FuryGlow"))
MEL.set_material_instance_vector_parameter_value(mi, "FuryColor", unreal.LinearColor(0.15, 1.0, 0.3, 1.0))
EAL.save_asset("%s/%s" % (PATH, MI), only_if_is_dirty=False)
unreal.log_warning("[RGLOW] %s parent %s" % (MI, mi.get_editor_property("parent").get_name()))
