# Editor Python, during PIE: put the hero in Swamp_Mud_0, stand still 6 s, then walk 2 s; then the same in the tar pit.
# Logs Sink, max walk speed, mesh relative Z and health. Also drops the nearest dinosaur into the tar and checks Trapped.
import unreal

TAG = "[SINKT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
cm = pawn.get_editor_property("CharacterMovement")
zones = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.load_class(None, "/Game/Timeshift/Hazards/BP_SinkZone.BP_SinkZone_C"))}
unreal.log_warning("%s zones in PIE: %s" % (TAG, sorted(zones)))
hc = [c for c in pawn.get_components_by_class(unreal.ActorComponent) if "Health" in c.get_class().get_name()]


def health():
    for n in ("CurrentHealth", "Health"):
        try:
            return hc[0].get_editor_property(n)
        except Exception:
            pass
    return None


def hpof(c):
    for n in ("CurrentHealth", "Health"):
        try:
            return c.get_editor_property(n)
        except Exception:
            pass
    return None


def put(label):
    z = zones[label]
    l = z.get_actor_location()
    h = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(l.x, l.y, 2000), unreal.Vector(l.x, l.y, -2000),
                                               unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [pawn], unreal.DrawDebugTrace.NONE, True)
    t = h.to_tuple()
    pawn.set_actor_location(unreal.Vector(l.x, l.y, (t[4].z if t[0] else l.z) + 95), False, True)


def report(what):
    unreal.log_warning("%s %s pos=(%.0f,%.0f,%.0f) t=%.1f sink=%.2f maxWalk=%.0f meshZ=%.1f hp=%s speedMult=%.2f" % (
        TAG, what, pawn.get_actor_location().x, pawn.get_actor_location().y, pawn.get_actor_location().z, sk["t"], pawn.get_editor_property("Sink"), cm.get_editor_property("max_walk_speed"),
        pawn.get_editor_property("Mesh").get_editor_property("relative_location").z, health(),
        pawn.get_editor_property("HazardSpeedMult")))
    d = sk.get("dino")
    tr = zones["Swamp_TarPit"].get_editor_property("Trapped")
    if d:
        unreal.log_warning("%s   dino valid=%s at %s tick=%s trapped=%s hp=%s" % (TAG, unreal.SystemLibrary.is_valid(d),
                           d.get_actor_location() if unreal.SystemLibrary.is_valid(d) else None,
                           d.is_actor_tick_enabled() if unreal.SystemLibrary.is_valid(d) else None, tr.get_actor_label() if tr else None,
                           hpof(d.get_component_by_class(HCC)) if unreal.SystemLibrary.is_valid(d) else None))
    unreal.log_warning("%s   gt=%.2f overlaps=%s" % (TAG, unreal.GameplayStatics.get_time_seconds(w),
                       sorted(set(a.get_actor_label() for a in pawn.get_overlapping_actors(None)))))


plan = [("Swamp_TarPit", 2.0, 1.5)]
sk = {"t": 0.0, "h": None, "phase": 0, "n": 0, "last": 0.0}
put(plan[0][0])

HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")


def creatures():
    return [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)
            if a != pawn and a.get_component_by_class(HCC)]


def freeze_near(c, r, keep=None):
    # stop creatures near the hero biting him, so the HP readout only reflects the hazard
    for a in creatures():
        if a != keep and a.is_actor_tick_enabled() and (a.get_actor_location() - c).length() < r:
            a.set_actor_tick_enabled(False)
            for comp in a.get_components_by_class(unreal.ActorComponent):
                comp.set_component_tick_enabled(False)
            unreal.log_warning("%s froze %s" % (TAG, a.get_actor_label()))


def grab_dino():
    tar = zones["Swamp_TarPit"].get_actor_location()
    others = creatures()
    unreal.log_warning("%s creatures: %s" % (TAG, [(a.get_actor_label(), int((a.get_actor_location() - tar).length())) for a in others][:8]))
    if others:
        live = [a for a in others if a.is_actor_tick_enabled()] or others
        dino = min(live, key=lambda a: (a.get_actor_location() - tar).length())
        dino.set_actor_location(unreal.Vector(tar.x + 450, tar.y + 350, tar.z + 150), False, True)
        sk["dino"] = dino
        unreal.log_warning("%s dropped %s into the tar" % (TAG, dino.get_actor_label()))


def tick(dt):
    try:
        sk["t"] += dt
        label, still, walk = plan[sk["phase"]]
        if sk["phase"] == 0 and "dino" not in sk and sk["t"] > 0.2:
            grab_dino()
        freeze_near(pawn.get_actor_location(), 3000, sk.get("dino"))
        if sk["t"] > still:
            pawn.add_movement_input(pawn.get_actor_forward_vector(), 1.0, True)
        if sk["t"] - sk["last"] >= 0.75:
            sk["last"] = sk["t"]
            report(label + (" STILL" if sk["t"] <= still else " WALK"))
        if sk["t"] > still + walk:
            report(label + " END")
            sk["phase"] += 1
            sk["t"], sk["last"] = 0.0, 0.0
            if sk["phase"] >= len(plan):
                d = sk.get("dino")
                if d:
                    tz = zones["Swamp_TarPit"]
                    tr = tz.get_editor_property("Trapped")
                    unreal.log_warning("%s tar Trapped=%s dino at %s vel=%.0f anim_rate=%s" % (TAG, tr.get_actor_label() if tr else None,
                                       d.get_actor_location(), d.get_velocity().length(),
                                       [c.get_editor_property("global_anim_rate_scale") for c in d.get_components_by_class(unreal.SkeletalMeshComponent)]))
                unreal.unregister_slate_post_tick_callback(sk["h"])
                return
            put(plan[sk["phase"]][0])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(sk["h"])


sk["h"] = unreal.register_slate_post_tick_callback(tick)
