# Editor Python: M_ArmourBronze - the ARMOUR look (user 2026-10-23 picked Grok concept 4: "his skin and clothes take on
# a polished bronze-statue metallic sheen"). Replaces the hero's slot-0 material (M_Hero_Era1) while he has armour.
# Keeps his detail by reusing his own textures:
#   lum       = luminance(Hero_BaseColor)
#   BaseColor = Bronze x lerp(0.45, 1.25, lum)      (dark cloth -> deep bronze, light skin -> bright gold)
#   Metallic 0.85, Roughness = 0.15 + (1 - lum) x 0.2, Normal = Hero_NormalMap, Emissive = BaseColor x WarmGlow 0.12
# Opaque lit; compiles through the property changes at the end (no recompile_material call).
import unreal
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
PATH, NAME = "/Game/Timeshift/VFX/Armour", "M_ArmourBronze"
TX = "/Game/Timeshift/Characters/Hero/Textures/"
m = unreal.load_object(None, "%s/%s.%s" % (PATH, NAME, NAME))
if m:
    MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset(NAME, PATH, unreal.Material, unreal.MaterialFactoryNew())
X = lambda cls, x, y: MEL.create_material_expression(m, cls, x, y)
C = MEL.connect_material_expressions
bc = X(unreal.MaterialExpressionTextureSample, -1000, 0)
bc.set_editor_property("texture", unreal.load_object(None, TX + "Hero_BaseColor.Hero_BaseColor"))
nm = X(unreal.MaterialExpressionTextureSample, -1000, 400)
nm.set_editor_property("texture", unreal.load_object(None, TX + "Hero_NormalMap.Hero_NormalMap"))
nm.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
w = X(unreal.MaterialExpressionConstant3Vector, -1000, 250); w.set_editor_property("constant", unreal.LinearColor(0.3, 0.59, 0.11, 1))
lum = X(unreal.MaterialExpressionDotProduct, -750, 100); C(bc, "RGB", lum, "A"); C(w, "", lum, "B")
lo = X(unreal.MaterialExpressionConstant, -750, 220); lo.set_editor_property("r", 0.45)
hi = X(unreal.MaterialExpressionConstant, -750, 300); hi.set_editor_property("r", 1.25)
lp = X(unreal.MaterialExpressionLinearInterpolate, -550, 180); C(lo, "", lp, "A"); C(hi, "", lp, "B"); C(lum, "", lp, "Alpha")
bronze = X(unreal.MaterialExpressionVectorParameter, -550, 0); bronze.set_editor_property("parameter_name", "Bronze")
bronze.set_editor_property("default_value", unreal.LinearColor(0.95, 0.58, 0.22, 1))
base = X(unreal.MaterialExpressionMultiply, -350, 80); C(bronze, "", base, "A"); C(lp, "", base, "B")
MEL.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
one = X(unreal.MaterialExpressionConstant, -350, 200); one.set_editor_property("r", 0.85)
MEL.connect_material_property(one, "", unreal.MaterialProperty.MP_METALLIC)
inv = X(unreal.MaterialExpressionOneMinus, -550, 320); C(lum, "", inv, "")
k = X(unreal.MaterialExpressionConstant, -550, 400); k.set_editor_property("r", 0.2)
rm = X(unreal.MaterialExpressionMultiply, -400, 330); C(inv, "", rm, "A"); C(k, "", rm, "B")
r0 = X(unreal.MaterialExpressionConstant, -400, 420); r0.set_editor_property("r", 0.15)
ra = X(unreal.MaterialExpressionAdd, -250, 350); C(rm, "", ra, "A"); C(r0, "", ra, "B")
MEL.connect_material_property(ra, "", unreal.MaterialProperty.MP_ROUGHNESS)
MEL.connect_material_property(nm, "RGB", unreal.MaterialProperty.MP_NORMAL)
# v2 (PIE: pure metal read as dark gunmetal in the shady jungle - nothing bright to reflect): warm self-glow so it
# still reads as polished bronze in shade
gk = X(unreal.MaterialExpressionScalarParameter, -350, 520); gk.set_editor_property("parameter_name", "WarmGlow"); gk.set_editor_property("default_value", 0.12)
em = X(unreal.MaterialExpressionMultiply, -150, 480); C(base, "", em, "A"); C(gk, "", em, "B")
MEL.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
m.set_editor_property("used_with_skeletal_mesh", True)
m.set_editor_property("two_sided", True)       # property changes -> compile
m.set_editor_property("two_sided", False)
EAL.save_asset("%s/%s" % (PATH, NAME), only_if_is_dirty=False)
unreal.log_warning("[ABRONZE] %s built, %d textures" % (NAME, len(MEL.get_used_textures(m))))
