# Editor Python: after the pickup model swap (2026-10-23) the new meshes have their origin at the bottom while the old ones
# were centred differently - settle every pickup (not the hovering key pieces) so its mesh bottom rests 2 cm into the first
# surface below it (ground, rock or nest). Moves under 3 cm or over 3 m are left alone and reported.
import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.EditorLevelLibrary.get_editor_world()
acts = EAS.get_all_level_actors()
picks = [a for a in acts if a.get_class().get_name().startswith("BP_Pickup_") and a.get_class().get_name() != "BP_Pickup_KeyArtifact_C"]
moved, skipped = 0, []
for a in picks:
    o, e = a.get_actor_bounds(False)
    bottom = o.z - e.z
    t = unreal.SystemLibrary.line_trace_single(W, unreal.Vector(o.x, o.y, o.z + e.z + 20), unreal.Vector(o.x, o.y, bottom - 3000),
                                               unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, picks, unreal.DrawDebugTrace.NONE, True)
    t = t.to_tuple() if t else None
    if not t or not t[0]:
        skipped.append((a.get_actor_label(), "no surface"))
        continue
    d = (t[4].z - 2) - bottom
    if abs(d) < 3:
        continue
    if abs(d) > 300:
        skipped.append((a.get_actor_label(), round(d)))
        continue
    a.modify()
    l = a.get_actor_location()
    a.set_actor_location(unreal.Vector(l.x, l.y, l.z + d), False, False)
    moved += 1
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log_warning("[GROUND] %d pickups settled, %d checked, left alone: %s" % (moved, len(picks), skipped))
