# Editor Python: finish + place the rockfall.
#  - BP_FallingRock: centre the boulder on the actor (SM_Boulder_01 pivot is at its base, 150 cm tall), Damage 20
#  - BP_Rockfall defaults, then one instance "Rockfall_Trap" over the path under Rockfall_Cliff (folder Hazards/Rockfall)
#    with the landscape height grid from rockfall_grid.json and the cliff lip line (visible-surface traces, cliff_lip / rockfall_grid.py)
import json
import unreal

TAG = "[RFP]"
EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
LIB = unreal.SubobjectDataBlueprintFunctionLibrary
fr = EAL.load_asset("/Game/Timeshift/Hazards/BP_FallingRock")
for h in sds.k2_gather_subobject_data_for_blueprint(fr):
    ob = LIB.get_object(sds.k2_find_subobject_data_from_handle(h))
    if ob and ob.get_name().startswith("Rock"):
        ob.set_editor_property("relative_location", unreal.Vector(0, 0, -75))
        ob.set_editor_property("cast_shadow", True)
unreal.BlueprintEditorLibrary.compile_blueprint(fr)
unreal.get_default_object(unreal.load_class(None, "/Game/Timeshift/Hazards/BP_FallingRock.BP_FallingRock_C")).set_editor_property("Damage", 20.0)
EAL.save_asset("/Game/Timeshift/Hazards/BP_FallingRock", only_if_is_dirty=False)

cls = unreal.load_class(None, "/Game/Timeshift/Hazards/BP_Rockfall.BP_Rockfall_C")
g = json.load(open(r"C:/agentpy/rockfall_grid.json"))
vals = {"RockCount": 8, "Cooldown": 25.0, "WarnTime": 1.4, "TXMin": 49300.0, "TXMax": 50900.0, "TYMin": -250.0, "TYMax": 1150.0,
        "LipA": unreal.Vector(49800, 1380, 880), "LipB": unreal.Vector(50250, 1980, 1060),
        "GX0": g["x0"], "GY0": g["y0"], "GStep": g["step"], "GNX": g["nx"], "GNY": g["ny"]}
cdo = unreal.get_default_object(cls)
for k, v in vals.items():
    cdo.set_editor_property(k, v)
EAL.save_asset("/Game/Timeshift/Hazards/BP_Rockfall", only_if_is_dirty=False)

for a in EAS.get_all_level_actors():
    if a.get_actor_label() == "Rockfall_Trap":
        EAS.destroy_actor(a)
a = EAS.spawn_actor_from_class(cls, unreal.Vector(50100, 450, 0), unreal.Rotator(0, 0, 0))
a.set_actor_label("Rockfall_Trap")
a.set_folder_path("Hazards/Rockfall")
for k, v in vals.items():
    a.set_editor_property(k, v)
a.set_editor_property("Heights", [float(x) for x in g["h"]])
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
hs = a.get_editor_property("Heights")
unreal.log_warning("%s Rockfall_Trap at %s heights=%d grid=%dx%d lip %s -> %s" % (TAG, a.get_actor_location(), len(hs), a.get_editor_property("GNX"),
                   a.get_editor_property("GNY"), a.get_editor_property("LipA"), a.get_editor_property("LipB")))
