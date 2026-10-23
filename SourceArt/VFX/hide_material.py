# Editor Python: INVISIBILITY look for the Hide power-up (user 2026-10-23, Gemini concept: body turned to shimmering glass
# bending the jungle behind, faint cyan glowing outline).
#  M_Invisible  - translucent, lit, refraction 1.12, opacity 0.08, near-black base, emissive = fresnel^3 x cyan x 1.4
#  MI_HideGlow  - child of M_FuryMolten2 (additive noise lines + rim, pulsing) in cyan, intensity 0.7
# Built in a fresh asset each time it does not exist (re-building one asset piles up stray nodes); compiles through the
# blend-mode property change (no recompile_material call).
import unreal
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
P = "/Game/Timeshift/VFX/Hide"
m = unreal.load_object(None, P + "/M_Invisible.M_Invisible")
if not m:
    m = AT.create_asset("M_Invisible", P, unreal.Material, unreal.MaterialFactoryNew())
    X = lambda cls, x, y: MEL.create_material_expression(m, cls, x, y)
    C = MEL.connect_material_expressions
    base = X(unreal.MaterialExpressionConstant3Vector, -500, -200); base.set_editor_property("constant", unreal.LinearColor(0.02, 0.05, 0.05, 1))
    op = X(unreal.MaterialExpressionConstant, -500, 0); op.set_editor_property("r", 0.08)
    ior = X(unreal.MaterialExpressionConstant, -500, 100); ior.set_editor_property("r", 1.12)
    rough = X(unreal.MaterialExpressionConstant, -500, -100); rough.set_editor_property("r", 0.1)
    fr = X(unreal.MaterialExpressionFresnel, -700, 250); fr.set_editor_property("exponent", 3.0)
    cyan = X(unreal.MaterialExpressionConstant3Vector, -700, 380); cyan.set_editor_property("constant", unreal.LinearColor(0.25, 1.4, 1.3, 1))
    em = X(unreal.MaterialExpressionMultiply, -450, 300); C(fr, "", em, "A"); C(cyan, "", em, "B")
    MEL.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
    MEL.connect_material_property(ior, "", unreal.MaterialProperty.MP_REFRACTION)
    MEL.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    m.set_editor_property("used_with_skeletal_mesh", True)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    EAL.save_asset(P + "/M_Invisible", only_if_is_dirty=False)
mi = unreal.load_object(None, P + "/MI_HideGlow.MI_HideGlow")
if not mi:
    mi = AT.create_asset("MI_HideGlow", P, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, unreal.load_object(None, "/Game/Timeshift/VFX/Fury/M_FuryMolten2.M_FuryMolten2"))
MEL.set_material_instance_vector_parameter_value(mi, "FuryColor", unreal.LinearColor(0.15, 1.0, 0.95, 1))
MEL.set_material_instance_scalar_parameter_value(mi, "Intensity", 0.7)
EAL.save_asset(P + "/MI_HideGlow", only_if_is_dirty=False)
unreal.log_warning("[HIDEMAT] M_Invisible blend %s, MI_HideGlow ok" % m.get_editor_property("blend_mode"))
