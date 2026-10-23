# Editor Python: for every clip of the three repaired species, the largest movement of head / feet / tail tip over the clip
# (FK, component space). ~0 = a frozen pose.
import json
import math
import unreal
TAG = "[CMC]"
AL = unreal.AnimationLibrary
EAL = unreal.EditorAssetLibrary
SKEL = json.load(open(r"C:/agentpy/skeletons.json"))
_q = {"math": math}
src = open(r"C:/agentpy/dino_attack_anims.py").read()
exec(src[src.index("def qmul"):src.index("Z = (0.0")] + src[src.index("def fk"):src.index("def posed")], _q)
for sp in ("Psittacosaurus", "Caudipteryx", "Archaeoceratops"):
    rows = []
    for p in sorted(EAL.list_assets("/Game/Timeshift/Enemies/%s" % sp, False)):
        if "_Anim_" not in p:
            continue
        a = EAL.load_asset(p.split(".")[0])
        if not isinstance(a, unreal.AnimSequence):
            continue
        nf = AL.get_num_frames(a)
        pts = {"head": [], "leg_L_foot": [], "tail_06": []}
        for f in range(0, nf + 1, max(1, nf // 10)):
            loc = {}
            for b, _ in SKEL[sp]:
                tr = AL.get_bone_pose_for_frame(a, b, f, False)
                q = tr.rotation
                loc[b] = ((tr.translation.x, tr.translation.y, tr.translation.z), _q["qnorm"]((q.x, q.y, q.z, q.w)), tr.scale3d.x)
            cs = _q["fk"](SKEL[sp], loc)
            for k in pts:
                pts[k].append(cs[k][0])
        mv = max(max(math.dist(x, y) for x in v for y in v) for v in pts.values())
        rows.append("%s %.0f" % (p.split("_")[-1].split(".")[0], mv))
    unreal.log_warning("%s %-15s %s" % (TAG, sp, " | ".join(rows)))
unreal.log_warning("%s done" % TAG)
