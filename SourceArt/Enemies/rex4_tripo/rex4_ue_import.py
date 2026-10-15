# Unreal editor Python: import rex4 mesh onto SK_RexPrime_Skeleton, its textures, and replace the 28 boss clips.
import os
import unreal

TAG = "[R4I]"
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

# ---------------------------------------------------------------- textures
for fname, asset, kind in (("Color.jpg", "T_Rex4_BaseColor", "base"), ("Normal.png", "T_Rex4_Normal", "normal"),
                           ("rex4_tripo_roughness.JPEG", "T_Rex4_Roughness", "linear"),
                           ("rex4_tripo_metallic.JPEG", "T_Rex4_Metallic", "linear")):
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", os.path.join(TEXSRC, fname))
    t.set_editor_property("destination_path", DEST + "/Textures")
    t.set_editor_property("destination_name", asset)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("automated", True)
    t.set_editor_property("save", False)
    TOOLS.import_asset_tasks([t])
    a = EAL.load_asset("%s/Textures/%s" % (DEST, asset))
    if a is None:
        log("texture FAILED %s" % asset); continue
    if kind == "normal":
        a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    a.set_editor_property("srgb", kind == "base")
    EAL.save_asset(a.get_path_name(), only_if_is_dirty=False)
    log("texture %s ok" % asset)

# ---------------------------------------------------------------- mesh
ui = unreal.FbxImportUI()
ui.set_editor_property("import_mesh", True)
ui.set_editor_property("import_as_skeletal", True)
ui.set_editor_property("import_animations", False)
ui.set_editor_property("import_materials", False)
ui.set_editor_property("import_textures", False)
ui.set_editor_property("create_physics_asset", False)
ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
ui.set_editor_property("skeleton", skeleton)
ui.set_editor_property("automated_import_should_detect_type", False)
sd = ui.skeletal_mesh_import_data
sd.set_editor_property("import_morph_targets", False)
sd.set_editor_property("update_skeleton_reference_pose", False)
sd.set_editor_property("use_t0_as_ref_pose", False)
sd.set_editor_property("import_uniform_scale", 1.0)
sd.set_editor_property("convert_scene", True)
sd.set_editor_property("force_front_x_axis", False)
sd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)
t = unreal.AssetImportTask()
t.set_editor_property("filename", os.path.join(FBX, "SK_Rex4_mesh.fbx"))
t.set_editor_property("destination_path", DEST)
t.set_editor_property("destination_name", "SK_Rex4")
t.set_editor_property("replace_existing", True)
t.set_editor_property("automated", True)
t.set_editor_property("save", False)
t.set_editor_property("options", ui)
TOOLS.import_asset_tasks([t])
mesh = EAL.load_asset(DEST + "/SK_Rex4")
if mesh is None:
    log("FATAL mesh import failed"); raise SystemExit
b = mesh.get_bounds()
log("mesh skeleton=%s bounds extent=(%.0f, %.0f, %.0f) origin=(%.0f, %.0f, %.0f) slots=%s" % (
    mesh.skeleton.get_name(), b.box_extent.x, b.box_extent.y, b.box_extent.z, b.origin.x, b.origin.y, b.origin.z,
    [str(m.material_slot_name) for m in mesh.materials]))
EAL.save_asset(DEST + "/SK_Rex4", only_if_is_dirty=False)

# ---------------------------------------------------------------- animations -> the 28 boss clip assets
MAP = {"Idle": "Idle", "Idle_Look": "Idle", "Idle_Shake": "Idle",
       "Walk": "Walk", "Walk_Wounded": "Walk", "Turn_L": "Walk", "Turn_R": "Walk",
       "Run": "Run", "Attack_Charge": "Run",
       "Attack": "Bite", "Attack_Bite2": "Bite", "Attack_Lunge": "Bite", "Attack_HeadSwing": "Bite", "Attack_TailSwipe": "Bite",
       "Hit": "Hit", "Hit_Head": "Hit", "Hit_Body": "Hit", "Hit_Leg": "Hit", "Hit_Stagger": "Hit", "Hit_Tail": "Hit",
       "Hit_Head2": "Hit", "Flinch_Small": "Hit",
       "Roar": "Roar", "Alert": "Roar", "Taunt": "Roar", "Stomp": "Roar",
       "Death": "Death", "Death_Forward": "Death"}
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
