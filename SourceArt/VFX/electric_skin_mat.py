# Editor Python: M_ElectricSkin - Adrenaline overlay (user 2026-10-23 reference: thin bright lightning lines running
# over the whole body, blue-white, electric speedster look - original effect, nothing of the reference character copied).
# Additive overlay, unlit. Thin wandering lines that stick to the body (pre-skinned local position, so they ride the
# limbs) and re-strike ~14 times a second (stepped time):
#   p     = PreSkinnedLocalPosition x 0.045 + floor(time x 14) x (3.1, 1.7, 2.3)
#   lines = saturate(1 - |noise(p)| x 28)^3 + 0.5 x saturate(1 - |noise(p x 2.3 + 11)| x 34)^3   (fine branches)
#   emissive = (lines x (white-blue) + fresnel^3 x 0.25 x cyan) x Intensity
# Compiles through the blend-mode property change (no recompile_material call).
import unreal
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
PATH, NAME = "/Game/Timeshift/VFX/Adrenaline", "M_ElectricSkin"
m = unreal.load_object(None, "%s/%s.%s" % (PATH, NAME, NAME))
if m:
    MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset(NAME, PATH, unreal.Material, unreal.MaterialFactoryNew())
X = lambda cls, x, y: MEL.create_material_expression(m, cls, x, y)
C = MEL.connect_material_expressions
def K(v, x, y):
    c = X(unreal.MaterialExpressionConstant, x, y); c.set_editor_property("r", v); return c
def V(r, g, b, x, y):
    c = X(unreal.MaterialExpressionConstant3Vector, x, y); c.set_editor_property("constant", unreal.LinearColor(r, g, b, 1)); return c
def mul(a, b, x, y, pa="", pb=""):
    n = X(unreal.MaterialExpressionMultiply, x, y); C(a, pa, n, "A"); C(b, pb, n, "B"); return n
def add(a, b, x, y):
    n = X(unreal.MaterialExpressionAdd, x, y); C(a, "", n, "A"); C(b, "", n, "B"); return n
pos = X(unreal.MaterialExpressionPreSkinnedPosition, -1800, 0)
p0 = mul(pos, K(0.045, -1800, 120), -1600, 40)
tm = X(unreal.MaterialExpressionTime, -1800, 240)
t14 = mul(tm, K(14.0, -1800, 340), -1600, 260)
fl = X(unreal.MaterialExpressionFloor, -1450, 260); C(t14, "", fl, "")
jump = mul(fl, V(3.1, 1.7, 2.3, -1450, 360), -1300, 300)
p = add(p0, jump, -1150, 120)
def lines(src, scale, offs, sharp, x, y):
    s = mul(src, K(scale, x - 150, y + 100), x, y)
    s = add(s, K(offs, x - 150, y + 180), x + 120, y)
    nz = X(unreal.MaterialExpressionNoise, x + 240, y)
    nz.set_editor_property("scale", 1.0); nz.set_editor_property("output_min", -1.0); nz.set_editor_property("output_max", 1.0)
    nz.set_editor_property("levels", 1)
    C(s, "", nz, "Position")
    ab = X(unreal.MaterialExpressionAbs, x + 400, y); C(nz, "", ab, "")
    k = mul(ab, K(sharp, x + 400, y + 100), x + 520, y)
    inv = X(unreal.MaterialExpressionOneMinus, x + 640, y); C(k, "", inv, "")
    sat = X(unreal.MaterialExpressionSaturate, x + 760, y); C(inv, "", sat, "")
    sq = mul(sat, sat, x + 880, y)
    return mul(sq, sat, x + 1000, y)
l1 = lines(p, 1.0, 0.0, 28.0, -1000, 0)
l2 = lines(p, 2.3, 11.0, 34.0, -1000, 400)
l2h = mul(l2, K(0.5, 0, 500), 120, 420)
ln = add(l1, l2h, 250, 200)
col = X(unreal.MaterialExpressionVectorParameter, 250, 0); col.set_editor_property("parameter_name", "BoltColor")
col.set_editor_property("default_value", unreal.LinearColor(0.75, 0.9, 1.0, 1.0))
lc = mul(ln, col, 420, 120)
fr = X(unreal.MaterialExpressionFresnel, 250, 500); fr.set_editor_property("exponent", 3.0)
cy = V(0.1, 0.5, 1.0, 250, 600)
rim = mul(mul(fr, K(0.25, 400, 650), 450, 520), cy, 600, 560)
tot = add(lc, rim, 750, 300)
inten = X(unreal.MaterialExpressionScalarParameter, 750, 450)
inten.set_editor_property("parameter_name", "Intensity"); inten.set_editor_property("default_value", 6.0)
out = mul(tot, inten, 900, 320)
MEL.connect_material_property(out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property("used_with_skeletal_mesh", True)
m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)      # property change -> compiles
EAL.save_asset("%s/%s" % (PATH, NAME), only_if_is_dirty=False)

# big arcs: a copy of NS_AdrenalineSpark, retuned next into long bolts whipping off around / behind him
ARC = "NS_AdrenalineArcs"
if not unreal.load_object(None, "%s/%s.%s" % (PATH, ARC, ARC)):
    EAL.duplicate_asset(PATH + "/NS_AdrenalineSpark", "%s/%s" % (PATH, ARC))
    EAL.save_asset("%s/%s" % (PATH, ARC), only_if_is_dirty=False)
unreal.log_warning("[ESKIN] %s blend %s, arcs %s" % (NAME, m.get_editor_property("blend_mode"), bool(unreal.load_object(None, "%s/%s.%s" % (PATH, ARC, ARC)))))
