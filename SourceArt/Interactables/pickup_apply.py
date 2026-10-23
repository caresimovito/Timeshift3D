# Editor Python: put a prepared pickup model (pickup_prep.py GLB) on a pickup Blueprint - the herbs recipe made generic
# (2026-10-23). Globals: GLB, DEST (content folder), BP (pickup BP path), TINT (r, g, b emissive tint x the model's own
# colours), GLOW, SCALE, LIGHT (r, g, b 0-255) / LUX (point light 40 cm above, no shadows, 3 m reach; LUX 0 = no light).
# Steps: import -> emissive = base colour x tint -> simple box collision (overlaps) -> BP template mesh / scale ->
# placed instances updated -> light component (added once, named PickupGlow).
import unreal
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
g = globals()
GLB, DEST, BPP = g["GLB"], g["DEST"], g["BP"]
TINT, GLOW, SCALE = g.get("TINT", (1, 1, 1)), float(g.get("GLOW", 1.0)), float(g.get("SCALE", 1.0))
LIGHT, LUX = g.get("LIGHT", (255, 255, 255)), float(g.get("LUX", 0))
t = unreal.AssetImportTask()
t.set_editor_property("filename", GLB)
t.set_editor_property("destination_path", DEST)
t.set_editor_property("replace_existing", True)
t.set_editor_property("automated", True)
t.set_editor_property("save", True)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
mesh = [EAL.load_asset(p.split(".")[0]) for p in EAL.list_assets(DEST, True) if "/StaticMeshes/" in p][0]
mi = mesh.get_material(0)
base = [v.parameter_value for v in mi.get_editor_property("texture_parameter_values") if str(v.parameter_info.name) == "BaseColorTexture"][0]
MEL.set_material_instance_texture_parameter_value(mi, "EmissiveTexture", base)
MEL.set_material_instance_vector_parameter_value(mi, "EmissiveFactor", unreal.LinearColor(TINT[0] * GLOW, TINT[1] * GLOW, TINT[2] * GLOW, 1.0))
EAL.save_asset(mi.get_path_name(), only_if_is_dirty=False)
if unreal.EditorStaticMeshLibrary.get_simple_collision_count(mesh) == 0:
    unreal.EditorStaticMeshLibrary.add_simple_collisions(mesh, unreal.ScriptCollisionShapeType.BOX)
EAL.save_asset(mesh.get_path_name(), only_if_is_dirty=False)
bp = EAL.load_asset(BPP)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
BFL = unreal.SubobjectDataBlueprintFunctionLibrary
handles = sds.k2_gather_subobject_data_for_blueprint(bp)
objs = [BFL.get_object(sds.k2_find_subobject_data_from_handle(h)) for h in handles]
for o in objs:
    if isinstance(o, unreal.StaticMeshComponent):
        o.set_editor_property("static_mesh", mesh)
        o.set_editor_property("override_materials", [])
        o.set_editor_property("relative_scale3d", unreal.Vector(SCALE, SCALE, SCALE))
if LUX > 0:
    lights = [o for o in objs if isinstance(o, unreal.PointLightComponent)]
    if lights:
        lt = lights[0]
    else:
        p = unreal.AddNewSubobjectParams()
        p.set_editor_property("parent_handle", handles[0])
        p.set_editor_property("new_class", unreal.PointLightComponent)
        p.set_editor_property("blueprint_context", bp)
        h, why = sds.add_new_subobject(p)
        sds.rename_subobject(h, unreal.Text("PickupGlow"))
        lt = BFL.get_object(sds.k2_find_subobject_data_from_handle(h))
    lt.set_editor_property("intensity", LUX)
    lt.set_editor_property("light_color", unreal.Color(LIGHT[2], LIGHT[1], LIGHT[0], 255) if False else unreal.Color(r=LIGHT[0], g=LIGHT[1], b=LIGHT[2], a=255))
    lt.set_editor_property("attenuation_radius", 300.0)
    lt.set_editor_property("cast_shadows", False)
    lt.set_editor_property("relative_location", unreal.Vector(0, 0, 40))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset(BPP, only_if_is_dirty=False)
cls = bp.generated_class().get_name()
n = 0
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if a.get_class().get_name() == cls:
        c = a.get_components_by_class(unreal.StaticMeshComponent)[0]
        a.modify()
        c.modify()
        c.set_static_mesh(mesh)
        c.set_material(0, mi)
        c.set_relative_scale3d(unreal.Vector(SCALE, SCALE, SCALE))
        n += 1
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
bb = mesh.get_bounding_box()
unreal.log_warning("[PAPPLY] %s -> %s: tris %d, size %.0f x %.0f x %.0f cm x%.2f, glow %.1f, light %s, placed %d" % (
    mesh.get_name(), BPP.split("/")[-1], mesh.get_num_triangles(0), bb.max.x - bb.min.x, bb.max.y - bb.min.y, bb.max.z - bb.min.z, SCALE, GLOW,
    "%d" % LUX if LUX else "none", n))
