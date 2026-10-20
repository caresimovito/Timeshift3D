# Editor Python, during PIE: EquipTorch twice (does it leave an orphan torch?), morph, wait a few frames, report every
# SM_Torch component's hidden-in-game flag; then unmorph and report again.
import unreal
TAG = "[TMT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
pawn.call_method("EquipTorch")
pawn.call_method("EquipTorch")


def torches():
    out = []
    for c in pawn.get_components_by_class(unreal.StaticMeshComponent):
        m = c.static_mesh
        if m and m.get_name() == "SM_Torch":
            out.append("%s hidden=%s vis=%s" % (c.get_name(), c.get_editor_property("hidden_in_game"), c.is_visible()))
    return out


unreal.log_warning("%s after 2x EquipTorch: %s" % (TAG, torches()))
pawn.call_method("AddMorphCharge")
pawn.call_method("StartMorph")
st = {"h": None, "n": 0}


def tick(dt):
    st["n"] += 1
    if st["n"] == 6:
        unreal.log_warning("%s morphed (%s): %s" % (TAG, pawn.get_editor_property("MorphName"), torches()))
        pawn.call_method("EndMorph")
    if st["n"] == 9:
        unreal.log_warning("%s unmorphed: %s" % (TAG, torches()))
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
