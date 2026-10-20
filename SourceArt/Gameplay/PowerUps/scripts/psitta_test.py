# Editor Python, during PIE: give the torch, morph until we get a Psittacosaurus, then inspect MorphBody and every
# component that is NOT shrunk (world scale > 0.01) besides the capsule / camera / morph body.
import unreal
TAG = "[PSI]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
try:
    pawn.call_method("DebugGiveAllWeapons")
except Exception as e:
    unreal.log_warning("%s give: %s" % (TAG, e))
for i in range(40):
    pawn.call_method("AddMorphCharge")
    pawn.call_method("StartMorph")
    if str(pawn.get_editor_property("MorphName")) == "Psittacosaurus":
        break
    pawn.call_method("EndMorph")
mb = pawn.get_editor_property("MorphBody")
sk = mb.get_editor_property("skeletal_mesh_asset")
o, e = pawn.get_actor_bounds(False)
unreal.log_warning("%s morph=%s mesh=%s vis=%s hidden=%s rel=%s scale=%s world=%s bounds=%s/%s comp_bounds=%s mats=%s" % (TAG, pawn.get_editor_property("MorphName"), sk.get_name() if sk else None,
                   mb.is_visible(), mb.get_editor_property("hidden_in_game"), mb.get_editor_property("relative_location"), mb.get_world_scale(),
                   mb.get_world_location(), o, e, mb.bounds.box_extent if hasattr(mb, "bounds") else None, [m.get_name() if m else None for m in mb.get_materials()]))
for c in pawn.get_components_by_class(unreal.PrimitiveComponent):
    s = c.get_world_scale()
    if s.x > 0.01 and c.is_visible() and c.get_name() not in ("CollisionCylinder",) and c != mb:
        p = c.get_attach_parent()
        unreal.log_warning("%s NOT SHRUNK %s (%s) parent=%s socket=%s abs_scale=%s" % (TAG, c.get_name(), c.get_class().get_name(), p.get_name() if p else None,
                           c.get_attach_socket_name(), c.get_editor_property("absolute_scale")))
