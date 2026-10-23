# Editor Python: BP_Pickup_Health gets a soft green point light (no shadows, 3 m reach) 40 cm above the bundle, so herbs
# hidden in the ferns show as a green glow on the leaves around them (user 2026-10-23: herbs hard to see). Idempotent.
import unreal
EAL = unreal.EditorAssetLibrary
bp = EAL.load_asset("/Game/Timeshift/Interactables/BP_Pickup_Health")
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
BFL = unreal.SubobjectDataBlueprintFunctionLibrary
handles = sds.k2_gather_subobject_data_for_blueprint(bp)
objs = [BFL.get_object(sds.k2_find_subobject_data_from_handle(h)) for h in handles]
lights = [o for o in objs if isinstance(o, unreal.PointLightComponent)]
if not lights:
    p = unreal.AddNewSubobjectParams()
    p.set_editor_property("parent_handle", handles[0])
    p.set_editor_property("new_class", unreal.PointLightComponent)
    p.set_editor_property("blueprint_context", bp)
    h, why = sds.add_new_subobject(p)
    unreal.log_warning("[HLIGHT] add: %s" % why)
    sds.rename_subobject(h, unreal.Text("HerbGlow"))
    lt = BFL.get_object(sds.k2_find_subobject_data_from_handle(h))
else:
    lt = lights[0]
lt.set_editor_property("intensity", float(globals().get("LUX", 2500.0)))
lt.set_editor_property("intensity_units", unreal.LightUnits.CANDELAS if False else lt.get_editor_property("intensity_units"))
lt.set_editor_property("light_color", unreal.Color(110, 255, 110, 255))
lt.set_editor_property("attenuation_radius", 300.0)
lt.set_editor_property("cast_shadows", False)
lt.set_editor_property("relative_location", unreal.Vector(0, 0, 40))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset("/Game/Timeshift/Interactables/BP_Pickup_Health", only_if_is_dirty=False)
unreal.log_warning("[HLIGHT] %s intensity %s units %s" % (lt.get_name(), lt.get_editor_property("intensity"), lt.get_editor_property("intensity_units")))
