"""Author SK_Brontosaurus_Anim_SK_Brontosaurus_Graze from the existing Idle pose.

Run inside the Unreal editor (it uses the editor-only animation data controller).

There is no grazing clip in the Brontosaurus set -- only Idle, Walk, Run, Attack and Death --
so this builds one by curling the neck chain down out of the idle pose.

The rig's bone axes are not world aligned (neck_01's idle euler is 51.8, -62.6, 9.6), so the
curl axis was found by measurement rather than guesswork: every combination of local axis,
sign and composition order was built and the head bone evaluated in world space. A negative
rotation about local X, post-multiplied onto the idle rotation, is the one that lowers the
head -- 42/36/26 degrees across neck_01, neck_02 and head drops it from Z 1002 to Z 388.
Local Z is the lateral axis, so that carries the sway.

CURL_SCALE is then searched so the head finishes near TARGET_HEAD_Z, roughly grass height.
"""
import json
import math
import traceback

import unreal

FOLDER = '/Game/Timeshift/Enemies/Brontosaurus'
SK = FOLDER + '/SK_Brontosaurus.SK_Brontosaurus'
IDLE = FOLDER + '/SK_Brontosaurus_Anim_SK_Brontosaurus_Idle.SK_Brontosaurus_Anim_SK_Brontosaurus_Idle'
NAME = 'SK_Brontosaurus_Anim_SK_Brontosaurus_Graze'
OUT = r'C:/repos/Unreal Projects/Timeshift3D/Saved/graze_build.json'

NECK = ['neck_01', 'neck_02', 'head']
CURL = {'neck_01': -42.0, 'neck_02': -36.0, 'head': -26.0}   # degrees about local X
SWAY = {'neck_01': 9.0, 'neck_02': 6.0, 'head': 3.0}         # degrees about local Z
FPS = 30
FRAMES = 180                  # 6 s, loops
TARGET_HEAD_Z = 230.0

r = {}


def quat(x, y, z):
    q = unreal.Quat()
    q.set_from_euler(unreal.Vector(x, y, z))
    return q


def head_at(anim, frame=0):
    pose = anim.get_anim_pose_at_frame(frame, unreal.AnimPoseEvaluationOptions())
    t = pose.get_bone_pose('head', unreal.AnimPoseSpaces.WORLD)
    return [round(t.translation.x, 1), round(t.translation.y, 1), round(t.translation.z, 1)]


def write(anim, base, bones, mult, frames, animate):
    """Hold every bone at its idle frame-0 pose; drive only the neck chain."""
    c = anim.get_editor_property('controller')
    c.open_bracket('graze', False)
    c.set_frame_rate(unreal.FrameRate(FPS, 1), False)
    c.set_number_of_frames(unreal.FrameNumber(frames), False)
    n = frames + 1
    for bone in bones:
        t = base[bone]
        if bone in NECK and animate:
            rots = []
            for f in range(n):
                phase = 2.0 * math.pi * f / float(frames)
                sway = SWAY[bone] * math.sin(phase)
                bob = 4.0 * math.sin(phase * 5.0) if bone == 'head' else 0.0
                rots.append(t.rotation.multiply(quat(CURL[bone] * mult + bob, 0.0, sway)))
        elif bone in NECK:
            rots = [t.rotation.multiply(quat(CURL[bone] * mult, 0.0, 0.0))] * n
        else:
            rots = [t.rotation] * n
        c.add_bone_track(bone, False)
        c.set_bone_track_keys(bone, [t.translation] * n, rots, [t.scale3d] * n, False)
    c.close_bracket(False)


def main():
    idle = unreal.load_asset(IDLE)
    skeleton = unreal.load_asset(SK).get_editor_property('skeleton')
    pose = idle.get_anim_pose_at_frame(0, unreal.AnimPoseEvaluationOptions())
    bones = [str(b) for b in pose.get_bone_names()]
    base = {b: unreal.AnimationLibrary.get_bone_pose_for_frame(idle, b, 0, False) for b in bones}
    tools = unreal.AssetToolsHelpers.get_asset_tools()

    probe_path = FOLDER + '/TMP_GZ_SCAN'
    scan, best = [], (1.0, 1e9)
    for step in range(0, 13):
        mult = 1.0 + 0.1 * step
        if unreal.EditorAssetLibrary.does_asset_exist(probe_path):
            unreal.EditorAssetLibrary.delete_asset(probe_path)
        f = unreal.AnimSequenceFactory()
        f.set_editor_property('target_skeleton', skeleton)
        probe = tools.create_asset('TMP_GZ_SCAN', FOLDER, unreal.AnimSequence, f)
        write(probe, base, bones, mult, 2, False)
        h = head_at(probe)
        scan.append({'mult': round(mult, 2), 'head': h})
        if abs(h[2] - TARGET_HEAD_Z) < best[1]:
            best = (mult, abs(h[2] - TARGET_HEAD_Z))
        unreal.EditorAssetLibrary.delete_asset(probe_path)
    r['scan'] = scan
    r['mult'] = round(best[0], 2)

    path = FOLDER + '/' + NAME
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    f = unreal.AnimSequenceFactory()
    f.set_editor_property('target_skeleton', skeleton)
    anim = tools.create_asset(NAME, FOLDER, unreal.AnimSequence, f)
    write(anim, base, bones, best[0], FRAMES, True)
    anim.set_editor_property('loop', True)
    unreal.EditorAssetLibrary.save_asset(path)
    r['idle_head'] = head_at(idle, 0)
    r['graze_head'] = head_at(anim, 0)
    r['asset'] = path


try:
    main()
    r['status'] = 'ok'
except Exception:
    r['status'] = 'failed'
    r['traceback'] = traceback.format_exc()

json.dump(r, open(OUT, 'w'), indent=1, default=str)
unreal.log('GRAZEBUILD ' + r['status'])
