# Editor Python, during PIE: the morph's attack branch needs the attack KEY (the hero's tick polls it and sets bIsAttacking,
# which Python cannot write), so check the pieces it calls instead: the hero's AttackVariety component answers MoveCount for
# each morph species, and PlayMove plays every move on the morph body and returns its length.
import unreal
TAG = "[MMT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
av = pawn.get_editor_property("AttackVariety")
unreal.log_warning("%s hero AttackVariety = %s" % (TAG, av.get_name() if av else None))
seen = {}
for i in range(120):
    pawn.call_method("AddMorphCharge")
    pawn.call_method("StartMorph")
    sp = str(pawn.get_editor_property("MorphName"))
    if sp not in seen:
        mb = pawn.get_editor_property("MorphBody")
        n = av.call_method("MoveCount", (sp,))
        lens = [round(av.call_method("PlayMove", (mb, sp, k)), 2) for k in range(1, n + 1)]
        anim = mb.get_editor_property("animation_data").get_editor_property("anim_to_play")
        seen[sp] = (n, lens, anim.get_name() if anim else None)
        unreal.log_warning("%s %-15s MoveCount=%d PlayMove lengths=%s last clip on body=%s" % (TAG, sp, n, lens, seen[sp][2]))
    pawn.call_method("EndMorph")
    if len(seen) >= 10:
        break
unreal.log_warning("%s done, %d species checked" % (TAG, len(seen)))
