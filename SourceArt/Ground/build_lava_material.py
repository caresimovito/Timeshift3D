"""Import SM_LavaRiver and build M_LavaRiver: molten orange-yellow lava drifting slowly, dark cooling crust
plates (cracked-mud pattern) whose cracks glow. Run inside the editor (after PIE, via Saved/run_after_pie.py).
Also re-exports the landscape heights to Saved/land_dump_v5.bin to verify the v5 import."""
import unreal
MEL = unreal.MaterialEditingLibrary
log = lambda m: unreal.log('LAVA ' + str(m))
DST = '/Game/Timeshift/Environment/Ground/Lava'

unreal.SystemLibrary.execute_console_command(None, 'Interchange.FeatureFlags.Import.FBX 0')
o = unreal.FbxImportUI()
o.set_editor_property('import_mesh', True); o.set_editor_property('import_as_skeletal', False)
o.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_STATIC_MESH)
o.set_editor_property('import_materials', False); o.set_editor_property('import_textures', False)
o.static_mesh_import_data.set_editor_property('combine_meshes', True)
o.static_mesh_import_data.set_editor_property('auto_generate_collision', False)
t = unreal.AssetImportTask()
t.set_editor_property('filename', r'C:/repos/Unreal Projects/Timeshift3D/SourceArt/Ground/SM_LavaRiver.fbx')
t.set_editor_property('destination_path', DST); t.set_editor_property('destination_name', 'SM_LavaRiver')
t.set_editor_property('automated', True); t.set_editor_property('replace_existing', True); t.set_editor_property('options', o)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])

noise = unreal.load_asset('/Game/Timeshift/Environment/Water/Textures/T_Water_Noise')
mud = unreal.load_asset('/Game/Timeshift/Environment/Ground/Path/T_CrackedMud_BC')
mudn = unreal.load_asset('/Game/Timeshift/Environment/Ground/Path/T_CrackedMud_N')
mat = unreal.load_asset(DST + '/M_LavaRiver')
if mat is None:
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_LavaRiver', DST, unreal.Material, unreal.MaterialFactoryNew())
MEL.delete_all_material_expressions(mat)
for e in list(MEL.get_material_expressions(mat)):
    MEL.delete_material_expression(mat, e)


def n(cls, x, y):
    return MEL.create_material_expression(mat, cls, x, y)


def c1(v, x, y):
    e = n(unreal.MaterialExpressionConstant, x, y); e.set_editor_property('r', v); return e


def c3(r, g, b, x, y):
    e = n(unreal.MaterialExpressionConstant3Vector, x, y)
    e.set_editor_property('constant', unreal.LinearColor(r, g, b, 1)); return e


def wuv(tile, sx, sy, x, y):
    wp = n(unreal.MaterialExpressionWorldPosition, x, y)
    m = n(unreal.MaterialExpressionComponentMask, x + 150, y)
    m.set_editor_property('r', True); m.set_editor_property('g', True)
    m.set_editor_property('b', False); m.set_editor_property('a', False)
    MEL.connect_material_expressions(wp, '', m, '')
    d = n(unreal.MaterialExpressionDivide, x + 300, y); d.set_editor_property('const_b', tile)
    MEL.connect_material_expressions(m, '', d, 'A')
    p = n(unreal.MaterialExpressionPanner, x + 450, y)
    p.set_editor_property('speed_x', sx); p.set_editor_property('speed_y', sy)
    MEL.connect_material_expressions(d, '', p, 'Coordinate')
    return p


def samp(tex, uv, st, x, y):
    s = n(unreal.MaterialExpressionTextureSample, x, y)
    s.set_editor_property('texture', tex); s.set_editor_property('sampler_type', st)
    MEL.connect_material_expressions(uv, '', s, 'UVs'); return s


