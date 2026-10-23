# Editor Python, during PIE: do the moves' hits land? Stand the player beside SPS[0] (then SPS[1]...), provoke it (1 damage, so
# herbivores fight back), and log every hit the AttackVariety timeline fires: move, hit no., player health lost that tick and
# the launch velocity. Heals the player when low. Then PART B: morph into a Triceratops beside a Raptor and stomp - log the
# enemies' health and how far they are shoved.
import unreal
TAG = "[MFX]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")
AVC = unreal.load_class(None, "/Game/Timeshift/Enemies/BP_AttackVariety.BP_AttackVariety_C")
hc = pawn.get_component_by_class(HCC)
SPS = globals().get("SPS") or ["Raptor", "Triceratops"]
PER = globals().get("PER", 25.0)
ENS = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_EnemyBase_C"]
st = {"h": None, "i": -1, "t0": 0.0, "prev": {}, "hp": 0.0, "hits": [], "phase": "A"}


def health():
    return hc.get_editor_property("CurrentHealth") + hc.get_editor_property("Armour")


def go_next():
    st["i"] += 1
    if st["i"] >= len(SPS):
        return False
    sp = SPS[st["i"]]
    cands = [a for a in ENS if str(a.get_editor_property("Species")) == sp]
    if not cands:
        unreal.log_warning("%s no %s in the level" % (TAG, sp))
        return go_next()
    e = cands[0]
    l, f = e.get_actor_location(), e.get_actor_forward_vector()
    pawn.set_actor_location(unreal.Vector(l.x + f.x * 300, l.y + f.y * 300, l.z + 150), False, True)
    e.get_component_by_class(HCC).call_method("ApplyDamage", (1.0,))           # provoke (herbivores only fight back)
    st["t0"], st["hp"] = gt(), health()
    unreal.log_warning("%s --- beside %s %s" % (TAG, sp, e.get_actor_label()))
    return True


def tick(dt):
    try:
        now = gt()
        if st["phase"] == "A":
            if st["i"] < 0 or now - st["t0"] > PER:
                if not go_next():
                    st["phase"], st["t0"] = "B0", now
                return
            hp = health()
            for a in ENS:
                if (a.get_actor_location() - pawn.get_actor_location()).length() > 2500:
                    continue
                c = a.get_component_by_class(AVC)
                if not c:
                    continue
                k = a.get_actor_label()
                # the timeline clears CurMove in the same tick as its last hit, so remember the name from earlier ticks
                mv, hd = str(c.get_editor_property("CurMove")), c.get_editor_property("HitsDone")
                pname, ph = st["prev"].get(k, ("", 0))
                if mv and (mv != pname or hd < ph):
                    unreal.log_warning("%s %s starts %s" % (TAG, a.get_editor_property("Species"), mv))
                    pname, ph = mv, 0
                if hd > ph:
                    v = pawn.get_velocity()
                    d = (a.get_actor_location() - pawn.get_actor_location())
                    unreal.log_warning("%s   %s %s hit %d: player %.0f cm away, lost %.1f hp, velocity (%.0f, %.0f, %.0f)" % (
                        TAG, a.get_editor_property("Species"), mv or pname, hd, (d.x ** 2 + d.y ** 2) ** 0.5, st["hp"] - hp, v.x, v.y, v.z))
                    st["hits"].append((mv or pname, st["hp"] - hp))
                    st["watch"] = (mv or pname, now, 0.0, 0.0)
                st["prev"][k] = (mv or pname, hd)
            # a launch shows on the NEXT frames (LaunchCharacter is applied by the movement component's own tick)
            if st.get("watch"):
                nm, t1, pk, pz = st["watch"]
                v = pawn.get_velocity()
                pk, pz = max(pk, (v.x ** 2 + v.y ** 2) ** 0.5), max(pz, v.z)
                st["watch"] = (nm, t1, pk, pz)
                if now - t1 > 0.5:
                    unreal.log_warning("%s     after %s: peak speed %.0f sideways, %.0f up" % (TAG, nm, pk, pz))
                    st["watch"] = None
            st["hp"] = hp
            if hc.get_editor_property("CurrentHealth") < 50:
                hc.call_method("Heal", (100.0,))
                st["hp"] = health()
            return
        if st["phase"] == "B0":
            unreal.log_warning("%s part A: %d hits logged" % (TAG, len(st["hits"])))
            for i in range(120):
                pawn.call_method("AddMorphCharge")
                pawn.call_method("StartMorph")
                if str(pawn.get_editor_property("MorphName")) == "Triceratops":
                    break
                pawn.call_method("EndMorph")
            rap = [a for a in ENS if str(a.get_editor_property("Species")) == "Raptor"][0]
            l = rap.get_actor_location()
            pawn.set_actor_location(unreal.Vector(l.x - 250, l.y, l.z + 250), False, True)
            near = [a for a in ENS if (a.get_actor_location() - l).length() < 600]
            st["b"] = [(a, a.get_component_by_class(HCC).get_editor_property("CurrentHealth"), a.get_actor_location()) for a in near]
            av = pawn.get_editor_property("AttackVariety")
            ln = av.call_method("PlayMove", (pawn.get_editor_property("MorphBody"), "Triceratops", 3))   # 3 = Stomp
            unreal.log_warning("%s morph Triceratops (MorphDmg %.0f, MorphRange %.0f) stomps (len %.2f) beside %d enemies; CurMove=%s" % (
                TAG, pawn.get_editor_property("MorphDmg"), pawn.get_editor_property("MorphRange"), ln, len(near), av.get_editor_property("CurMove")))
            st["phase"], st["t0"], st["minh"] = "B", now, {}
            return
        if st["phase"] == "B":
            for a, h0, p0 in st["b"]:
                h = a.get_component_by_class(HCC).get_editor_property("CurrentHealth")
                st["minh"][a.get_actor_label()] = min(st["minh"].get(a.get_actor_label(), h), h)
        if st["phase"] == "B" and now - st["t0"] > 1.6:
            for a, h0, p0 in st["b"]:
                h1 = a.get_component_by_class(HCC).get_editor_property("CurrentHealth")
                p1 = a.get_actor_location()
                unreal.log_warning("%s   %s %s: health %.0f -> lowest %.0f -> %.0f, moved %.0f cm, %.0f cm from me" % (
                    TAG, a.get_editor_property("Species"), a.get_actor_label(), h0, st["minh"].get(a.get_actor_label(), h1), h1,
                    (p1 - p0).length(), (p1 - pawn.get_actor_location()).length()))
            pawn.call_method("EndMorph")
            unreal.log_warning("%s done" % TAG)
            unreal.unregister_slate_post_tick_callback(st["h"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
