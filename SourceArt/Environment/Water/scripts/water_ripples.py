# Editor Python: wading ripples in the water itself.
#  MPC_Wading: PlayerPos (vector), RippleStrength (scalar), set by the hero every 0.05 s.
#  M_SwampPond: ring ripples around PlayerPos added to the existing normal (world-space slope -> tangent space),
#  wavelength ~40 cm travelling outward, fading out by ~2.2 m. Re-running rebuilds only the RIP_ nodes.
#  Recompile afterwards with the MCP MaterialTools recompile.
import unreal

TAG = "[RIPPLE]"
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
MP = "/Game/Timeshift/Environment/Water/MPC_Wading"
mpc = EAL.load_asset(MP)
if mpc is None:
    mpc = tools.create_asset("MPC_Wading", "/Game/Timeshift/Environment/Water", unreal.MaterialParameterCollection,
                             unreal.MaterialParameterCollectionFactoryNew())
vp = unreal.CollectionVectorParameter()
vp.set_editor_property("parameter_name", "PlayerPos")
vp.set_editor_property("default_value", unreal.LinearColor(0, 0, -100000, 0))
sp = unreal.CollectionScalarParameter()
sp.set_editor_property("parameter_name", "RippleStrength")
sp.set_editor_property("default_value", 0.0)
mpc.set_editor_property("vector_parameters", [vp])
mpc.set_editor_property("scalar_parameters", [sp])
EAL.save_asset(MP, only_if_is_dirty=False)

m = EAL.load_asset("/Game/Timeshift/Environment/Water/M_SwampPond")
old_norm = None
for e in MEL.get_material_expressions(m) if hasattr(MEL, "get_material_expressions") else []:
    pass
# find the existing normal source: Normalize_2 (MCP readback said MP_Normal <- MaterialExpressionNormalize_2)
norm_src = unreal.find_object(None, m.get_path_name() + ":MaterialExpressionNormalize_2")
unreal.log_warning("%s existing normal node: %s" % (TAG, norm_src))
X, Y = -2200, 1400


def node(cls, x, y, **props):
    e = MEL.create_material_expression(m, cls, X + x, Y + y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    e.set_editor_property("desc", "RIP_")
    return e


def link(a, b, inp="", out=""):
    if not MEL.connect_material_expressions(a, out, b, inp):
        unreal.log_warning("%s link failed %s.%s -> %s.%s" % (TAG, a.get_name(), out, b.get_name(), inp))


wp = node(unreal.MaterialExpressionWorldPosition, 0, 0)
wpxy = node(unreal.MaterialExpressionComponentMask, 150, 0, r=True, g=True, b=False, a=False)
link(wp, wpxy)
pp = node(unreal.MaterialExpressionCollectionParameter, 0, 120, collection=mpc, parameter_name="PlayerPos")
ppxy = node(unreal.MaterialExpressionComponentMask, 150, 120, r=True, g=True, b=False, a=False)
link(pp, ppxy)
diff = node(unreal.MaterialExpressionSubtract, 300, 60)
link(wpxy, diff, "A")
link(ppxy, diff, "B")
dist = node(unreal.MaterialExpressionLength, 450, 60)
link(diff, dist)
dmax = node(unreal.MaterialExpressionMax, 600, 140, const_b=1.0)
link(dist, dmax, "A")
dirn = node(unreal.MaterialExpressionDivide, 750, 60)
link(diff, dirn, "A")
link(dmax, dirn, "B")
# phase in cycles: dist/40 - time*1.15  (40 cm wavelength, ~46 cm/s outward)
dcyc = node(unreal.MaterialExpressionDivide, 600, 260, const_b=40.0)
link(dist, dcyc, "A")
tm = node(unreal.MaterialExpressionTime, 450, 340)
tsp = node(unreal.MaterialExpressionMultiply, 600, 340, const_b=1.15)
link(tm, tsp, "A")
ph = node(unreal.MaterialExpressionSubtract, 750, 300)
link(dcyc, ph, "A")
link(tsp, ph, "B")
cs = node(unreal.MaterialExpressionCosine, 900, 300, period=1.0)
link(ph, cs)
# falloff: zero at the legs (inside 12 cm), (1 - d/220)^2 outward
fo1 = node(unreal.MaterialExpressionDivide, 600, 460, const_b=220.0)
link(dist, fo1, "A")
fo2 = node(unreal.MaterialExpressionOneMinus, 750, 460)
link(fo1, fo2)
fo3 = node(unreal.MaterialExpressionSaturate, 900, 460)
link(fo2, fo3)
fo4 = node(unreal.MaterialExpressionMultiply, 1050, 460)
link(fo3, fo4, "A")
link(fo3, fo4, "B")
inner = node(unreal.MaterialExpressionDivide, 900, 560, const_b=12.0)
link(dist, inner, "A")
inner2 = node(unreal.MaterialExpressionSaturate, 1050, 560)
link(inner, inner2)
st = node(unreal.MaterialExpressionCollectionParameter, 900, 660, collection=mpc, parameter_name="RippleStrength")
a1 = node(unreal.MaterialExpressionMultiply, 1200, 460)
link(fo4, a1, "A")
link(inner2, a1, "B")
a2 = node(unreal.MaterialExpressionMultiply, 1350, 460)
link(a1, a2, "A")
link(st, a2, "B")
amp = node(unreal.MaterialExpressionMultiply, 1500, 380)
link(a2, amp, "A")
link(cs, amp, "B")
gain = node(unreal.MaterialExpressionMultiply, 1650, 380, const_b=0.9)
link(amp, gain, "A")
slope = node(unreal.MaterialExpressionMultiply, 1800, 200)
link(dirn, slope, "A")
link(gain, slope, "B")
zero = node(unreal.MaterialExpressionConstant, 1800, 320, r=0.0)
v3 = node(unreal.MaterialExpressionAppendVector, 1950, 220)
link(slope, v3, "A")
link(zero, v3, "B")
tr = node(unreal.MaterialExpressionTransform, 2100, 220, transform_source_type=unreal.MaterialVectorCoordTransformSource.TRANSFORMSOURCE_WORLD,
          transform_type=unreal.MaterialVectorCoordTransform.TRANSFORM_TANGENT)
link(v3, tr)
add = node(unreal.MaterialExpressionAdd, 2250, 120)
link(norm_src, add, "A")
link(tr, add, "B")
nrm = node(unreal.MaterialExpressionNormalize, 2400, 120)
link(add, nrm)
ok = MEL.connect_material_property(nrm, "", unreal.MaterialProperty.MP_NORMAL)
EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)
unreal.log_warning("%s MPC saved, ripple network added, normal connected=%s" % (TAG, ok))
