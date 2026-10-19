# Editor Python: materials for the swamp sink hazards.
#  M_MudDecal - deferred decal: wet dark mud (glossy), soft broken edge from radial mask x noise.
#  M_Tar      - opaque near-black, very glossy tar with a slow, heavy ripple normal.
# Recompile both afterwards with the MCP MaterialTools recompile.
import unreal

TAG = "[HMAT]"
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
D = "/Game/Timeshift/Hazards/Materials"
noise = EAL.load_asset("/Game/Timeshift/Environment/Water/Textures/T_Water_Noise")
ripn = EAL.load_asset("/Game/Timeshift/Environment/Water/Textures/T_Water_Ripple_N")


def mk(name):
    m = EAL.load_asset(D + "/" + name) or unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        name, D, unreal.Material, unreal.MaterialFactoryNew())
    MEL.delete_all_material_expressions(m)
    return m


def builder(m):
    def node(cls, x, y, **props):
        e = MEL.create_material_expression(m, cls, x, y)
        for k, v in props.items():
            e.set_editor_property(k, v)
        return e

    def link(a, b, inp="", out=""):
        if not MEL.connect_material_expressions(a, out, b, inp):
            unreal.log_warning("%s %s link failed %s.%s -> %s.%s" % (TAG, m.get_name(), a.get_name(), out, b.get_name(), inp))
    return node, link


# ---- mud decal
m = mk("M_MudDecal")
node, link = builder(m)
uv = node(unreal.MaterialExpressionTextureCoordinate, -1400, 0)
c = node(unreal.MaterialExpressionConstant2Vector, -1400, 120, r=0.5, g=0.5)
sub = node(unreal.MaterialExpressionSubtract, -1250, 0)
link(uv, sub, "A")
link(c, sub, "B")
ln = node(unreal.MaterialExpressionLength, -1100, 0)
link(sub, ln)
rad = node(unreal.MaterialExpressionOneMinus, -950, 0)
r2 = node(unreal.MaterialExpressionMultiply, -1000, 80, const_b=2.0)
link(ln, r2, "A")
link(r2, rad)
tcn = node(unreal.MaterialExpressionTextureCoordinate, -1400, 300, utiling=2.5, vtiling=2.5)
nz = node(unreal.MaterialExpressionTextureSample, -1200, 300, texture=noise)
link(tcn, nz, "UVs")
edge = node(unreal.MaterialExpressionAdd, -800, 100)
link(rad, edge, "A")
nzs = node(unreal.MaterialExpressionMultiply, -950, 300, const_b=0.6)
link(nz, nzs, "A", "R")
link(nzs, edge, "B")
e3 = node(unreal.MaterialExpressionMultiply, -650, 100, const_b=2.5)
link(edge, e3, "A")
e4 = node(unreal.MaterialExpressionSubtract, -520, 100, const_b=0.9)
link(e3, e4, "A")
op = node(unreal.MaterialExpressionSaturate, -400, 100)
link(e4, op)
dark = node(unreal.MaterialExpressionConstant3Vector, -650, -250, constant=unreal.LinearColor(0.055, 0.038, 0.022, 1))
wet = node(unreal.MaterialExpressionConstant3Vector, -650, -150, constant=unreal.LinearColor(0.11, 0.075, 0.042, 1))
bc = node(unreal.MaterialExpressionLinearInterpolate, -400, -200)
link(dark, bc, "A")
link(wet, bc, "B")
link(nz, bc, "Alpha", "R")
rough = node(unreal.MaterialExpressionLinearInterpolate, -400, -50, const_a=0.12, const_b=0.38)
link(nz, rough, "Alpha", "G")
MEL.connect_material_property(bc, "", unreal.MaterialProperty.MP_BASE_COLOR)
MEL.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
MEL.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
m.set_editor_property("material_domain", unreal.MaterialDomain.MD_DEFERRED_DECAL)
m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)

# ---- tar
m = mk("M_Tar")
node, link = builder(m)
tc = node(unreal.MaterialExpressionTextureCoordinate, -1400, 200, utiling=0.6, vtiling=0.6)
wp = node(unreal.MaterialExpressionWorldPosition, -1600, 200)
wxy = node(unreal.MaterialExpressionComponentMask, -1450, 200, r=True, g=True, b=False, a=False)
link(wp, wxy)
sc = node(unreal.MaterialExpressionDivide, -1300, 200, const_b=900.0)
link(wxy, sc, "A")
pn = node(unreal.MaterialExpressionPanner, -1150, 200, speed_x=0.004, speed_y=0.002)
link(sc, pn, "Coordinate")
nt = node(unreal.MaterialExpressionTextureSample, -950, 200, texture=ripn, sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
link(pn, nt, "UVs")
flat = node(unreal.MaterialExpressionConstant3Vector, -950, 400, constant=unreal.LinearColor(0, 0, 1, 1))
nl = node(unreal.MaterialExpressionLinearInterpolate, -700, 250, const_alpha=0.35)
link(flat, nl, "A")
link(nt, nl, "B", "RGB")
bcol = node(unreal.MaterialExpressionConstant3Vector, -700, 0, constant=unreal.LinearColor(0.012, 0.009, 0.006, 1))
MEL.connect_material_property(bcol, "", unreal.MaterialProperty.MP_BASE_COLOR)
MEL.connect_material_property(node(unreal.MaterialExpressionConstant, -700, 100, r=0.06), "", unreal.MaterialProperty.MP_ROUGHNESS)
MEL.connect_material_property(node(unreal.MaterialExpressionConstant, -700, 160, r=0.7), "", unreal.MaterialProperty.MP_SPECULAR)
MEL.connect_material_property(nl, "", unreal.MaterialProperty.MP_NORMAL)
EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)
unreal.log_warning("%s built M_MudDecal + M_Tar (noise=%s ripple=%s)" % (TAG, noise is not None, ripn is not None))
