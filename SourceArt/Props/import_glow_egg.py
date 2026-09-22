"""Import SM_GlowEgg and build M_GlowEgg (dark teal shell, cyan inner glow brighter at the rim). Run in the editor."""
import unreal
MEL = unreal.MaterialEditingLibrary
log = lambda m: unreal.log('GLOWEGG ' + str(m))
DST = '/Game/Timeshift/Environment/Meshes/Nesting'
unreal.SystemLibrary.execute_console_command(None, 'Interchange.FeatureFlags.Import.FBX 0')
o = unreal.FbxImportUI()
o.set_editor_property('import_mesh', True); o.set_editor_property('import_as_skeletal', False)
o.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_STATIC_MESH)
o.set_editor_property('import_materials', False); o.set_editor_property('import_textures', False)
o.static_mesh_import_data.set_editor_property('combine_meshes', True)
o.static_mesh_import_data.set_editor_property('auto_generate_collision', False)
t = unreal.AssetImportTask()
t.set_editor_property('filename', r'C:/repos/Unreal Projects/Timeshift3D/SourceArt/Props/SM_GlowEgg.fbx')
t.set_editor_property('destination_path', DST); t.set_editor_property('destination_name', 'SM_GlowEgg')
t.set_editor_property('automated', True); t.set_editor_property('replace_existing', True); t.set_editor_property('options', o)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])

mat = unreal.load_asset(DST + '/M_GlowEgg')
if mat is None:
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_GlowEgg', DST, unreal.Material, unreal.MaterialFactoryNew())
MEL.delete_all_material_expressions(mat)
for e in list(MEL.get_material_expressions(mat)):
    MEL.delete_material_expression(mat, e)
def n(cls, x, y): return MEL.create_material_expression(mat, cls, x, y)
def c3(r, g, b, x, y):
    e = n(unreal.MaterialExpressionConstant3Vector, x, y); e.set_editor_property('constant', unreal.LinearColor(r, g, b, 1)); return e
def c1(v, x, y):
    e = n(unreal.MaterialExpressionConstant, x, y); e.set_editor_property('r', v); return e
fr = n(unreal.MaterialExpressionFresnel, -900, 200)
fr.set_editor_property('exponent', 2.5)
mul = n(unreal.MaterialExpressionMultiply, -700, 200)
MEL.connect_material_expressions(fr, '', mul, 'A'); MEL.connect_material_expressions(c1(3.5, -900, 320), '', mul, 'B')
add = n(unreal.MaterialExpressionAdd, -550, 200)
MEL.connect_material_expressions(mul, '', add, 'A'); MEL.connect_material_expressions(c1(1.2, -700, 320), '', add, 'B')
em = n(unreal.MaterialExpressionMultiply, -400, 150)
MEL.connect_material_expressions(c3(0.05, 0.85, 0.75, -600, 50), '', em, 'A'); MEL.connect_material_expressions(add, '', em, 'B')
MEL.connect_material_property(c3(0.02, 0.09, 0.09, -400, -100), '', unreal.MaterialProperty.MP_BASE_COLOR)
MEL.connect_material_property(em, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
MEL.connect_material_property(c1(0.25, -400, 350), '', unreal.MaterialProperty.MP_ROUGHNESS)
MEL.recompile_material(mat)
sm = unreal.load_asset(DST + '/SM_GlowEgg')
sm.set_material(0, mat)
for p in [DST + '/SM_GlowEgg', DST + '/M_GlowEgg']:
    unreal.EditorAssetLibrary.save_asset(p)
log('done %s' % sm.get_bounding_box())
