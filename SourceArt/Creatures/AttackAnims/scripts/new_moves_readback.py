# Editor Python (no PIE): read every second-batch clip back from the saved asset, rebuild the pose by FK at 25/50/75 %,
# and compare head / tail distance from the pelvis with the species' idle pose - catches collapsed or exploded clips.
import json
import unreal
TAG = "[NMR]"
exec(open(r"C:/agentpy/run_new_moves.py").read().split("_dry =")[0])          # just NEW_MOVES
SKEL = json.load(open(r"C:/agentpy/skeletons.json"))
AL = unreal.AnimationLibrary
# borrow the quaternion helpers and fk() from the authoring script
_q = {"math": __import__("math")}
src = open(r"C:/agentpy/dino_attack_anims.py").read()
helpers = src[src.index("def qmul"):src.index("Z = (0.0")]
fk_src = src[src.index("def fk"):src.index("def posed")]
exec(helpers + fk_src, _q)


def load(sp, clip):
    n = "SK_%s_Anim_SK_%s_%s" % (sp, sp, clip)
    return unreal.load_object(None, "/Game/Timeshift/Enemies/%s/%s.%s" % (sp, n, n))


def pose(seq, sp, frame):
    loc = {}
    for nm, _ in SKEL[sp]:
        tr = AL.get_bone_pose_for_frame(seq, nm, frame, False)
        q = tr.rotation
        loc[nm] = ((tr.translation.x, tr.translation.y, tr.translation.z), _q["qnorm"]((q.x, q.y, q.z, q.w)), tr.scale3d.x)
    return _q["fk"](SKEL[sp], loc)


def d(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


bad = 0
for sp, mvs in NEW_MOVES.items():
    idle = pose(load(sp, "Idle"), sp, 0)
    ih, it = d(idle["head"][0], idle["pelvis"][0]), d(idle["tail_06"][0], idle["pelvis"][0])
    for mv in mvs:
        seq = load(sp, mv)
        nf = AL.get_num_frames(seq)
        hs, ts, mvh = [], [], 0.0
        for fr in (nf // 4, nf // 2, 3 * nf // 4):
            cs = pose(seq, sp, fr)
            hs.append(d(cs["head"][0], cs["pelvis"][0]))
            ts.append(d(cs["tail_06"][0], cs["pelvis"][0]))
            mvh = max(mvh, d(cs["head"][0], idle["head"][0]))
        ok = 0.6 * ih < min(hs) and max(hs) < 1.6 * ih and 0.6 * it < min(ts) and max(ts) < 1.6 * it
        bad += 0 if ok else 1
        unreal.log_warning("%s %-15s %-8s frames=%d len=%.2f head-pelvis %.0f..%.0f (idle %.0f) tail %.0f..%.0f (idle %.0f) head moves %.0f %s" % (
            TAG, sp, mv, nf, seq.get_play_length(), min(hs), max(hs), ih, min(ts), max(ts), it, mvh, "ok" if ok else "BAD"))
unreal.log_warning("%s done, %d bad" % (TAG, bad))
