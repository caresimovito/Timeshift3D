# Editor Python, during PIE: are the ENEMY Psittacosauruses collapsed too? bones vs actor for each, and for comparison a Raptor.
import unreal
TAG = "[PSE]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
for sp in ("Psittacosaurus", "Raptor", "Archaeoceratops", "Kulindadromeus", "Caudipteryx", "Compy"):
    for e in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
        if e.get_class().get_name() == "BP_EnemyBase_C" and str(e.get_editor_property("Species")) == sp:
            b = e.get_editor_property("Body")
            el = e.get_actor_location()
            pts = []
            for bn in ("pelvis", "head", "tail_04", "leg_L_lower"):
                if b.get_bone_index(bn) >= 0:
                    p = b.get_socket_location(bn)
                    pts.append("%s(%.0f,%.0f,%.0f)" % (bn, p.x - el.x, p.y - el.y, p.z - el.z))
            unreal.log_warning("%s %s %s anim=%s | %s" % (TAG, sp, e.get_actor_label(), b.get_animation_mode(), " ".join(pts)))
            break
