# Editor Python, during PIE: which dinosaurs attack? Stand the (invulnerable) player 2.5 m from one enemy of each species
# for PER seconds and count its attacks (AnimState rising to 2); log bCanAttack / provoked / ranges when it never attacks,
# so a stuck cooldown shows up. Herbivores are expected to stay passive unless provoked.
import unreal
TAG = "[WHO]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")
hc = pawn.get_component_by_class(HCC)
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
PER = globals().get("PER", 15.0)
ENS = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_EnemyBase_C"]
FLY = ("Pteranodon", "Tupandactylus", "Dimorphodon", "Pterosaur")
by = {}
for a in ENS:
    sp = str(a.get_editor_property("Species"))
    if sp not in FLY and a.get_actor_location().z < 400 and not a.get_editor_property("bDying"):
        if globals().get("EACH") and sp in EACH:
            by[sp + "#" + a.get_actor_label()] = a                       # every individual of these species
        elif not globals().get("EACH"):
            by.setdefault(sp, a)
ORDER = [s for s in sorted(by) if (not globals().get("SKIP") or s not in SKIP) and (not globals().get("ONLY_SP") or s.split("#")[0] in ONLY_SP)]
st = {"h": None, "i": -1, "t0": 0.0, "n": 0, "last": 0, "minDist": 1e9}


def prop(a, n):
    try:
        return a.get_editor_property(n)
    except Exception:
        return "?"


def go():
    st["i"] += 1
    if st["i"] >= len(ORDER):
        return False
    e = by[ORDER[st["i"]]]
    l, f = e.get_actor_location(), e.get_actor_forward_vector()
    pawn.set_actor_location(unreal.Vector(l.x + f.x * 250, l.y + f.y * 250, l.z + 120), False, True)
    if globals().get("PROVOKE"):
        e.get_component_by_class(HCC).call_method("ApplyDamage", (1.0,))       # one light hit - timid species should turn
    st.update(t0=gt(), n=0, last=prop(e, "AnimState"), minDist=1e9)
    return True


def tick(dt):
    try:
        try:
            hc.set_editor_property("bIsInvulnerable", True)
        except Exception:
            pass
        if hc.get_editor_property("CurrentHealth") < 60:
            hc.call_method("Heal", (100.0,))
        if st["i"] < 0:
            go()
            return
        e = by[ORDER[st["i"]]]
        if not unreal.SystemLibrary.is_valid(e):
            unreal.log_warning("%s %-15s destroyed during the test (killed?) - skipped" % (TAG, ORDER[st["i"]]))
            if not go():
                unreal.log_warning("%s done" % TAG)
                unreal.unregister_slate_post_tick_callback(st["h"])
            return
        s = prop(e, "AnimState")
        if s == 2 and st["last"] != 2:
            st["n"] += 1
        st["last"] = s
        st["minDist"] = min(st["minDist"], (e.get_actor_location() - pawn.get_actor_location()).length())
        if gt() - st["t0"] > PER:
            unreal.log_warning("%s %-15s attacks=%d in %.0fs | closest %.0f cm | AttackRange=%s Detection=%s bCanAttack=%s provoked=%s dead=%s state=%s" % (
                TAG, ORDER[st["i"]], st["n"], PER, st["minDist"], prop(e, "AttackRange"), prop(e, "DetectionRange"),
                prop(e, "bCanAttack"), prop(e, "bHasBeenProvoked"), prop(e, "bDying"), s))
            if not go():
                unreal.log_warning("%s done" % TAG)
                unreal.unregister_slate_post_tick_callback(st["h"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(st["h"])


unreal.log_warning("%s testing %s" % (TAG, ORDER))
st["h"] = unreal.register_slate_post_tick_callback(tick)
