# Editor Python: author the BASE clips (Idle, Walk, Run, Attack, Hit, Flinch, Death) of the three repaired species
# (Psittacosaurus, Caudipteryx, Archaeoceratops). Their original retargeted clips hold one frozen pose in every frame
# (clip_motion_check.py: 0 cm of motion; gait_check.py: feet swing 0 cm) - so they slid along without moving their legs
# and stood like statues (user 2026-10-22). Same method as dino_attack_anims.py: body-space rotations on top of the
# species' rest pose (Idle frame 0), FK to local. Written IN PLACE into the existing assets (they are referenced by
# BP_EnemyBase / the morph), keeping the frame rate. Globals: SPECIES, CLIPS, DRY.
import math
import unreal

_src = open(r"C:/agentpy/dino_attack_anims.py").read()
exec(_src[:_src.index("\nfor sp in SPECIES:")])          # helpers: qaxis, env, posed, base_pose, fk, apath, SKEL, Y, Z ...
TAG = "[BASE]"
SPECIES = globals().get("BASE_SPECIES") or ["Psittacosaurus", "Caudipteryx", "Archaeoceratops"]
CLIPS = globals().get("BASE_CLIPS") or ["Idle", "Walk", "Run", "Attack", "Hit", "Flinch", "Death"]
DRY = globals().get("DRY", False)
X = (1.0, 0.0, 0.0)
TAU = 2 * math.pi
PD = PITCH_DOWN


def legs(ph, hip, knee, foot=0.6):
    """one stride: left leg at phase ph, right leg half a cycle later. Forward swing = -Y on a downward limb."""
    r = {}
    for side, p in (("L", ph), ("R", ph + math.pi)):
        h = hip * math.sin(p)                                  # + = forward
        k = knee * max(0.0, math.cos(p))                       # knee folds while the leg swings forward
        r["leg_%s_upper" % side] = [(Y, -h * PD)]
        r["leg_%s_lower" % side] = [(Y, k * PD)]
        r["leg_%s_foot" % side] = [(Y, (h - k) * foot * PD)]    # keep the foot roughly level
    return r


def gait(t, period, hip, knee, bob, lean, sway):
    ph = TAU * t / period
    r = legs(ph, hip, knee)
    s = math.sin(ph)
    r.update({"pelvis": [(Z, sway * s)], "spine_01": [(Z, -0.6 * sway * s)], "spine_02": [(Y, lean * PD)],
              "spine_03": [(Y, 0.5 * lean * PD)], "neck_01": [(Y, -0.6 * lean * PD), (Z, -0.5 * sway * s)],
              "head": [(Y, (1.5 * math.sin(2 * ph) - 0.4 * lean) * PD)],
              "hand_arm_L_upper": [(Y, -6 * s * PD)], "hand_arm_R_upper": [(Y, 6 * s * PD)]})
    for i in range(1, 7):
        r["tail_%02d" % i] = [(Z, (1.5 + 0.8 * i) * math.sin(ph - 0.45 * i) * sway / 4.0), (Y, -0.5 * lean * PD if i < 3 else 0.0)]
    return r, (0.03 * lean / 8.0, 0.0, -bob * 0.5 * (1 - math.cos(2 * ph)))


def walk(t):
    return gait(t, 32.0 / FPS, hip=24, knee=38, bob=0.035, lean=3, sway=4)


def run(t):
    return gait(t, 20.0 / FPS, hip=40, knee=70, bob=0.07, lean=10, sway=6)


def idle(t):
    b = math.sin(TAU * t / 2.0)                                # breathe, one cycle per 2 s (clip = 2 s, loops)
    look = math.sin(TAU * t / 2.0 + 0.8)
    r = {"spine_02": [(Y, 1.2 * b * PD)], "spine_03": [(Y, 1.0 * b * PD)], "neck_01": [(Z, 9 * look), (Y, -1.5 * b * PD)],
         "head": [(Z, 7 * look), (Y, 2 * math.sin(TAU * t) * PD)]}
    for i in range(1, 7):
        r["tail_%02d" % i] = [(Z, (1 + 0.6 * i) * math.sin(TAU * t / 2.0 - 0.5 * i))]
    return r, (0.0, 0.0, -0.01 * (1 - b))


def bite(t):
    d = env(t, [(0, 0), (0.25, 1), (0.4, 1), (0.8, 0)])         # lean in
    snap = env(t, [(0, 0), (0.25, -0.5), (0.36, 1), (0.48, 0.2), (0.8, 0)])
    r = {"spine_02": [(Y, 5 * d * PD)], "spine_03": [(Y, 6 * d * PD)], "neck_01": [(Y, 10 * d * PD)], "neck_02": [(Y, 8 * d * PD)],
         "head": [(Y, 22 * snap * PD)], "tail_01": [(Y, -5 * d * PD)], "tail_02": [(Y, -4 * d * PD)]}
    r.update(legs(0.0, 0, 0))
    r["leg_L_upper"] = [(Y, -8 * d * PD)]
    r["leg_L_lower"] = [(Y, 12 * d * PD)]
    return r, (0.22 * d, 0.0, -0.04 * d)


