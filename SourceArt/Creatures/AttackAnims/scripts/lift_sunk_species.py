# Editor Python: Psittacosaurus and Caudipteryx render sunk into the ground (feet 60 / 40 cm under, user screenshot
# 2026-10-21). Their Blender armature bone (SK_<Sp>1, the skeleton's top bone) carries a downward offset in the reference
# pose (z -62.8 / -94.9; Archaeoceratops, which stands fine, has 0) and every clip keeps it, so the whole body sits that
# much too low. Zero that bone's translation in EVERY clip of the two species (base clips + authored moves); all other
# tracks are rewritten unchanged. DRY=True only reports.
import json
import unreal
TAG = "[LIFT]"
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
SKEL = json.load(open(r"C:/agentpy/skeletons.json"))
DRY = globals().get("DRY", False)
for sp in ("Psittacosaurus", "Caudipteryx"):
    bones = [b for b, _ in SKEL[sp]]
    top = bones[0]
    clips = [p for p in EAL.list_assets("/Game/Timeshift/Enemies/%s" % sp, False) if ("_Anim_SK_%s_" % sp) in p]
    for p in clips:
        seq = EAL.load_asset(p.split(".")[0])
        if not isinstance(seq, unreal.AnimSequence):
            continue
        nkeys = AL.get_num_frames(seq) + 1
        before = AL.get_bone_pose_for_frame(seq, top, 0, False).translation
        if abs(before.z) < 0.5 and abs(before.x) < 0.5 and abs(before.y) < 0.5:
            unreal.log_warning("%s %s already level" % (TAG, p.split("/")[-1]))
            continue
        tracks = {}
        for b in bones:
            ps, rs, ss = [], [], []
            for f in range(nkeys):
                tr = AL.get_bone_pose_for_frame(seq, b, f, False)
                pp, q, s = tr.translation, tr.rotation, tr.scale3d
                if b == top:
                    pp = unreal.Vector(0.0, 0.0, 0.0)
                ps.append(unreal.Vector(pp.x, pp.y, pp.z))
                rs.append(unreal.Quat(q.x, q.y, q.z, q.w))
                ss.append(unreal.Vector(s.x, s.y, s.z))
            tracks[b] = (ps, rs, ss)
        if not DRY:
            ctrl = seq.get_editor_property("controller")
            ctrl.open_bracket(unreal.Text("lift armature offset"), True)
            for b in bones:
                ctrl.set_bone_track_keys(unreal.Name(b), tracks[b][0], tracks[b][1], tracks[b][2], True)
            ctrl.close_bracket(True)
            EAL.save_asset(seq.get_path_name(), only_if_is_dirty=False)
        after = AL.get_bone_pose_for_frame(seq, top, 0, False).translation
        unreal.log_warning("%s %s keys=%d top z %.1f -> %.1f%s" % (TAG, p.split("/")[-1].split(".")[0], nkeys, before.z, after.z, " (dry)" if DRY else ""))
unreal.log_warning("%s done" % TAG)
