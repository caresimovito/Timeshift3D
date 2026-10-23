# Editor Python (user 2026-10-23: "next do the portal" -> the big key ring): the portal is now the complete Tripo key ring
# the three key pieces are cut from (SM_PortalKeyRing, 5.5 m), standing on the arena floor at x 97300 (the old ring sat
# half sunk with its centre at z -3, floor z 120). Portal_Exit (BP_Portal: the trigger + the swirl disc) moves up to the
# ring's centre and fills it; BP_Portal hides it until all key pieces are collected. Previous state -> portal_prev.json.
import json
import unreal
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
DEST = "/Game/Timeshift/Environment/Arena2/PortalKeyRing"
t = unreal.AssetImportTask()
t.set_editor_property("filename", r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/Interactables/KeyPiece/SM_PortalKeyRing.glb")
t.set_editor_property("destination_path", DEST)
t.set_editor_property("replace_existing", True)
t.set_editor_property("automated", True)
t.set_editor_property("save", True)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
mesh = [EAL.load_asset(p.split(".")[0]) for p in EAL.list_assets(DEST, True) if "/StaticMeshes/" in p][0]
mi = mesh.get_material(0)
base = [v.parameter_value for v in mi.get_editor_property("texture_parameter_values") if str(v.parameter_info.name) == "BaseColorTexture"][0]
MEL.set_material_instance_texture_parameter_value(mi, "EmissiveTexture", base)
MEL.set_material_instance_vector_parameter_value(mi, "EmissiveFactor", unreal.LinearColor(0.3 * 0.6, 0.9 * 0.6, 1.0 * 0.6, 1))
EAL.save_asset(mi.get_path_name(), only_if_is_dirty=False)
bs = mesh.get_editor_property("body_setup")
if bs:
    bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)   # walk through the hole, bump the stone
EAL.save_asset(mesh.get_path_name(), only_if_is_dirty=False)
FLOOR = 120.0
prev = {}
for a in EAS.get_all_level_actors():
    lab = a.get_actor_label()
    if lab == "Arena_PortalRing":
        c = a.static_mesh_component
        prev[lab] = {"mesh": c.static_mesh.get_path_name(), "loc": [a.get_actor_location().x, a.get_actor_location().y, a.get_actor_location().z],
                     "rot": [a.get_actor_rotation().pitch, a.get_actor_rotation().yaw, a.get_actor_rotation().roll]}
        a.modify()
        c.modify()
        c.set_static_mesh(mesh)
        c.set_editor_property("override_materials", [])
        c.set_material(0, mi)
        a.set_actor_location(unreal.Vector(97300, 0, FLOOR - 20), False, False)
        a.set_actor_rotation(unreal.Rotator(0, 0, 90), False)        # (roll, pitch, yaw): ring plane across the path
    if lab == "Portal_Exit":
        c = a.get_components_by_class(unreal.StaticMeshComponent)[0]
        prev[lab] = {"loc": [a.get_actor_location().x, a.get_actor_location().y, a.get_actor_location().z], "scale": [a.get_actor_scale3d().x, a.get_actor_scale3d().y, a.get_actor_scale3d().z],
                     "mat": c.get_material(0).get_path_name() if c.get_material(0) else None}
        a.modify()
        c.modify()
        a.set_actor_location(unreal.Vector(97300, 0, FLOOR - 20 + 275), False, False)
        a.set_actor_scale3d(unreal.Vector(3.9, 3.9, 0.05))
        c.set_material(0, EAL.load_asset("/Game/Timeshift/Environment/Meshes/Relic/M_PortalSwirl"))
        c.set_visibility(True, False)
json.dump(prev, open(r"C:/agentpy/portal_prev.json", "w"))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
for a in EAS.get_all_level_actors():
    if a.get_actor_label() in ("Arena_PortalRing", "Portal_Exit"):
        o, e = a.get_actor_bounds(False)
        unreal.log_warning("[PORTAL] %s bounds centre %s ext %s" % (a.get_actor_label(), o, e))
unreal.log_warning("[PORTAL] mesh %s tris %d" % (mesh.get_name(), mesh.get_num_triangles(0)))
