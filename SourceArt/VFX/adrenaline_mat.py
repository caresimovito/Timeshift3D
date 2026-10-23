# Editor Python: ADRENALINE look (user 2026-10-23 picked Grok concept 4: blue-white lightning crackling between his
# feet and the ground, a thin electric trail, a faint blue rim).
#   T_Lightning_4x4 (SourceArt/VFX, make_lightning_flipbook.py): R = white core, A = core + glow
#   M_Lightning: additive Niagara sprite, ParticleSubUV (no blend - each bolt is a random frame)
#       emissive = (A x ParticleColor.rgb + R x 1.5) x ParticleColor.a x Intensity
#   MI_AdrenalineGlow: M_FuryGlow instance, blue-white rim, almost no inner glow (overlay on the hero)
# Compiles through the blend-mode property change (no recompile_material call).
import unreal
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
PATH = "/Game/Timeshift/VFX/Adrenaline"
SRC = r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/VFX/T_Lightning_4x4.png"
t = unreal.AssetImportTask()
t.filename = SRC; t.destination_path = PATH; t.destination_name = "T_Lightning_4x4"
t.replace_existing = True; t.automated = True; t.save = False
AT.import_asset_tasks([t])
tex = unreal.load_object(None, PATH + "/T_Lightning_4x4.T_Lightning_4x4")
tex.set_editor_property("srgb", False)
tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_EFFECTS)
EAL.save_asset(PATH + "/T_Lightning_4x4", only_if_is_dirty=False)

NAME = "M_Lightning"
m = unreal.load_object(None, "%s/%s.%s" % (PATH, NAME, NAME))
if m:
    MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset(NAME, PATH, unreal.Material, unreal.MaterialFactoryNew())
X = lambda cls, x, y: MEL.create_material_expression(m, cls, x, y)
C = MEL.connect_material_expressions
sub = X(unreal.MaterialExpressionParticleSubUV, -900, 0)
sub.set_editor_property("texture", tex)
sub.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
sub.set_editor_property("blend", False)
pc = X(unreal.MaterialExpressionParticleColor, -900, 300)
a1 = X(unreal.MaterialExpressionMultiply, -600, 100); C(sub, "A", a1, "A"); C(pc, "", a1, "B")
k = X(unreal.MaterialExpressionConstant, -750, 220); k.set_editor_property("r", 1.5)
r1 = X(unreal.MaterialExpressionMultiply, -600, 220); C(sub, "R", r1, "A"); C(k, "", r1, "B")
ad = X(unreal.MaterialExpressionAdd, -450, 160); C(a1, "", ad, "A"); C(r1, "", ad, "B")
m1 = X(unreal.MaterialExpressionMultiply, -300, 200); C(ad, "", m1, "A"); C(pc, "A", m1, "B")
inten = X(unreal.MaterialExpressionScalarParameter, -450, 350)
inten.set_editor_property("parameter_name", "Intensity"); inten.set_editor_property("default_value", 3.0)
m2 = X(unreal.MaterialExpressionMultiply, -150, 220); C(m1, "", m2, "A"); C(inten, "", m2, "B")
MEL.connect_material_property(m2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property("used_with_niagara_sprites", True)
m.set_editor_property("two_sided", True)
m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)     # property change -> compiles
EAL.save_asset("%s/%s" % (PATH, NAME), only_if_is_dirty=False)

MI = "MI_AdrenalineGlow"
mi = unreal.load_object(None, "%s/%s.%s" % (PATH, MI, MI))
if not mi:
    mi = AT.create_asset(MI, PATH, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, unreal.load_object(None, "/Game/Timeshift/VFX/Fury/M_FuryGlow.M_FuryGlow"))
MEL.set_material_instance_scalar_parameter_value(mi, "Inner", 0.02)
MEL.set_material_instance_scalar_parameter_value(mi, "Rim", 2.2)
MEL.set_material_instance_scalar_parameter_value(mi, "RimExp", 3.5)
MEL.set_material_instance_vector_parameter_value(mi, "FuryColor", unreal.LinearColor(0.35, 0.6, 1.0, 1.0))
EAL.save_asset("%s/%s" % (PATH, MI), only_if_is_dirty=False)

# the effect: a copy of NS_FurySpearFire (Flame + Embers sprite emitters) retuned into lightning in the next step
NS = "NS_AdrenalineSpark"
if not unreal.load_object(None, "%s/%s.%s" % (PATH, NS, NS)):
    EAL.duplicate_asset("/Game/Timeshift/VFX/Fury/NS_FurySpearFire", "%s/%s" % (PATH, NS))
    EAL.save_asset("%s/%s" % (PATH, NS), only_if_is_dirty=False)
unreal.log_warning("[ADREN] tex %s, mat blend %s, MI parent %s, NS %s" % (tex.get_name(), m.get_editor_property("blend_mode"), mi.get_editor_property("parent").get_name(), bool(unreal.load_object(None, "%s/%s.%s" % (PATH, NS, NS)))))
