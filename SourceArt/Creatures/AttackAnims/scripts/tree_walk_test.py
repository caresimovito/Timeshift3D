# Editor Python, during PIE: walk enemies straight at trees that have collision and log how close they get to the trunk
# centre and how high they get above the landscape. For N enemies of SPECIES: find the nearest colliding tree instance
# (instanced meshes whose name looks like a tree / trunk), aim the enemy's roam target 6 m beyond the trunk on the line
# through it, and watch for PER seconds. Pass = it never reaches the trunk centre and never rises > 100 cm off the ground.
import math
import unreal
TAG = "[TWT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
SPECIES = globals().get("SPECIES") or ["Raptor", "Triceratops", "Compy", "Stegosaurus"]
PER = globals().get("PER", 12.0)
KEYS = ("tree", "trunk", "cycad", "palm", "fir")


def land_z(x, y, top):
    z = top
    for _ in range(14):
        h = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x, y, z), unreal.Vector(x, y, z - 8000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                   False, [], unreal.DrawDebugTrace.NONE, True)
        t = h.to_tuple() if h else None
        if not t or not t[0]:
            return None
        if t[10] and "Landscape" in t[10].get_name():
            return t[4].z
        z = t[4].z - 5
    return None


trees = []
for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        if not m or not any(k in m.get_name().lower() for k in KEYS) or any(k in m.get_name() for k in ("FirTree", "IslandTree")):
            continue
        if str(c.get_collision_enabled()).find("NO_COLLISION") >= 0:
            continue
        for i in range(c.get_instance_count()):
            trees.append((c.get_instance_transform(i, True).translation, m.get_name()))
ens = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_EnemyBase_C"
       and str(a.get_editor_property("Species")) in SPECIES and not a.get_editor_property("bIsFlying")]
picked = {}
for e in ens:
    sp = str(e.get_editor_property("Species"))
    if sp in picked:
        continue
    l = e.get_actor_location()
    near = [t for t in trees if 300 < math.hypot(t[0].x - l.x, t[0].y - l.y) < 700]
    if not near:
        continue
    tp, tn = min(near, key=lambda t: math.hypot(t[0].x - l.x, t[0].y - l.y))
    dx, dy = tp.x - l.x, tp.y - l.y
    dl = math.hypot(dx, dy)
    tgt = unreal.Vector(tp.x + dx / dl * 300, tp.y + dy / dl * 300, l.z)
    picked[sp] = dict(e=e, tree=tp, tname=tn, tgt=tgt, minr=1e9, maxup=-1e9, start=l)
ORDER = list(picked)
HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")
hc = pawn.get_component_by_class(HCC)
unreal.log_warning("%s %d colliding tree instances; testing %s" % (TAG, len(trees), {k: "%s at %.0f m" % (v["tname"], math.hypot(v["tree"].x - v["start"].x, v["tree"].y - v["start"].y) / 100) for k, v in picked.items()}))
st = {"h": None, "t0": gt(), "i": -1}


def start(i):
    p = picked[ORDER[i]]
    gz = land_z(p["tgt"].x, p["tgt"].y, p["start"].z + 3000) or p["start"].z
    pawn.set_actor_location(unreal.Vector(p["tgt"].x, p["tgt"].y, gz + 120), False, True)   # the bait: 6 m behind the trunk
    st["t0"] = gt()


def tick(dt):
    try:
        try:
            hc.set_editor_property("bIsInvulnerable", True)
        except Exception:
            pass
        if st["i"] < 0:
            st["i"] = 0
            start(0)
            return
        sp = ORDER[st["i"]]
        p = picked[sp]
        e = p["e"]
        if unreal.SystemLibrary.is_valid(e):
            l = e.get_actor_location()
            p["minr"] = min(p["minr"], math.hypot(l.x - p["tree"].x, l.y - p["tree"].y))
            gz = land_z(l.x, l.y, l.z + 3000)
            if gz is not None:
                p["maxup"] = max(p["maxup"], l.z - gz)
        if gt() - st["t0"] > PER:
            l = e.get_actor_location()
            unreal.log_warning("%s %-12s (%s) closest to trunk centre %.0f cm | highest above ground %.0f cm | moved %.0f m, now %.0f m from the bait" % (
                TAG, sp, p["tname"], p["minr"], p["maxup"], math.hypot(l.x - p["start"].x, l.y - p["start"].y) / 100,
                math.hypot(l.x - p["tgt"].x, l.y - p["tgt"].y) / 100))
            st["i"] += 1
            if st["i"] >= len(ORDER):
                unreal.log_warning("%s done" % TAG)
                unreal.unregister_slate_post_tick_callback(st["h"])
                return
            start(st["i"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(st["h"])


st["h"] = unreal.register_slate_post_tick_callback(tick)
