# Editor Python: the KEY PIECES are the three arcs of the Tripo key ring (ring_split.py) - arc 1 is BP_Pickup_KeyArtifact's own
# mesh (set by pickup_apply.py first), arcs 2 and 3 go on the second and third placed pieces. All three hover 60 cm above
# the ground (KeyPiece_02 hung 9 m up in the air) and turn slowly (RotatingMovement added to the BP once).
import unreal
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
W = unreal.EditorLevelLibrary.get_editor_world()
S = "C:/repos/Unreal Projects/Timeshift3D/SourceArt/Interactables/KeyPiece/"
TINT, GLOW = (0.3, 0.9, 1.0), 0.7
meshes = {}
for k in (2, 3):
    dest = "/Game/Timeshift/Interactables/KeyPiece/P%d" % k
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", S + "SM_KeyPiece_%d.glb" % k)
    t.set_editor_property("destination_path", dest)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("automated", True)
    t.set_editor_property("save", True)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    m = [EAL.load_asset(p.split(".")[0]) for p in EAL.list_assets(dest, True) if "/StaticMeshes/" in p][0]
    mi = m.get_material(0)
    base = [v.parameter_value for v in mi.get_editor_property("texture_parameter_values") if str(v.parameter_info.name) == "BaseColorTexture"][0]
    MEL.set_material_instance_texture_parameter_value(mi, "EmissiveTexture", base)
    MEL.set_material_instance_vector_parameter_value(mi, "EmissiveFactor", unreal.LinearColor(TINT[0] * GLOW, TINT[1] * GLOW, TINT[2] * GLOW, 1))
    EAL.save_asset(mi.get_path_name(), only_if_is_dirty=False)
    if unreal.EditorStaticMeshLibrary.get_simple_collision_count(m) == 0:
        unreal.EditorStaticMeshLibrary.add_simple_collisions(m, unreal.ScriptCollisionShapeType.BOX)
    EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)
    meshes[k] = m
bp = EAL.load_asset("/Game/Timeshift/Interactables/BP_Pickup_KeyArtifact")
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
BFL = unreal.SubobjectDataBlueprintFunctionLibrary
handles = sds.k2_gather_subobject_data_for_blueprint(bp)
objs = [BFL.get_object(sds.k2_find_subobject_data_from_handle(h)) for h in handles]
rots = [o for o in objs if isinstance(o, unreal.RotatingMovementComponent)]
if not rots:
    p = unreal.AddNewSubobjectParams()
    p.set_editor_property("parent_handle", handles[0])
    p.set_editor_property("new_class", unreal.RotatingMovementComponent)
    p.set_editor_property("blueprint_context", bp)
    h, why = sds.add_new_subobject(p)
    rm = BFL.get_object(sds.k2_find_subobject_data_from_handle(h))
else:
    rm = rots[0]
rm.set_editor_property("rotation_rate", unreal.Rotator(0, 0, 40))     # (roll, pitch, yaw): 40 deg/s about Z
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset("/Game/Timeshift/Interactables/BP_Pickup_KeyArtifact", only_if_is_dirty=False)
keys = sorted([a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
               if a.get_class().get_name() == "BP_Pickup_KeyArtifact_C"], key=lambda a: a.get_actor_location().x)
out = []
for i, a in enumerate(keys):
    c = a.get_components_by_class(unreal.StaticMeshComponent)[0]
    a.modify()
    c.modify()
    if i + 1 in meshes:
        c.set_static_mesh(meshes[i + 1])
        c.set_material(0, meshes[i + 1].get_material(0))
    l = a.get_actor_location()
    hit = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(l.x, l.y, l.z + 50), unreal.Vector(l.x, l.y, l.z - 5000),
                                                 unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [a], unreal.DrawDebugTrace.NONE, True)
    hit = hit.to_tuple() if hit else None
    gz = hit[4].z if hit and hit[0] else l.z
    a.set_actor_location(unreal.Vector(l.x, l.y, gz + 60), False, False)
    out.append((a.get_actor_label(), c.static_mesh.get_name(), round(l.z), round(gz + 60)))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log_warning("[KEYAPPLY] rotating %s, pieces %s" % (rm.get_name(), out))
