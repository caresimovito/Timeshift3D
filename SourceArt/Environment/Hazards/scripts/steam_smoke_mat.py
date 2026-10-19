# Editor Python: real-looking steam smoke for the geysers.
#  - copies the engine's 8x8 smoke flipbook (T_SmokeSubUV_8X8) into the project
#  - M_SteamSmoke: lit translucent sprite (volumetric non-directional lighting, so it shades like smoke rather than glowing),
#    flipbook via ParticleSubUV (blended frames), tinted by particle colour, soft depth fade against water / ground
# Recompile afterwards with the MCP MaterialTools recompile.
import unreal

TAG = "[SMAT]"
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
T = "/Game/Timeshift/Hazards/Textures/T_SmokeSubUV_8x8"
if not EAL.does_asset_exist(T):
    EAL.duplicate_asset("/Engine/Tutorial/SubEditors/TutorialAssets/T_SmokeSubUV_8X8", T)
tex = EAL.load_asset(T)
EAL.save_asset(T, only_if_is_dirty=False)
# density from the texture's alpha when it has one, else from its red channel
src_alpha = not tex.get_editor_property("compression_no_alpha") and tex.get_editor_property("compression_settings") != unreal.TextureCompressionSettings.TC_GRAYSCALE
unreal.log_warning("%s tex compression=%s no_alpha=%s srgb=%s size=%dx%d" % (TAG, tex.get_editor_property("compression_settings"),
                   tex.get_editor_property("compression_no_alpha"), tex.get_editor_property("srgb"), tex.blueprint_get_size_x(), tex.blueprint_get_size_y()))

D = "/Game/Timeshift/Hazards/Materials"
m = EAL.load_asset(D + "/M_SteamSmoke") or unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    "M_SteamSmoke", D, unreal.Material, unreal.MaterialFactoryNew())
MEL.delete_all_material_expressions(m)


def node(cls, x, y, **props):
    e = MEL.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def link(a, b, inp="", out=""):
    if not MEL.connect_material_expressions(a, out, b, inp):
        unreal.log_warning("%s link failed %s.%s -> %s.%s" % (TAG, a.get_name(), out, b.get_name(), inp))


sub = node(unreal.MaterialExpressionParticleSubUV, -900, 0, texture=tex, blend=True)
pc = node(unreal.MaterialExpressionParticleColor, -900, 300)
shade = node(unreal.MaterialExpressionLinearInterpolate, -600, -100, const_a=0.72, const_b=1.0)
link(sub, shade, "Alpha", "R")
bc = node(unreal.MaterialExpressionMultiply, -400, -100)
link(pc, bc, "A", "RGB")
link(shade, bc, "B")
dens = node(unreal.MaterialExpressionMultiply, -600, 200)
link(sub, dens, "A", "A" if src_alpha else "R")
link(pc, dens, "B", "A")
df = node(unreal.MaterialExpressionDepthFade, -600, 400, fade_distance_default=90.0)
op = node(unreal.MaterialExpressionMultiply, -400, 250)
link(dens, op, "A")
link(df, op, "B")
em = node(unreal.MaterialExpressionMultiply, -400, 0, const_b=0.12)   # a little self-light so it never goes muddy in shade
link(bc, em, "A")
MEL.connect_material_property(bc, "", unreal.MaterialProperty.MP_BASE_COLOR)
MEL.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
MEL.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
m.set_editor_property("translucency_lighting_mode", unreal.TranslucencyLightingMode.TLM_VOLUMETRIC_NON_DIRECTIONAL)
m.set_editor_property("used_with_niagara_sprites", True)
EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)
unreal.log_warning("%s M_SteamSmoke built (tex %s, density from %s)" % (TAG, tex is not None, "alpha" if src_alpha else "red"))
