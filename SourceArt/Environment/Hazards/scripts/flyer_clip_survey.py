# Editor Python: every anim clip of the four flyer species - frames, length and how far the bones turn (frozen pose vs real
# wing beat), plus how many of each flyer are in the level. Drives the flap/glide cycle in BP_AttackVariety (2026-10-22).
import math
import unreal
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for sp in ("Pteranodon", "Tupandactylus", "Dimorphodon", "Pterosaur"):
    for p in sorted(EAL.list_assets("/Game/Timeshift/Enemies/" + sp, False)):
        a = EAL.load_asset(p.split(".")[0])
        if not isinstance(a, unreal.AnimSequence):
            continue
        names = [str(n) for n in AL.get_animation_track_names(a)]
        nf = AL.get_num_frames(a)
        worst, wb = 0.0, ""
        for b in names:
            q0 = AL.get_bone_pose_for_frame(a, b, 0, False).rotation
            for f in range(0, nf + 1, max(1, nf // 10)):
                q = AL.get_bone_pose_for_frame(a, b, f, False).rotation
                d = math.degrees(2 * math.acos(min(1.0, abs(q0.x * q.x + q0.y * q.y + q0.z * q.z + q0.w * q.w))))
                if d > worst:
                    worst, wb = d, b
        unreal.log_warning("[FLYC] %-14s %-52s frames %3d len %.2fs | max turn %3.0f deg (%s)" % (
            sp, p.split("/")[-1].split(".")[0], nf, a.get_play_length(), worst, wb))
cnt = {}
for a in EAS.get_all_level_actors():
    if a.get_class().get_name().startswith("BP_Enemy"):
        try:
            s = str(a.get_editor_property("Species"))
        except Exception:
            continue
        if s in ("Pteranodon", "Tupandactylus", "Dimorphodon", "Pterosaur"):
            cnt[s] = cnt.get(s, 0) + 1
unreal.log_warning("[FLYC] in level: %s" % cnt)
unreal.log_warning("[FLYC] done")
