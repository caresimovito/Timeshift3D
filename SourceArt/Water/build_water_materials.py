"""Rebuild M_SwampWater and M_RiverWater as Single Layer Water materials (run inside the editor).
Imports T_Water_Ripple_N / T_Water_Noise from this folder into /Game/Timeshift/Environment/Water/Textures."""
import unreal

SRC = r'C:/repos/Unreal Projects/Timeshift3D/SourceArt/Water/'
DST = '/Game/Timeshift/Environment/Water'
MEL = unreal.MaterialEditingLibrary
log = lambda m: unreal.log('WATERBUILD ' + str(m))

# --- textures ---------------------------------------------------------------
tasks = []
for name in ['T_Water_Ripple_N', 'T_Water_Noise']:
    t = unreal.AssetImportTask()
    t.set_editor_property('filename', SRC + name + '.png')
    t.set_editor_property('destination_path', DST + '/Textures')
    t.set_editor_property('destination_name', name)
    t.set_editor_property('automated', True)
    t.set_editor_property('replace_existing', True)
    tasks.append(t)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
ripple = unreal.load_asset(DST + '/Textures/T_Water_Ripple_N')
ripple.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP)
ripple.set_editor_property('srgb', False)
noise = unreal.load_asset(DST + '/Textures/T_Water_Noise')
noise.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
noise.set_editor_property('srgb', False)


def node(mat, cls, x, y):
    return MEL.create_material_expression(mat, cls, x, y)


def const(mat, v, x, y):
    c = node(mat, unreal.MaterialExpressionConstant, x, y)
    c.set_editor_property('r', v)
    return c


def const3(mat, rgb, x, y):
    c = node(mat, unreal.MaterialExpressionConstant3Vector, x, y)
    c.set_editor_property('constant', unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))
    return c


def world_uv(mat, tile, x, y):
    """World XY / tile  -> UV (independent of the plane's scale)."""
    wp = node(mat, unreal.MaterialExpressionWorldPosition, x, y)
    mask = node(mat, unreal.MaterialExpressionComponentMask, x + 150, y)
    mask.set_editor_property('r', True); mask.set_editor_property('g', True)
    mask.set_editor_property('b', False); mask.set_editor_property('a', False)
    MEL.connect_material_expressions(wp, '', mask, '')
    div = node(mat, unreal.MaterialExpressionDivide, x + 300, y)
    div.set_editor_property('const_b', tile)
    MEL.connect_material_expressions(mask, '', div, 'A')
    return div


def panned_sample(mat, tex, tile, speed, x, y, sampler):
    uv = world_uv(mat, tile, x, y)
    pan = node(mat, unreal.MaterialExpressionPanner, x + 450, y)
    pan.set_editor_property('speed_x', speed[0]); pan.set_editor_property('speed_y', speed[1])
    MEL.connect_material_expressions(uv, '', pan, 'Coordinate')
    s = node(mat, unreal.MaterialExpressionTextureSample, x + 650, y)
    s.set_editor_property('texture', tex)
    s.set_editor_property('sampler_type', sampler)
    MEL.connect_material_expressions(pan, '', s, 'UVs')
    return s


