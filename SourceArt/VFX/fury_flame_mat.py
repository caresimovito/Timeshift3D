# Editor Python: import the procedural flame flipbook (SourceArt/VFX/T_FuryFlame_8x8.png, made by
# make_flame_flipbook.py) and build M_FuryFlame - the Niagara sprite material for the new Fury fire
# (user 2026-10-23: "build fury like the gemini concept" - tall licking flames, not glowing blobs).
#   tex R = heat, A = flame mask; ParticleSubUV (8x8, blended frames)
#   emissive = lerp(deep orange, yellow-white, heat^2) x heat^0.6 x ParticleColor.rgb x Intensity
#   opacity  = mask x ParticleColor.a       (translucent, unlit; compiles via the blend-mode change)
import unreal
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
PATH = "/Game/Timeshift/VFX/Fury"
SRC = r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/VFX/T_FuryFlame_8x8.png"

t = unreal.AssetImportTask()
t.filename = SRC; t.destination_path = PATH; t.destination_name = "T_FuryFlame_8x8"
t.replace_existing = True; t.automated = True; t.save = False
if not unreal.load_object(None, PATH + '/T_FuryFlame_8x8.T_FuryFlame_8x8'): AT.import_asset_tasks([t])
tex = unreal.load_object(None, PATH + "/T_FuryFlame_8x8.T_FuryFlame_8x8")
tex.set_editor_property("srgb", False)
tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_EFFECTS)
tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
EAL.save_asset(PATH + "/T_FuryFlame_8x8", only_if_is_dirty=False)

NAME = "M_FuryFlame"
m = unreal.load_object(None, "%s/%s.%s" % (PATH, NAME, NAME))
if m:
    MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset(NAME, PATH, unreal.Material, unreal.MaterialFactoryNew())
X = lambda cls, x, y: MEL.create_material_expression(m, cls, x, y)
C = MEL.connect_material_expressions
sub = X(unreal.MaterialExpressionParticleSubUV, -1200, 0)
sub.set_editor_property("texture", tex)
sub.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
sub.set_editor_property("blend", True)
pc = X(unreal.MaterialExpressionParticleColor, -1200, 400)
# heat curve
p2 = X(unreal.MaterialExpressionMultiply, -900, -100); C(sub, "R", p2, "A"); C(sub, "R", p2, "B")
lo = X(unreal.MaterialExpressionConstant3Vector, -900, 0); lo.set_editor_property("constant", unreal.LinearColor(1.0, 0.22, 0.03, 1))
hi = X(unreal.MaterialExpressionConstant3Vector, -900, 100); hi.set_editor_property("constant", unreal.LinearColor(1.6, 1.1, 0.45, 1))
lp = X(unreal.MaterialExpressionLinearInterpolate, -650, 0); C(lo, "", lp, "A"); C(hi, "", lp, "B"); C(p2, "", lp, "Alpha")
pw = X(unreal.MaterialExpressionPower, -650, 200); C(sub, "R", pw, "Base")
e6 = X(unreal.MaterialExpressionConstant, -800, 260); e6.set_editor_property("r", 0.6); C(e6, "", pw, "Exp")
m1 = X(unreal.MaterialExpressionMultiply, -450, 80); C(lp, "", m1, "A"); C(pw, "", m1, "B")
m2 = X(unreal.MaterialExpressionMultiply, -300, 160); C(m1, "", m2, "A"); C(pc, "", m2, "B")
inten = X(unreal.MaterialExpressionScalarParameter, -450, 300)
inten.set_editor_property("parameter_name", "Intensity"); inten.set_editor_property("default_value", 4.0)
m3 = X(unreal.MaterialExpressionMultiply, -150, 160); C(m2, "", m3, "A"); C(inten, "", m3, "B")
# additive (v2, user: separate hard-edged "candles"): overlapping tongues merge into one fire mass, so emissive is
# premultiplied by the soft mask (mask^1.5) x particle alpha instead of using opacity
op = X(unreal.MaterialExpressionMultiply, -300, 420); C(sub, "A", op, "A"); C(pc, "A", op, "B")
soft = X(unreal.MaterialExpressionPower, -150, 420); C(op, "", soft, "Base")
e15 = X(unreal.MaterialExpressionConstant, -300, 520); e15.set_editor_property("r", 1.5); C(e15, "", soft, "Exp")
m4 = X(unreal.MaterialExpressionMultiply, 0, 200); C(m3, "", m4, "A"); C(soft, "", m4, "B")
MEL.connect_material_property(m4, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property("used_with_niagara_sprites", True)
m.set_editor_property("two_sided", True)
m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)     # property change -> compiles
EAL.save_asset("%s/%s" % (PATH, NAME), only_if_is_dirty=False)
unreal.log_warning("[FFLAME] tex %s %s, mat %s blend %s" % (tex.blueprint_get_size_x(), tex.blueprint_get_size_y(), NAME, m.get_editor_property("blend_mode")))
