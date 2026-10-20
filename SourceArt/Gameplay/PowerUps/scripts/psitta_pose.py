# Editor Python, during PIE (already morphed into Psittacosaurus by psitta_test.py): skeleton of mesh vs anims, a few bone
# world positions relative to the actor (collapsed / far-away pose?), and the anim instance state.
import unreal
TAG = "[PSP]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
mb = pawn.get_editor_property("MorphBody")
sk = mb.get_editor_property("skeletal_mesh_asset")
al = pawn.get_actor_location()
names = [str(mb.get_bone_name(i)) for i in range(min(mb.get_num_bones(), 200))]
unreal.log_warning("%s mesh skeleton=%s bones=%d first=%s" % (TAG, sk.skeleton.get_name() if sk.skeleton else None, mb.get_num_bones(), names[:6]))
for n in names[:: max(1, len(names) // 6)]:
    p = mb.get_socket_location(n)
    unreal.log_warning("%s bone %s rel to actor=(%.0f,%.0f,%.0f)" % (TAG, n, p.x - al.x, p.y - al.y, p.z - al.z))
for a in ("MorphIdle", "MorphWalk", "MorphRun", "MorphAttack"):
    an = pawn.get_editor_property(a)
    unreal.log_warning("%s %s=%s skeleton=%s" % (TAG, a, an.get_name() if an else None, an.get_editor_property("skeleton").get_name() if an else None))
unreal.log_warning("%s anim mode=%s single-node anim=%s" % (TAG, mb.get_animation_mode(), mb.get_editor_property("animation_data").get_editor_property("anim_to_play") if mb.get_editor_property("animation_data") else None))
# compare with a placed enemy psittacosaurus body
for e in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
    if e.get_class().get_name() == "BP_EnemyBase_C" and str(e.get_editor_property("Species")) == "Psittacosaurus":
        b = e.get_editor_property("Body")
        el = e.get_actor_location()
        pr = b.get_socket_location(names[len(names) // 2])
        unreal.log_warning("%s enemy %s body anim mode=%s bone %s rel=(%.0f,%.0f,%.0f)" % (TAG, e.get_actor_label(), b.get_animation_mode(), names[len(names) // 2], pr.x - el.x, pr.y - el.y, pr.z - el.z))
        break
