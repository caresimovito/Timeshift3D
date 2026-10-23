# Editor Python: Regen coil assets (user 2026-10-23 Regen concept: green / gold light ribbons coiling around his limbs;
# the v1 surface-band overlay read as patchy green, so the ribbons are now real geometry floating around each limb).
#   SM_RegenCoil  - procedural helix ribbon (SourceArt/VFX/SM_RegenCoil.obj, make_regen_coil.py), no collision
#   M_RegenRibbon - additive, unlit, two-sided. Light pulses race along the ribbon:
#       s = frac(U x 3 - t x 0.8)   (3 pulses per coil)      head = s^3      edge = (1 - |V - 0.5| x 2)^0.7
#       emissive = lerp(Green, Gold, s^6) x (0.25 + head x 1.6) x edge x Intensity
import unreal
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
PATH = "/Game/Timeshift/VFX/Regen"
t = unreal.AssetImportTask()
t.filename = r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/VFX/SM_RegenCoil.obj"
t.destination_path = PATH; t.destination_name = "SM_RegenCoil"
t.replace_existing = True; t.automated = True; t.save = False
AT.import_asset_tasks([t])
sm = unreal.load_object(None, PATH + "/SM_RegenCoil.SM_RegenCoil")
NAME = "M_RegenRibbon"
m = unreal.load_object(None, "%s/%s.%s" % (PATH, NAME, NAME))
if m:
    MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset(NAME, PATH, unreal.Material, unreal.MaterialFactoryNew())
X = lambda cls, x, y: MEL.create_material_expression(m, cls, x, y)
C = MEL.connect_material_expressions
def K(v, x, y):
    c = X(unreal.MaterialExpressionConstant, x, y); c.set_editor_property("r", v); return c
def mul(a, b, x, y, pa="", pb=""):
    n = X(unreal.MaterialExpressionMultiply, x, y); C(a, pa, n, "A"); C(b, pb, n, "B"); return n
def add(a, b, x, y):
    n = X(unreal.MaterialExpressionAdd, x, y); C(a, "", n, "A"); C(b, "", n, "B"); return n
def chan(src, c, x, y):
    cm = X(unreal.MaterialExpressionComponentMask, x, y)
    for k in "rgba":
        cm.set_editor_property(k, k == c)
    C(src, "", cm, "")
    return cm
uv = X(unreal.MaterialExpressionTextureCoordinate, -1400, 0)
u = chan(uv, "r", -1250, 0)
v = chan(uv, "g", -1250, 200)
tm = X(unreal.MaterialExpressionTime, -1400, 100)
su = add(mul(u, K(3.0, -1250, 80), -1100, 0), mul(tm, K(-0.8, -1250, 160), -1100, 100), -950, 40)
s = X(unreal.MaterialExpressionFrac, -800, 40); C(su, "", s, "")
head = mul(mul(s, s, -650, 0), s, -500, 0)
s6 = mul(head, head, -500, 120)
dv = add(v, K(-0.5, -1250, 280), -1100, 220)
av = X(unreal.MaterialExpressionAbs, -950, 220); C(dv, "", av, "")
ev = X(unreal.MaterialExpressionOneMinus, -800, 220); C(mul(av, K(2.0, -950, 300), -880, 260), "", ev, "")
evs = X(unreal.MaterialExpressionSaturate, -700, 220); C(ev, "", evs, "")
edge = X(unreal.MaterialExpressionPower, -580, 220); C(evs, "", edge, "Base"); C(K(0.7, -700, 300), "", edge, "Exp")
green = X(unreal.MaterialExpressionVectorParameter, -500, -250); green.set_editor_property("parameter_name", "Green")
green.set_editor_property("default_value", unreal.LinearColor(0.2, 1.0, 0.35, 1))
gold = X(unreal.MaterialExpressionVectorParameter, -500, -120); gold.set_editor_property("parameter_name", "Gold")
gold.set_editor_property("default_value", unreal.LinearColor(1.0, 0.8, 0.25, 1))
col = X(unreal.MaterialExpressionLinearInterpolate, -300, -150); C(green, "", col, "A"); C(gold, "", col, "B"); C(s6, "", col, "Alpha")
br = add(K(0.25, -350, 60), mul(head, K(1.6, -350, 120), -250, 80), -150, 60)
inten = X(unreal.MaterialExpressionScalarParameter, -150, 250)
inten.set_editor_property("parameter_name", "Intensity"); inten.set_editor_property("default_value", 6.0)
out = mul(mul(mul(col, br, 0, -50), edge, 150, 50), inten, 300, 100)
MEL.connect_material_property(out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property("two_sided", True)
m.set_editor_property("used_with_niagara_mesh_particles", True)
m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)      # property change -> compiles
EAL.save_asset("%s/%s" % (PATH, NAME), only_if_is_dirty=False)
if sm:
    sm.set_material(0, m)
    bs = sm.get_editor_property("body_setup")
    if bs:
        bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_SIMPLE_AS_COMPLEX)
    EAL.save_asset(PATH + "/SM_RegenCoil", only_if_is_dirty=False)
unreal.log_warning("[RCOIL] mesh %s bounds %s, mat %s" % (bool(sm), sm.get_bounds().box_extent if sm else None, m.get_editor_property("blend_mode")))
