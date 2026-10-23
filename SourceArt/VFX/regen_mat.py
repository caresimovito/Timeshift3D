# Editor Python: REGEN look (user 2026-10-23 picked the Grok "golden spiral" concept: green and gold healing ribbons
# spiralling around his legs, torso and arms, with glowing motes).
#   M_RegenSpiral (additive overlay, unlit). In pre-skinned local space P (cm; hero rest pose: Z up 0-180, arms out
#   along +-X angled down), thin bands = planes slightly tilted across X, drifting upward over time -> rings around each
#   leg / the torso / each arm that climb like spirals; a slow noise mask breaks them into ribbon segments:
#     g = band(frac(P.z x 0.05 + P.x x 0.012 - t x 0.45))           green ribbon
#     y = band(frac(P.z x 0.05 - P.x x 0.012 - t x 0.45 + 0.5))     gold ribbon, opposite tilt (they cross)
#     band(f) = saturate(1 - |f - 0.5| x 14)^2 ;  mask = saturate(noise(P x 0.03 + t x 0.3) x 3 + 0.4)
#     emissive = (g x green + y x gold) x mask x Intensity + fresnel^3 x 0.12 x green
#   NS_RegenMotes: copy of NS_AdrenalineBody, retuned next (bolts off, green-gold motes rising off his bones)
# Compiles through the blend-mode property change (no recompile_material call).
import unreal
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
PATH, NAME = "/Game/Timeshift/VFX/Regen", "M_RegenSpiral"
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
def add(a, b, x, y, pa="", pb=""):
    n = X(unreal.MaterialExpressionAdd, x, y); C(a, pa, n, "A"); C(b, pb, n, "B"); return n
pos_raw = X(unreal.MaterialExpressionPreSkinnedPosition, -2000, 0)
# PosScale (v2): PIE showed grainy speckle instead of bands - pre-skinned units differ from the assumed cm; tuned in the MI
psc = X(unreal.MaterialExpressionScalarParameter, -2200, 150); psc.set_editor_property("parameter_name", "PosScale"); psc.set_editor_property("default_value", 1.0)
pos = X(unreal.MaterialExpressionMultiply, -2100, 60); C(pos_raw, "", pos, "A"); C(psc, "", pos, "B")
tm = X(unreal.MaterialExpressionTime, -2000, 300)
drift = mul(tm, K(-0.45, -2000, 400), -1800, 320)
def chan(src, c, x, y):
    cm = X(unreal.MaterialExpressionComponentMask, x, y)
    for k in "rgba":
        cm.set_editor_property(k, k == c)
    C(src, "", cm, "")
    return cm
zz = mul(chan(pos, "b", -1950, 60), K(0.05, -2000, 120), -1800, 60)        # P.z
xx = mul(chan(pos, "r", -1950, 160), K(0.012, -2000, 200), -1800, 160)     # P.x
def band(coord, x, y):
    fr = X(unreal.MaterialExpressionFrac, x, y); C(coord, "", fr, "")
    d = add(fr, K(-0.5, x, y + 80), x + 120, y)
    ab = X(unreal.MaterialExpressionAbs, x + 240, y); C(d, "", ab, "")
    k = mul(ab, K(14.0, x + 240, y + 80), x + 360, y)
    inv = X(unreal.MaterialExpressionOneMinus, x + 480, y); C(k, "", inv, "")
    sat = X(unreal.MaterialExpressionSaturate, x + 600, y); C(inv, "", sat, "")
    return mul(sat, sat, x + 720, y)
cg = add(add(zz, xx, -1600, 60), drift, -1450, 100)
g = band(cg, -1300, 0)
sub = X(unreal.MaterialExpressionSubtract, -1600, 200); C(zz, "", sub, "A"); C(xx, "", sub, "B")
cy = add(add(sub, drift, -1450, 220), K(0.5, -1450, 300), -1350, 220)
yb = band(cy, -1300, 250)
ps = mul(pos, K(0.03, -1300, 500), -1150, 500)
tsh = mul(tm, K(0.3, -1300, 600), -1150, 600)
nz = X(unreal.MaterialExpressionNoise, -1000, 520)
nz.set_editor_property("scale", 1.0); nz.set_editor_property("output_min", -1.0); nz.set_editor_property("output_max", 1.0)
nz.set_editor_property("levels", 2)
C(add(ps, tsh, -1080, 560), "", nz, "Position")
mk = add(mul(nz, K(3.0, -850, 620), -750, 540), K(0.4, -750, 640), -620, 560)
mask = X(unreal.MaterialExpressionSaturate, -500, 560); C(mk, "", mask, "")
green = X(unreal.MaterialExpressionVectorParameter, -400, -150); green.set_editor_property("parameter_name", "Green")
green.set_editor_property("default_value", unreal.LinearColor(0.2, 1.0, 0.35, 1))
gold = X(unreal.MaterialExpressionVectorParameter, -400, 300); gold.set_editor_property("parameter_name", "Gold")
gold.set_editor_property("default_value", unreal.LinearColor(1.0, 0.75, 0.2, 1))
rib = add(mul(g, green, -250, 0), mul(yb, gold, -250, 250), -100, 120)
inten = X(unreal.MaterialExpressionScalarParameter, -100, 400)
inten.set_editor_property("parameter_name", "Intensity"); inten.set_editor_property("default_value", 4.0)
rm = mul(mul(rib, mask, 50, 200), inten, 200, 250)
fr = X(unreal.MaterialExpressionFresnel, 50, 500); fr.set_editor_property("exponent", 3.0)
rim = mul(mul(fr, K(0.12, 50, 600), 200, 520), green, 350, 520)
out = add(rm, rim, 500, 350)
MEL.connect_material_property(out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property("used_with_skeletal_mesh", True)
m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)      # property change -> compiles
EAL.save_asset("%s/%s" % (PATH, NAME), only_if_is_dirty=False)
NS = "NS_RegenMotes"
if not unreal.load_object(None, "%s/%s.%s" % (PATH, NS, NS)):
    EAL.duplicate_asset("/Game/Timeshift/VFX/Adrenaline/NS_AdrenalineBody", "%s/%s" % (PATH, NS))
    EAL.save_asset("%s/%s" % (PATH, NS), only_if_is_dirty=False)
unreal.log_warning("[REGENM] %s blend %s, motes %s" % (NAME, m.get_editor_property("blend_mode"), bool(unreal.load_object(None, "%s/%s.%s" % (PATH, NS, NS)))))

MIN = "MI_RegenSpiral"
mi = unreal.load_object(None, "%s/%s.%s" % (PATH, MIN, MIN))
if not mi:
    mi = AT.create_asset(MIN, PATH, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, m)
EAL.save_asset("%s/%s" % (PATH, MIN), only_if_is_dirty=False)
unreal.log_warning("[MI] %s ready" % MIN)
