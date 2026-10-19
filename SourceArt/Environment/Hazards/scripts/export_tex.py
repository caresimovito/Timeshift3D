# Editor Python: export a texture to TGA (for eyeballing its colour/alpha offline).
import unreal
t = unreal.AssetExportTask()
t.set_editor_property("object", unreal.EditorAssetLibrary.load_asset("/Game/Timeshift/Hazards/Textures/T_SmokeSubUV_8x8"))
t.set_editor_property("filename", r"C:/agentpy/T_SmokeSubUV_8x8.tga")
t.set_editor_property("automated", True)
t.set_editor_property("replace_identical", True)
t.set_editor_property("prompt", False)
unreal.log_warning("[TEXX] export %s" % unreal.Exporter.run_asset_export_task(t))