MK = unreal.MaterialSamplerType.SAMPLERTYPE_MASKS
# heat field: product of two slow drifting noises
n1 = samp(noise, wuv(900.0, 0.004, 0.001, -2400, -200), MK, -1700, -200)
n2 = samp(noise, wuv(380.0, -0.006, 0.003, -2400, 100), MK, -1700, 100)
heat = n(unreal.MaterialExpressionMultiply, -1400, -50)
MEL.connect_material_expressions(n1, 'R', heat, 'A'); MEL.connect_material_expressions(n2, 'R', heat, 'B')
# crust where heat is low: saturate((0.30 - heat) * 5)
sub = n(unreal.MaterialExpressionSubtract, -1250, -50)
MEL.connect_material_expressions(c1(0.30, -1400, 60), '', sub, 'A'); MEL.connect_material_expressions(heat, '', sub, 'B')
mul = n(unreal.MaterialExpressionMultiply, -1100, -50); mul.set_editor_property('const_b', 5.0)
MEL.connect_material_expressions(sub, '', mul, 'A')
crust = n(unreal.MaterialExpressionSaturate, -950, -50); MEL.connect_material_expressions(mul, '', crust, '')
# glowing cracks inside the crust, from the cracked-mud pattern (its cracks are dark)
muv = wuv(220.0, 0.002, 0.0005, -2400, 400)
mb = samp(mud, muv, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -1700, 400)
crk = n(unreal.MaterialExpressionOneMinus, -1400, 400); MEL.connect_material_expressions(mb, 'R', crk, '')
cp = n(unreal.MaterialExpressionPower, -1250, 400)
MEL.connect_material_expressions(crk, '', cp, 'Base'); MEL.connect_material_expressions(c1(4.0, -1400, 500), '', cp, 'Exp')
# molten colour: orange -> yellow with heat
hot = n(unreal.MaterialExpressionLinearInterpolate, -800, -300)
MEL.connect_material_expressions(c3(2.6, 0.42, 0.04, -1000, -380), '', hot, 'A')
MEL.connect_material_expressions(c3(5.0, 1.5, 0.15, -1000, -300), '', hot, 'B')
MEL.connect_material_expressions(heat, '', hot, 'Alpha')
# emissive = lerp(hot, hot * cracks * 0.7, crust)
cg = n(unreal.MaterialExpressionMultiply, -800, 300)
MEL.connect_material_expressions(hot, '', cg, 'A'); MEL.connect_material_expressions(cp, '', cg, 'B')
cg2 = n(unreal.MaterialExpressionMultiply, -650, 300); cg2.set_editor_property('const_b', 0.7)
MEL.connect_material_expressions(cg, '', cg2, 'A')
em = n(unreal.MaterialExpressionLinearInterpolate, -450, 0)
MEL.connect_material_expressions(hot, '', em, 'A'); MEL.connect_material_expressions(cg2, '', em, 'B')
MEL.connect_material_expressions(crust, '', em, 'Alpha')
bc = n(unreal.MaterialExpressionLinearInterpolate, -450, -250)
MEL.connect_material_expressions(c3(0.25, 0.06, 0.01, -650, -330), '', bc, 'A')
MEL.connect_material_expressions(c3(0.035, 0.03, 0.028, -650, -250), '', bc, 'B')
MEL.connect_material_expressions(crust, '', bc, 'Alpha')
rough = n(unreal.MaterialExpressionLinearInterpolate, -450, 450)
MEL.connect_material_expressions(c1(0.35, -650, 420), '', rough, 'A'); MEL.connect_material_expressions(c1(0.9, -650, 480), '', rough, 'B')
MEL.connect_material_expressions(crust, '', rough, 'Alpha')
nrm = samp(mudn, muv, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, -1700, 700)
MEL.connect_material_property(bc, '', unreal.MaterialProperty.MP_BASE_COLOR)
MEL.connect_material_property(em, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
MEL.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
MEL.connect_material_property(nrm, 'RGB', unreal.MaterialProperty.MP_NORMAL)
MEL.recompile_material(mat)
sm = unreal.load_asset(DST + '/SM_LavaRiver'); sm.set_material(0, mat)
for p in [DST + '/SM_LavaRiver', DST + '/M_LavaRiver']:
    unreal.EditorAssetLibrary.save_asset(p)

# verify the v5 landscape import with a fresh export
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
L = [a for a in eas.get_all_level_actors() if isinstance(a, unreal.Landscape)][0]
rt = unreal.RenderingLibrary.create_render_target2d(world, 2206, 505, unreal.TextureRenderTargetFormat.RTF_RGBA8)
L.landscape_export_heightmap_to_render_target(rt, True, True)
px = unreal.RenderingLibrary.read_render_target(world, rt)
with open(r'C:/repos/Unreal Projects/Timeshift3D/Saved/land_dump_v5.bin', 'wb') as f:
    f.write(bytes(b for c in px for b in (c.r, c.g)))
log('done %s nodes %d' % (sm.get_bounding_box(), len(MEL.get_material_expressions(mat))))
