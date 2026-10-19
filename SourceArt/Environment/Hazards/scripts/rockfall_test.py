# Editor Python, during PIE: stand the hero on the path under the cliff (inside Rockfall_Trap's trigger) and log, by game
# time, the trap state, every falling rock (pos, phase, bounces) and the hero's HP / position. Freezes nearby creatures.
import unreal

TAG = "[RFT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
trap = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.load_class(None, "/Game/Timeshift/Hazards/BP_Rockfall.BP_Rockfall_C"))][0]
RC = unreal.load_class(None, "/Game/Timeshift/Hazards/BP_FallingRock.BP_FallingRock_C")
HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")
hc = pawn.get_component_by_class(HCC)
x, y = globals().get("TX", 50000), globals().get("TY", 500)
h = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x, y, 400), unreal.Vector(x, y, -500),
                                           unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [pawn], unreal.DrawDebugTrace.NONE, True).to_tuple()
pawn.set_actor_location(unreal.Vector(x, y, (h[4].z if h[0] else 10) + 100), False, True)
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
rk = {"h": None, "t0": gt(), "last": -1.0, "seen": set()}


def hp():
    for n in ("CurrentHealth", "Health"):
        try:
            return hc.get_editor_property(n)
        except Exception:
            pass


def tick(dt):
    try:
        now = gt() - rk["t0"]
        for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
            if a != pawn and a.is_actor_tick_enabled() and a.get_component_by_class(HCC) and (a.get_actor_location() - pawn.get_actor_location()).length() < 4000:
                a.set_actor_tick_enabled(False)
                for c in a.get_components_by_class(unreal.ActorComponent):
                    c.set_component_tick_enabled(False)
        if now - rk["last"] >= 0.5:
            rk["last"] = now
            rocks = unreal.GameplayStatics.get_all_actors_of_class(w, RC)
            desc = []
            for r in rocks:
                l = r.get_actor_location()
                desc.append("(%.0f,%.0f,%.0f p%d b%d s%.2f)" % (l.x, l.y, l.z, r.get_editor_property("Phase"), r.get_editor_property("Bounces"), r.get_editor_property("Scale")))
            p = pawn.get_actor_location()
            unreal.log_warning("%s t=%.1f busy=%s left=%s hp=%s hero=(%.0f,%.0f,%.0f) rocks=%d %s" % (TAG, now, trap.get_editor_property("Busy"),
                               trap.get_editor_property("RocksLeft"), hp(), p.x, p.y, p.z, len(rocks), " ".join(desc[:8])))
        if now > 9:
            unreal.log_warning("%s done" % TAG)
            unreal.unregister_slate_post_tick_callback(rk["h"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(rk["h"])


rk["h"] = unreal.register_slate_post_tick_callback(tick)
