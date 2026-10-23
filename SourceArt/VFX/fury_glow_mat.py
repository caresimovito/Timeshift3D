# Editor Python: M_FuryGlow - the "fiery glow" FURY option (user 2026-10-23: "cant we just use like a fiery glow?" -
# compare in game against the flames version; dev key '-'). Additive overlay, unlit, NO noise (v1 M_FuryMolten's
# noise cracks read as grainy orange):
#   emissive = (fresnel^RimExp x Rim + Inner) x pulse x FuryColor x Intensity,  pulse = 0.85 + 0.15 sin(5 t)
# -> a hot orange rim around his silhouette plus a faint ember warmth. MI_FuryGlowSpear: Inner high = red-hot spear.
# Compiles through the blend-mode property change (no recompile_material call).
import unreal
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
PATH, NAME = "/Game/Timeshift/VFX/Fury", "M_FuryGlow"
m = unreal.load_object(None, "%s/%s.%s" % (PATH, NAME, NAME))
if m:
    MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset(NAME, PATH, unreal.Material, unreal.MaterialFactoryNew())
X = lambda cls, x, y: MEL.create_material_expression(m, cls, x, y)
C = MEL.connect_material_expressions
def P(name, v, x, y):
    p = X(unreal.MaterialExpressionScalarParameter, x, y)
    p.set_editor_property("parameter_name", name); p.set_editor_property("default_value", v)
    return p
rimexp = P("RimExp", 2.5, -900, 0)
fr = X(unreal.MaterialExpressionFresnel, -700, 0); C(rimexp, "", fr, "ExponentIn")
rim = P("Rim", 3.0, -700, 120)
m1 = X(unreal.MaterialExpressionMultiply, -500, 40); C(fr, "", m1, "A"); C(rim, "", m1, "B")
inner = P("Inner", 0.12, -500, 160)
a1 = X(unreal.MaterialExpressionAdd, -350, 80); C(m1, "", a1, "A"); C(inner, "", a1, "B")
tm = X(unreal.MaterialExpressionTime, -900, 300)
k5 = X(unreal.MaterialExpressionConstant, -900, 400); k5.set_editor_property("r", 5.0)
t5 = X(unreal.MaterialExpressionMultiply, -750, 320); C(tm, "", t5, "A"); C(k5, "", t5, "B")
sn = X(unreal.MaterialExpressionSine, -600, 320); C(t5, "", sn, "")
k15 = X(unreal.MaterialExpressionConstant, -600, 420); k15.set_editor_property("r", 0.15)
amp = X(unreal.MaterialExpressionMultiply, -450, 340); C(sn, "", amp, "A"); C(k15, "", amp, "B")
k85 = X(unreal.MaterialExpressionConstant, -450, 440); k85.set_editor_property("r", 0.85)
pul = X(unreal.MaterialExpressionAdd, -300, 360); C(amp, "", pul, "A"); C(k85, "", pul, "B")
m2 = X(unreal.MaterialExpressionMultiply, -150, 160); C(a1, "", m2, "A"); C(pul, "", m2, "B")
col = X(unreal.MaterialExpressionVectorParameter, -300, -120); col.set_editor_property("parameter_name", "FuryColor")
col.set_editor_property("default_value", unreal.LinearColor(1.0, 0.25, 0.04, 1.0))
m3 = X(unreal.MaterialExpressionMultiply, 0, 60); C(m2, "", m3, "A"); C(col, "", m3, "B")
inten = P("Intensity", 4.0, 0, 200)
m4 = X(unreal.MaterialExpressionMultiply, 150, 100); C(m3, "", m4, "A"); C(inten, "", m4, "B")
MEL.connect_material_property(m4, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property("used_with_skeletal_mesh", True)
m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)      # property change -> compiles
EAL.save_asset("%s/%s" % (PATH, NAME), only_if_is_dirty=False)

MI = "MI_FuryGlowSpear"
mi = unreal.load_object(None, "%s/%s.%s" % (PATH, MI, MI))
if not mi:
    mi = AT.create_asset(MI, PATH, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, m)
MEL.set_material_instance_scalar_parameter_value(mi, "Inner", 0.9)
MEL.set_material_instance_scalar_parameter_value(mi, "Rim", 1.5)
MEL.set_material_instance_vector_parameter_value(mi, "FuryColor", unreal.LinearColor(1.0, 0.18, 0.02, 1.0))
EAL.save_asset("%s/%s" % (PATH, MI), only_if_is_dirty=False)
unreal.log_warning("[FGLOW] %s blend %s, %s parent %s" % (NAME, m.get_editor_property("blend_mode"), MI, mi.get_editor_property("parent").get_name()))
