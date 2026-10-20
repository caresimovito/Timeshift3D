# Editor Python, during PIE: after a few seconds of play, the (previously collapsed) Psittacosaurus / Archaeoceratops /
# Caudipteryx enemies should have spread-out poses; sample head / tail vs pelvis for each.
import unreal
TAG = "[FST2]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
for sp in ("Psittacosaurus", "Archaeoceratops", "Caudipteryx"):
    for e in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
        if e.get_class().get_name() == "BP_EnemyBase_C" and str(e.get_editor_property("Species")) == sp:
            b = e.get_editor_property("Body")
            pts = []
            pel = b.get_socket_location("pelvis")
            for bn in ("head", "tail_04", "leg_L_lower"):
                p = b.get_socket_location(bn)
                pts.append("%s %.0f cm from pelvis" % (bn, (p - pel).length()))
            unreal.log_warning("%s %s %s: %s" % (TAG, sp, e.get_actor_label(), ", ".join(pts)))
            break