def recoil(t, dur):
    k = env(t, [(0, 0), (0.12 * dur / 0.5, 1), (dur, 0)])
    r = {"pelvis": [(Y, -6 * k * PD)], "spine_02": [(Y, -6 * k * PD)], "spine_03": [(Y, -5 * k * PD)], "neck_01": [(Y, -12 * k * PD)],
         "head": [(Y, -16 * k * PD), (Z, 10 * k)], "tail_01": [(Y, 8 * k * PD)], "tail_02": [(Y, 6 * k * PD)],
         "leg_L_upper": [(Y, 10 * k * PD)], "leg_R_upper": [(Y, 6 * k * PD)]}
    return r, (-0.12 * k, 0.0, 0.02 * k)


def death(t):
    f = env(t, [(0, 0), (0.25, 0.15), (0.75, 1), (1.3, 1)])     # stagger, topple onto the side, lie still
    g = env(t, [(0, 0), (0.2, 1), (0.5, 0.6), (0.9, 0)])
    r = {"pelvis": [(X, 82 * f), (Y, -5 * g * PD)], "neck_01": [(Y, 25 * f * PD), (Z, -15 * f)], "neck_02": [(Y, 15 * f * PD)],
         "head": [(Y, 20 * f * PD), (Z, -10 * f)], "leg_L_upper": [(Y, -30 * f * PD)], "leg_L_lower": [(Y, 45 * f * PD)],
         "leg_R_upper": [(Y, -15 * f * PD)], "leg_R_lower": [(Y, 60 * f * PD)], "hand_arm_L_upper": [(Y, -20 * f * PD)]}
    for i in range(1, 7):
        r["tail_%02d" % i] = [(Z, -6 * f), (Y, 3 * f * PD)]
    return r, (0.0, 0.25 * f, -0.55 * f)


DEFS = {"Idle": idle, "Walk": walk, "Run": run, "Attack": bite, "Hit": lambda t: recoil(t, 0.45), "Flinch": lambda t: recoil(t, 0.5),
        "Death": death}


def write_in_place(seq, sp, frames, fps):
    ctrl = seq.get_editor_property("controller")
    ctrl.open_bracket(unreal.Text("author base clip"), True)
    ctrl.set_frame_rate(unreal.FrameRate(fps, 1), True)
    ctrl.set_number_of_frames(unreal.FrameNumber(len(frames) - 1), True)
    for nm, _ in SKEL[sp]:
        pos = [unreal.Vector(*fr[nm][0]) for fr in frames]
        rot = [unreal.Quat(*fr[nm][1]) for fr in frames]
        scl = [unreal.Vector(fr[nm][2], fr[nm][2], fr[nm][2]) for fr in frames]
        ctrl.set_bone_track_keys(unreal.Name(nm), pos, rot, scl, True)
    ctrl.close_bracket(True)
    EAL.save_asset(seq.get_path_name(), only_if_is_dirty=False)


AL = unreal.AnimationLibrary
for sp in SPECIES:
    src = EAL.load_asset(apath(sp, "Idle"))
    bones, base_local = base_pose(sp, src)
    base_cs = fk(bones, base_local)
    unit = max(10.0, base_cs["pelvis"][0][2] - min(base_cs[b][0][2] for b in base_cs if "toe" in b or "foot" in b))
    for clip in CLIPS:
        seq = EAL.load_asset(apath(sp, clip))
        if not seq:
            unreal.log_warning("%s %s %s missing" % (TAG, sp, clip))
            continue
        n_old = AL.get_num_frames(seq) + 1
        n = n_old if clip != "Idle" else max(n_old, 61)
        fn = DEFS[clip]
        frames, heads, feet = [], [], []
        for i in range(n):
            t = i / float(FPS)
            deltas, off = fn(t)
            loc, cs = posed(bones, base_local, base_cs, deltas, off, unit)
            frames.append(loc)
            heads.append(cs["head"][0])
            feet.append(cs["leg_L_foot"][0])
        hm = max(math.dist(a, b) for a in heads for b in heads)
        fm = max(math.dist(a, b) for a in feet for b in feet)
        unreal.log_warning("%s %s %-6s frames %d (%.2fs) unit %.0f | head moves %.0f cm, left foot %.0f cm%s" % (
            TAG, sp, clip, n, (n - 1) / float(FPS), unit, hm, fm, " (dry)" if DRY else ""))
        if not DRY:
            write_in_place(seq, sp, frames, FPS)
unreal.log_warning("%s done" % TAG)
