"""Author a strong hit-flinch per species from the Idle pose.

The existing Hit clips barely move (a Compy's head travels 17.9cm, less than its
own idle), so hits read as nothing. This builds a real recoil: the neck chain and
upper spine snap back, peak fast, then settle.

Bone axes are not world aligned and differ per rig, so the recoil axis is MEASURED
per species (6 candidates) by evaluating head world Z, not guessed.
"""
import json
import math
import traceback
import unreal

SPECIES = ['Compy', 'Raptor', 'Dilophosaurus', 'Triceratops', 'Ankylosaur', 'RiverAmbusher', 'Pterosaur']
CHAIN = {'neck_01': 34.0, 'neck_02': 26.0, 'head': 20.0, 'spine_02': 13.0, 'spine_01': 7.0}
FPS = 30
FRAMES = 15          # 0.5s, matches the 0.5s hit lock
PEAK = 3             # frame the recoil peaks on
opts = unreal.AnimPoseEvaluationOptions()
W = unreal.AnimPoseSpaces.WORLD
r = {}


def quat(x, y, z):
    q = unreal.Quat()
    q.set_from_euler(unreal.Vector(x, y, z))
    return q


def axis_euler(axis, sign, deg):
    d = sign * deg
    return quat(d, 0, 0) if axis == 'X' else (quat(0, d, 0) if axis == 'Y' else quat(0, 0, d))


def envelope(f):
    if f <= PEAK:
        a = f / float(PEAK)
    else:
        a = max(0.0, (FRAMES - f) / float(FRAMES - PEAK))
    return a * a * (3 - 2 * a)      # smoothstep


def write(anim, base, bones, chain, axis, sign, frames, animate):
    c = anim.get_editor_property('controller')
    c.open_bracket('flinch', False)
    c.set_frame_rate(unreal.FrameRate(FPS, 1), False)
    c.set_number_of_frames(unreal.FrameNumber(frames), False)
    n = frames + 1
    for bone in bones:
        t = base[bone]
        if bone in chain:
            rots = []
            for f in range(n):
                a = envelope(f) if animate else 1.0
                sway = 0.35 * chain[bone] * a * math.sin(f * 0.9)
                rots.append(t.rotation.multiply(axis_euler(axis, sign, chain[bone] * a)).multiply(quat(0, 0, sway)))
        else:
            rots = [t.rotation] * n
        c.add_bone_track(bone, False)
        c.set_bone_track_keys(bone, [t.translation] * n, rots, [t.scale3d] * n, False)
    c.close_bracket(False)


def head_z(anim, frame=0):
    p = anim.get_anim_pose_at_frame(frame, opts)
    names = [str(b) for b in p.get_bone_names()]
    hb = 'head' if 'head' in names else names[-1]
    return p.get_bone_pose(hb, W).translation.z


def build(sp):
    folder = '/Game/Timeshift/Enemies/%s' % sp
    idle = unreal.load_asset('%s/SK_%s_Anim_SK_%s_Idle' % (folder, sp, sp))
    sk = unreal.load_asset('%s/SK_%s' % (folder, sp)).get_editor_property('skeleton')
    pose = idle.get_anim_pose_at_frame(0, opts)
    bones = [str(b) for b in pose.get_bone_names()]
    base = {b: unreal.AnimationLibrary.get_bone_pose_for_frame(idle, b, 0, False) for b in bones}
    chain = {k: v for k, v in CHAIN.items() if k in bones}
    if not chain:
        return {'error': 'no chain bones', 'bones': bones[:8]}
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    idle_z = head_z(idle, 0)

    # measure: which local axis+sign rears the head UP
    probe_path = folder + '/TMP_FLINCH_SCAN'
    scan, best = [], (None, None, -1e9)
    for axis in ['X', 'Y', 'Z']:
        for sign in [1.0, -1.0]:
            if unreal.EditorAssetLibrary.does_asset_exist(probe_path):
                unreal.EditorAssetLibrary.delete_asset(probe_path)
            f = unreal.AnimSequenceFactory()
            f.set_editor_property('target_skeleton', sk)
            probe = tools.create_asset('TMP_FLINCH_SCAN', folder, unreal.AnimSequence, f)
            write(probe, base, bones, chain, axis, sign, 2, False)
            dz = head_z(probe, 0) - idle_z
            scan.append({'axis': axis, 'sign': sign, 'dz': round(dz, 1)})
            if abs(dz) > abs(best[2]) or best[0] is None:
                best = (axis, sign, dz)
            unreal.EditorAssetLibrary.delete_asset(probe_path)

    # rearing BACK reads as pain; a head drop can look like a lunge. Prefer the
    # best upward option whenever it is at least 45% as large as the best overall.
    ups = [c for c in scan if c['dz'] > 0]
    if ups:
        up = max(ups, key=lambda c: c['dz'])
        if up['dz'] >= 0.45 * abs(best[2]):
            best = (up['axis'], up['sign'], up['dz'])

    # scale the recoil to the creature's own size: aim for ~35% of head height
    target = 0.35 * idle_z
    mult = 1.0 if abs(best[2]) < 1e-3 else target / abs(best[2])
    mult = max(0.5, min(2.2, mult))
    chain = {k: v * mult for k, v in chain.items()}

    name = 'SK_%s_Anim_SK_%s_Flinch' % (sp, sp)
    path = folder + '/' + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    f = unreal.AnimSequenceFactory()
    f.set_editor_property('target_skeleton', sk)
    anim = tools.create_asset(name, folder, unreal.AnimSequence, f)
    write(anim, base, bones, chain, best[0], best[1], FRAMES, True)
    anim.set_editor_property('loop', False)
    unreal.EditorAssetLibrary.save_asset(path)

    # how far does the head travel over the clip?
    zs = [head_z(anim, i) for i in range(FRAMES + 1)]
    return {'axis': best[0], 'sign': best[1], 'mult': round(mult, 2), 'scan': scan, 'chain': list(chain),
            'idle_head_z': round(idle_z, 1), 'peak_head_z': round(max(zs), 1),
            'travel_cm': round(max(zs) - min(zs), 1), 'asset': path}


try:
    for s in SPECIES:
        try:
            r[s] = build(s)
        except Exception:
            r[s] = {'error': traceback.format_exc()[-400:]}
    r['status'] = 'ok'
except Exception:
    r['status'] = 'failed'
    r['traceback'] = traceback.format_exc()

json.dump(r, open(r'C:/repos/Unreal Projects/Timeshift3D/Saved/flinch_build.json', 'w'), indent=1, default=str)
unreal.log('FLINCH ' + str(r.get('status')))
