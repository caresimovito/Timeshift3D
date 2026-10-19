# Editor Python: import SM_TarPit and place BP_SinkZone instances (folder Swamp/Hazards, rebuilt each run):
# one tar pit over the old moss basin, three mud patches on flat swamp shore (C:/agentpy/mud_spots.json).
import json
import unreal

TAG = "[SINKS]"
EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
t = unreal.AssetImportTask()
t.set_editor_property("filename", r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/Environment/Hazards/SM_TarPit.fbx")
t.set_editor_property("destination_path", "/Game/Timeshift/Hazards/Meshes")
t.set_editor_property("destination_name", "SM_TarPit")
t.set_editor_property("replace_existing", True)
t.set_editor_property("automated", True)
t.set_editor_property("save", True)
o = unreal.FbxImportUI()
o.set_editor_property("import_mesh", True)
o.set_editor_property("import_materials", False)
o.set_editor_property("import_textures", False)
o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
o.get_editor_property("static_mesh_import_data").set_editor_property("combine_meshes", True)
t.set_editor_property("options", o)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
tar_mesh = EAL.load_asset("/Game/Timeshift/Hazards/Meshes/SM_TarPit")
tar_mesh.set_material(0, EAL.load_asset("/Game/Timeshift/Hazards/Materials/M_Tar"))
EAL.save_asset(tar_mesh.get_path_name(), only_if_is_dirty=False)

FOLDER = "Swamp/Hazards"
for a in EAS.get_all_level_actors():
    if str(a.get_folder_path()) == FOLDER:
        EAS.destroy_actor(a)
cls = unreal.load_class(None, "/Game/Timeshift/Hazards/BP_SinkZone.BP_SinkZone_C")


def ground(x, y):
    ign = []
    for _ in range(10):
        h = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(x, y, 3000), unreal.Vector(x, y, -3000),
                                                   unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ign, unreal.DrawDebugTrace.NONE, True)
        tt = h.to_tuple() if h else None
        if not tt or not tt[0] or not tt[9]:
            return 0.0
        if "Landscape" in type(tt[9]).__name__:
            return tt[4].z
        ign.append(tt[9])
    return 0.0


def zone(label, loc, tar, speed, rate, depth, dmg, box, decal=None):
    a = EAS.spawn_actor_from_class(cls, loc, unreal.Rotator(0, 0, 0))
    a.set_actor_label(label)
    a.set_folder_path(FOLDER)
    a.set_editor_property("bIsTar", tar)
    a.set_editor_property("SpeedMult", speed)
    a.set_editor_property("SinkRate", rate)
    a.set_editor_property("SinkDepth", depth)
    a.set_editor_property("SinkDamage", dmg)
    for c in a.get_components_by_class(unreal.ActorComponent):
        n = c.get_name()
        if n.startswith("Trigger"):
            c.set_editor_property("box_extent", box)
        elif n.startswith("MudDecal"):
            c.set_editor_property("visible", not tar)
            if decal:
                c.set_editor_property("decal_size", decal)
        elif n.startswith("TarSurface"):
            c.set_editor_property("visible", tar)
            if tar:
                c.set_editor_property("static_mesh", tar_mesh)
                c.set_editor_property("override_materials", [EAL.load_asset("/Game/Timeshift/Hazards/Materials/M_Tar")])
    unreal.log_warning("%s %s at %s tar=%s speed=%s rate=%s depth=%s dmg=%s" % (TAG, label, loc, tar, speed, rate, depth, dmg))
    return a


zone("Swamp_TarPit", unreal.Vector(26100, 100, -3.5), True, 0.25, 0.35, 70.0, 8.0, unreal.Vector(700, 650, 120))
for i, (x, y) in enumerate(json.load(open(r"C:/agentpy/mud_spots.json"))):
    zone("Swamp_Mud_%d" % i, unreal.Vector(x, y, ground(x, y) + 5), False, 0.45, 0.15, 45.0, 4.0,
         unreal.Vector(230, 230, 120), unreal.Vector(150, 290, 290))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
