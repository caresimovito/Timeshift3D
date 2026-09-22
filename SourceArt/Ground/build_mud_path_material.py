"""Build M_CrackedMudPath_Decal (deferred decal, cracked dry mud, soft ragged round edge). Run inside the editor."""
import unreal

SRC = r'C:/repos/Unreal Projects/Timeshift3D/SourceArt/Ground/'
DST = '/Game/Timeshift/Environment/Ground/Path'
MEL = unreal.MaterialEditingLibrary
log = lambda m: unreal.log('MUDPATH ' + str(m))

tasks = []
for name in ['T_CrackedMud_BC', 'T_CrackedMud_N', 'T_CrackedMud_R']:
    t = unreal.AssetImportTask()
    t.set_editor_property('filename', SRC + name + '.png')
    t.set_editor_property('destination_path', DST)
    t.set_editor_property('destination_name', name)
    t.set_editor_property('automated', True)
    t.set_editor_property('replace_existing', True)
    tasks.append(t)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
bc = unreal.load_asset(DST + '/T_CrackedMud_BC')
nm = unreal.load_asset(DST + '/T_CrackedMud_N')
nm.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP)
nm.set_editor_property('srgb', False)
rg = unreal.load_asset(DST + '/T_CrackedMud_R')
rg.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
rg.set_editor_property('srgb', False)
noise = unreal.load_asset('/Game/Timeshift/Environment/Water/Textures/T_Water_Noise')

path = DST + '/M_CrackedMudPath_Decal'
mat = unreal.load_asset(path)
if mat is None:
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_CrackedMudPath_Decal', DST, unreal.Material, unreal.MaterialFactoryNew())
MEL.delete_all_material_expressions(mat)
for e in list(MEL.get_material_expressions(mat)):
    MEL.delete_material_expression(mat, e)
mat.set_editor_property('material_domain', unreal.MaterialDomain.MD_DEFERRED_DECAL)
mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)


def node(cls, x, y):
    return MEL.create_material_expression(mat, cls, x, y)


def const(v, x, y):
    c = node(unreal.MaterialExpressionConstant, x, y); c.set_editor_property('r', v); return c


def world_uv(tile, x, y):
    wp = node(unreal.MaterialExpressionWorldPosition, x, y)
    m = node(unreal.MaterialExpressionComponentMask, x + 150, y)
    m.set_editor_property('r', True); m.set_editor_property('g', True)
    m.set_editor_property('b', False); m.set_editor_property('a', False)
    MEL.connect_material_expressions(wp, '', m, '')
    d = node(unreal.MaterialExpressionDivide, x + 300, y); d.set_editor_property('const_b', tile)
    MEL.connect_material_expressions(m, '', d, 'A')
    return d


def sample(tex, uv, stype, x, y):
    s = node(unreal.MaterialExpressionTextureSample, x, y)
    s.set_editor_property('texture', tex); s.set_editor_property('sampler_type', stype)
    MEL.connect_material_expressions(uv, '', s, 'UVs')
    return s


uv = world_uv(260.0, -1600, 0)                      # 2.6 m texture tile, same everywhere
sbc = sample(bc, uv, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -1100, -200)
snm = sample(nm, uv, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, -1100, 50)
srg = sample(rg, uv, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS, -1100, 300)

# round, ragged edge: r = |decalUV - 0.5| * 2, pushed around by a slow world-space noise
tc = node(unreal.MaterialExpressionTextureCoordinate, -1600, 600)
sub = node(unreal.MaterialExpressionSubtract, -1400, 600); sub.set_editor_property('const_b', 0.5)
MEL.connect_material_expressions(tc, '', sub, 'A')
ln = node(unreal.MaterialExpressionLength, -1250, 600)
MEL.connect_material_expressions(sub, '', ln, '')
r2 = node(unreal.MaterialExpressionMultiply, -1100, 600); r2.set_editor_property('const_b', 2.0)
MEL.connect_material_expressions(ln, '', r2, 'A')
nuv = world_uv(420.0, -1600, 850)
nz = sample(noise, nuv, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS, -1100, 850)
nzc = node(unreal.MaterialExpressionSubtract, -900, 850); nzc.set_editor_property('const_b', 0.5)
MEL.connect_material_expressions(nz, 'R', nzc, 'A')
nzs = node(unreal.MaterialExpressionMultiply, -750, 850); nzs.set_editor_property('const_b', 0.45)
MEL.connect_material_expressions(nzc, '', nzs, 'A')
rr = node(unreal.MaterialExpressionAdd, -900, 650)
MEL.connect_material_expressions(r2, '', rr, 'A'); MEL.connect_material_expressions(nzs, '', rr, 'B')
ss = node(unreal.MaterialExpressionSmoothStep, -700, 650)
MEL.connect_material_expressions(const(0.95, -900, 750), '', ss, 'Min')
MEL.connect_material_expressions(const(0.5, -900, 800), '', ss, 'Max')
MEL.connect_material_expressions(rr, '', ss, 'Value')

tintmul = node(unreal.MaterialExpressionMultiply, -700, -200)
tint = node(unreal.MaterialExpressionConstant3Vector, -900, -300)
tint.set_editor_property('constant', unreal.LinearColor(0.62, 0.52, 0.42, 1.0))   # darker, warmer sun-baked clay
MEL.connect_material_expressions(sbc, 'RGB', tintmul, 'A'); MEL.connect_material_expressions(tint, '', tintmul, 'B')
MEL.connect_material_property(tintmul, '', unreal.MaterialProperty.MP_BASE_COLOR)
MEL.connect_material_property(snm, 'RGB', unreal.MaterialProperty.MP_NORMAL)
MEL.connect_material_property(srg, 'R', unreal.MaterialProperty.MP_ROUGHNESS)
MEL.connect_material_property(ss, '', unreal.MaterialProperty.MP_OPACITY)
MEL.recompile_material(mat)
log('built %d nodes' % len(MEL.get_material_expressions(mat)))
