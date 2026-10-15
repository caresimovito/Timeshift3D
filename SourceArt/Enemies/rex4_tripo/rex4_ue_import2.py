# Unreal editor Python: import rex4 mesh onto SK_RexPrime_Skeleton, its textures, and replace the 28 boss clips.
import os
import unreal

TAG = "[R4I2]"
SRC = r"C:\repos\Unreal Projects\Timeshift3D\SourceArt\Enemies\rex4_tripo"
FBX = os.path.join(SRC, "fbx")
TEXSRC = os.path.join(SRC, "tripo_convert_adf150cf-38b0-4ae9-bf7e-3c49e711b16c.fbm")
DEST = "/Game/Timeshift/Enemies/Rex4"
OLD = "/Game/Timeshift/Enemies/RexPrime"
EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()


def log(m):
    unreal.log_warning("%s %s" % (TAG, m))


unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
skeleton = EAL.load_asset(OLD + "/SK_RexPrime_Skeleton")

# ---------------------------------------------------------------- animations -> the 28 boss clip assets
MAP = {"Idle": "Idle", "Idle_Look": "IdleLook", "Idle_Shake": "IdleShake",
       "Walk": "Walk", "Walk_Wounded": "Walk", "Turn_L": "Walk", "Turn_R": "Walk",
       "Alert": "Alert", "Taunt": "Taunt", "Attack_HeadSwing": "HeadSwing", "Hit_Head": "HitHead", "Hit_Head2": "HitHead"}
tasks = []
for old, new in MAP.items():
    ui = unreal.FbxImportUI()
    ui.set_editor_property("import_mesh", False)
    ui.set_editor_property("import_materials", False)
    ui.set_editor_property("import_textures", False)
    ui.set_editor_property("import_as_skeletal", True)
    ui.set_editor_property("import_animations", True)
    ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
    ui.set_editor_property("skeleton", skeleton)
    ui.set_editor_property("automated_import_should_detect_type", False)
    aid = ui.anim_sequence_import_data
    aid.set_editor_property("import_uniform_scale", 1.0)
    aid.set_editor_property("animation_length", unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    aid.set_editor_property("remove_redundant_keys", False)
    aid.set_editor_property("import_bone_tracks", True)
    aid.set_editor_property("convert_scene", True)
    aid.set_editor_property("force_front_x_axis", False)
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", os.path.join(FBX, "Rex4_%s.fbx" % new))
    t.set_editor_property("destination_path", OLD)
    t.set_editor_property("destination_name", "SK_RexPrime_Anim_SK_RexPrime_%s" % old)
    t.set_editor_property("automated", True)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("replace_existing_settings", True)
    t.set_editor_property("save", False)
    t.set_editor_property("options", ui)
    tasks.append((old, new, t))
TOOLS.import_asset_tasks([t for _, _, t in tasks])
ok = 0
for old, new, t in tasks:
    p = "%s/SK_RexPrime_Anim_SK_RexPrime_%s" % (OLD, old)
    a = EAL.load_asset(p)
    if isinstance(a, unreal.AnimSequence):
        ok += 1
        EAL.save_asset(p, only_if_is_dirty=False)
        log("anim %-16s <- %-5s %.2fs frames %d" % (old, new, a.get_play_length(), a.get_editor_property("number_of_sampled_frames") if hasattr(a, "number_of_sampled_frames") else -1))
    else:
        log("anim %-16s FAILED" % old)
log("DONE anims ok %d / %d" % (ok, len(tasks)))