def build(path, p):
    mat = unreal.load_asset(path)
    MEL.delete_all_material_expressions(mat)
    for e in list(MEL.get_material_expressions(mat)):   # delete_all leaves some behind
        MEL.delete_material_expression(mat, e)
    log('%s cleared -> %d left' % (path, len(MEL.get_material_expressions(mat))))
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_OPAQUE)
    mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_SINGLE_LAYER_WATER)
    mat.set_editor_property('two_sided', False)

    NM = unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
    MK = unreal.MaterialSamplerType.SAMPLERTYPE_MASKS
    # two ripple layers drifting in different directions
    a = panned_sample(mat, ripple, p['tile'], p['pan1'], -2200, -300, NM)
    b = panned_sample(mat, ripple, p['tile'] * 0.57, p['pan2'], -2200, 0, NM)
    add1 = node(mat, unreal.MaterialExpressionAdd, -1350, -150)
    MEL.connect_material_expressions(a, 'RGB', add1, 'A'); MEL.connect_material_expressions(b, 'RGB', add1, 'B')
    add2 = add1
    flat = const3(mat, (0, 0, 1), -1200, 150)
    strength = const(mat, p['normal_strength'], -1200, 250)
    lerpn = node(mat, unreal.MaterialExpressionLinearInterpolate, -1000, 50)
    MEL.connect_material_expressions(flat, '', lerpn, 'A'); MEL.connect_material_expressions(add2, '', lerpn, 'B')
    MEL.connect_material_expressions(strength, '', lerpn, 'Alpha')
    nrm = node(mat, unreal.MaterialExpressionNormalize, -820, 50)
    MEL.connect_material_expressions(lerpn, '', nrm, 'VectorInput')

    # floating scum / foam mask from slow noise
    n = panned_sample(mat, noise, p['scum_tile'], p['scum_pan'], -2200, 700, MK)
    sub = node(mat, unreal.MaterialExpressionSubtract, -1350, 700)
    sub.set_editor_property('const_b', p['scum_threshold'])
    MEL.connect_material_expressions(n, 'R', sub, 'A')
    mul = node(mat, unreal.MaterialExpressionMultiply, -1200, 700)
    mul.set_editor_property('const_b', p['scum_sharp'])
    MEL.connect_material_expressions(sub, '', mul, 'A')
    sat = node(mat, unreal.MaterialExpressionSaturate, -1050, 700)
    MEL.connect_material_expressions(mul, '', sat, '')
    amount = const(mat, p['scum_amount'], -1050, 800)
    scum = node(mat, unreal.MaterialExpressionMultiply, -900, 720)
    MEL.connect_material_expressions(sat, '', scum, 'A'); MEL.connect_material_expressions(amount, '', scum, 'B')

    rough = node(mat, unreal.MaterialExpressionLinearInterpolate, -700, 450)
    MEL.connect_material_expressions(const(mat, p['roughness'], -900, 420), '', rough, 'A')
    MEL.connect_material_expressions(const(mat, 0.75, -900, 500), '', rough, 'B')
    MEL.connect_material_expressions(scum, '', rough, 'Alpha')

    MEL.connect_material_property(nrm, '', unreal.MaterialProperty.MP_NORMAL)
    MEL.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(const3(mat, p['scum_color'], -700, 600), '', unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(scum, '', unreal.MaterialProperty.MP_OPACITY)
    MEL.connect_material_property(const(mat, p['specular'], -700, 350), '', unreal.MaterialProperty.MP_SPECULAR)

    out = node(mat, unreal.MaterialExpressionSingleLayerWaterMaterialOutput, -300, 900)
    MEL.connect_material_expressions(const3(mat, p['scattering'], -600, 850), '', out, 'ScatteringCoefficients')
    MEL.connect_material_expressions(const3(mat, p['absorption'], -600, 950), '', out, 'AbsorptionCoefficients')
    MEL.connect_material_expressions(const(mat, 0.1, -600, 1050), '', out, 'PhaseG')
    MEL.connect_material_expressions(const(mat, p['behind'], -600, 1130), '', out, 'ColorScaleBehindWater')

    MEL.recompile_material(mat)
    log('%s built (%d expressions)' % (path, len(MEL.get_material_expressions(mat)) if hasattr(MEL, 'get_material_expressions') else -1))


build(DST + '/M_SwampWater', {
    'tile': 700.0, 'pan1': (0.012, 0.006), 'pan2': (-0.007, 0.010), 'pan3': (0.002, -0.003),
    'normal_strength': 0.35, 'roughness': 0.06, 'specular': 0.5,
    # murky green-brown: strong absorption, greenish scattering
    'scattering': (0.11, 0.15, 0.06), 'absorption': (0.7, 0.45, 0.85), 'behind': 0.6,
    'scum_tile': 2600.0, 'scum_pan': (0.0015, 0.001), 'scum_threshold': 0.62, 'scum_sharp': 5.0, 'scum_amount': 0.85,
    'scum_color': (0.05, 0.07, 0.02),
})
# river flows along +Y (the strip is long in Y); faster, clearer, stretched ripples
build(DST + '/M_RiverWater', {
    'tile': 500.0, 'pan1': (0.004, 0.09), 'pan2': (-0.006, 0.06), 'pan3': (0.0, 0.03),
    'normal_strength': 0.45, 'roughness': 0.12, 'specular': 0.35,
    'scattering': (0.02, 0.06, 0.06), 'absorption': (0.45, 0.12, 0.10), 'behind': 0.8,
    'scum_tile': 1400.0, 'scum_pan': (0.0, 0.08), 'scum_threshold': 0.78, 'scum_sharp': 6.0, 'scum_amount': 0.5,
    'scum_color': (0.55, 0.58, 0.52),
})
log('done')
