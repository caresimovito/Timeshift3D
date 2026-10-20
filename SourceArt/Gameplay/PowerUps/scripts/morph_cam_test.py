# Editor Python, during PIE: camera / body relative locations around a morph, plus the morph camera vars.
import unreal
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
cam = pawn.get_editor_property("FollowCamera")
f = lambda v: "(%.0f,%.0f,%.0f)" % (v.x, v.y, v.z)
c0 = cam.get_editor_property("relative_location")
pawn.call_method("AddMorphCharge")
pawn.call_method("StartMorph")
mb = pawn.get_editor_property("MorphBody")
unreal.log_warning("[MCT] %s back=%s up=%s saved=%s cam %s -> %s (world %s, boom-end?) body rel=%s cam parent=%s" % (
    pawn.get_editor_property("MorphName"), pawn.get_editor_property("MorphCamBack"), pawn.get_editor_property("MorphCamUp"),
    f(pawn.get_editor_property("SavedCamLoc")), f(c0), f(cam.get_editor_property("relative_location")), f(cam.get_world_location()),
    f(mb.get_editor_property("relative_location")), cam.get_attach_parent().get_name() if cam.get_attach_parent() else None))
pawn.call_method("EndMorph")
