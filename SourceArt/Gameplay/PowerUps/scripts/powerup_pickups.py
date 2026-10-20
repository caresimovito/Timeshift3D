# Editor Python: Fury + Regeneration pickups.
#  - BP_Pickup_Fury / BP_Pickup_Regen = duplicates of BP_Pickup_Adrenaline (EventInteract rewritten with the DSL afterwards)
#  - M_PickupGlow (base colour + strong emissive from a Color param, slow pulse) + MI_PickupFury (red) / MI_PickupRegen (green)
#  - recompiles the hero; reports mesh sizes for SM_Mushrooms / SM_Fern_01 so the regen herb can be scaled
import unreal
TAG = "[PUP]"
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
unreal.BlueprintEditorLibrary.compile_blueprint(EAL.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"))
I = "/Game/Timeshift/Interactables/"
for n in ("BP_Pickup_Fury", "BP_Pickup_Regen"):
    if not EAL.does_asset_exist(I + n):
        EAL.duplicate_asset(I + "BP_Pickup_Adrenaline", I + n)
    EAL.save_asset(I + n, only_if_is_dirty=False)

D = "/Game/Timeshift/Interactables/Materials"
m = EAL.load_asset(D + "/M_PickupGlow") or tools.create_asset("M_PickupGlow", D, unreal.Material, unreal.MaterialFactoryNew())
MEL.delete_all_material_expressions(m)
col = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -700, 0)
col.set_editor_property("parameter_name", "GlowColor")
col.set_editor_property("default_value", unreal.LinearColor(1, 0.2, 0.1, 1))
t = MEL.create_material_expression(m, unreal.MaterialExpressionTime, -900, 250)
sn = MEL.create_material_expression(m, unreal.MaterialExpressionSine, -750, 250)
sn.set_editor_property("period", 1.6)
MEL.connect_material_expressions(t, "", sn, "")
pulse = MEL.create_material_expression(m, unreal.MaterialExpressionMultiplyAdd if hasattr(unreal, "MaterialExpressionMultiplyAdd") else unreal.MaterialExpressionAdd, -600, 250)
# pulse = 6 + 3*sin  (emissive strength between 3 and 9)
mul3 = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -600, 250)
mul3.set_editor_property("const_b", 3.0)
MEL.connect_material_expressions(sn, "", mul3, "A")
add6 = MEL.create_material_expression(m, unreal.MaterialExpressionAdd, -450, 250)
add6.set_editor_property("const_b", 6.0)
MEL.connect_material_expressions(mul3, "", add6, "A")
MEL.delete_material_expression(m, pulse)
em = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, 100)
MEL.connect_material_expressions(col, "", em, "A")
MEL.connect_material_expressions(add6, "", em, "B")
bc = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, -100)
bc.set_editor_property("const_b", 0.6)
MEL.connect_material_expressions(col, "", bc, "A")
MEL.connect_material_property(bc, "", unreal.MaterialProperty.MP_BASE_COLOR)
MEL.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
rough = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -300, 300)
rough.set_editor_property("r", 0.4)
MEL.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)
for name, c in (("MI_PickupFury", unreal.LinearColor(1.0, 0.12, 0.04, 1)), ("MI_PickupRegen", unreal.LinearColor(0.15, 1.0, 0.25, 1))):
    mi = EAL.load_asset(D + "/" + name) or tools.create_asset(name, D, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mi.set_editor_property("parent", m)
    MEL.set_material_instance_vector_parameter_value(mi, "GlowColor", c)
    MEL.update_material_instance(mi)
    EAL.save_asset(mi.get_path_name(), only_if_is_dirty=False)
for p in ("/Game/Timeshift/Environment/Meshes/SM_Fern_01", ):
    pass
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if a.get_class().get_name() == "BP_Pickup_Health_C":
        sm = a.get_component_by_class(unreal.StaticMeshComponent).static_mesh
        b = sm.get_bounding_box()
        unreal.log_warning("%s mushrooms %s size=(%.0f,%.0f,%.0f)" % (TAG, sm.get_path_name(), b.max.x - b.min.x, b.max.y - b.min.y, b.max.z - b.min.z))
        break
fern = [p for p in EAL.list_assets("/Game/Timeshift", True) if p.split(".")[-1] == "SM_Fern_01"]
if fern:
    b = EAL.load_asset(fern[0]).get_bounding_box()
    unreal.log_warning("%s fern %s size=(%.0f,%.0f,%.0f)" % (TAG, fern[0], b.max.x - b.min.x, b.max.y - b.min.y, b.max.z - b.min.z))
unreal.log_warning("%s pickups=%s mats ok" % (TAG, [EAL.does_asset_exist(I + n) for n in ("BP_Pickup_Fury", "BP_Pickup_Regen")]))
