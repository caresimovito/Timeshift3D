# Editor Python, during PIE: stand the hero on Swamp_Geyser_0 and log (by game time) the vent phase, steam/warn state,
# hero HP, height and vertical speed through a full idle->warning->burst cycle. Freezes nearby creatures.
import unreal

TAG = "[GEYT]"
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
gcls = unreal.load_class(None, "/Game/Timeshift/Hazards/BP_GeyserVent.BP_GeyserVent_C")
g = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, gcls) if a.get_actor_label() == "Swamp_Geyser_0"][0]
HCC = unreal.load_class(None, "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C")
hc = pawn.get_component_by_class(HCC)
l = g.get_actor_location()
h = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(l.x, l.y, 2000), unreal.Vector(l.x, l.y, -2000),
                                           unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [pawn], unreal.DrawDebugTrace.NONE, True)
t = h.to_tuple()
pawn.set_actor_location(unreal.Vector(l.x + 30, l.y, (t[4].z if t[0] else l.z) + 95), False, True)
comps = {c.get_name(): c for c in g.get_components_by_class(unreal.NiagaraComponent)}
gt = lambda: unreal.GameplayStatics.get_time_seconds(w)
gk = {"h": None, "t0": gt(), "last": -1.0, "launched": 0}


def hp():
    for n in ("CurrentHealth", "Health"):
        try:
            return hc.get_editor_property(n)
        except Exception:
            pass


def tick(dt):
    try:
        now = gt() - gk["t0"]
        for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
            if a != pawn and a.is_actor_tick_enabled() and a.get_component_by_class(HCC) and (a.get_actor_location() - l).length() < 3000:
                a.set_actor_tick_enabled(False)
                for c in a.get_components_by_class(unreal.ActorComponent):
                    c.set_component_tick_enabled(False)
        if now > 12 and g.get_editor_property("Phase") == 1 and not gk.get("back"):
            gk["back"] = True   # step back onto the vent before the next burst
            pawn.set_actor_location(unreal.Vector(l.x - 20, l.y + 10, pawn.get_actor_location().z), False, True)
        v = pawn.get_velocity()
        if v.z > 500:
            gk["launched"] += 1
        if now - gk["last"] >= 0.5:
            gk["last"] = now
            unreal.log_warning("%s t=%.1f phase=%s warn=%s steam=%s hp=%s x=%.0f z=%.0f vz=%.0f" % (TAG, now, g.get_editor_property("Phase"),
                               comps["Warn"].is_active(), comps["Steam"].is_active(), hp(), pawn.get_actor_location().x - l.x, pawn.get_actor_location().z, v.z))
        if now > 24:
            unreal.log_warning("%s done, frames launched=%d" % (TAG, gk["launched"]))
            unreal.unregister_slate_post_tick_callback(gk["h"])
    except Exception as ex:
        unreal.log_warning("%s error %s" % (TAG, ex))
        unreal.unregister_slate_post_tick_callback(gk["h"])


gk["h"] = unreal.register_slate_post_tick_callback(tick)
