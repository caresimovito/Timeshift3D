# Editor Python: how much do the feet actually move in each species' Walk / Run clip? FK from the saved clips (component
# space) - per foot, the range of its forward (x) and up (z) position over the clip, relative to the pelvis. A real stride
# swings the foot tens of cm; a sliding gait barely moves it. Compares the repaired species with species that walk fine.
import json
import math
import unreal
TAG = "[GAIT]"
AL = unreal.AnimationLibrary
EAL = unreal.EditorAssetLibrary
SKEL = json.load(open(r"C:/agentpy/skeletons.json"))
_q = {"math": math}
src = open(r"C:/agentpy/dino_attack_anims.py").read()
exec(src[src.index("def qmul"):src.index("Z = (0.0")] + src[src.index("def fk"):src.index("def posed")], _q)
for sp in ("Psittacosaurus", "Caudipteryx", "Archaeoceratops", "Kulindadromeus", "Compy", "Raptor"):
    for clip in ("Walk", "Run"):
        n = "SK_%s_Anim_SK_%s_%s" % (sp, sp, clip)
        a = EAL.load_asset("/Game/Timeshift/Enemies/%s/%s" % (sp, n))
        if not a:
            continue
        nf = AL.get_num_frames(a)
        fx, fz, hz = [], [], []
        for f in range(0, nf, max(1, nf // 16)):
            loc = {}
            for b, _ in SKEL[sp]:
                tr = AL.get_bone_pose_for_frame(a, b, f, False)
                q = tr.rotation
                loc[b] = ((tr.translation.x, tr.translation.y, tr.translation.z), _q["qnorm"]((q.x, q.y, q.z, q.w)), tr.scale3d.x)
            cs = _q["fk"](SKEL[sp], loc)
            pv = cs["pelvis"][0]
            ft = cs["leg_L_foot"][0]
            fx.append(ft[0] - pv[0])
            fz.append(ft[2] - pv[2])
            hz.append(pv[2])
        leg = math.dist(cs["pelvis"][0], cs["leg_L_foot"][0])
        unreal.log_warning("%s %-15s %-4s frames %3d | foot swing fwd %.0f cm, lift %.0f cm, pelvis bob %.0f cm | leg length %.0f cm -> swing/leg %.2f" % (
            TAG, sp, clip, nf, max(fx) - min(fx), max(fz) - min(fz), max(hz) - min(hz), leg, (max(fx) - min(fx)) / max(1.0, leg)))
unreal.log_warning("%s done" % TAG)
