# Editor Python: author new dinosaur attack clips for every ground species, from script.
#   TailSwipe - wind-up, then the tail whips across (spine twists, head looks back)
#   Charge    - head and neck drop, the body lunges forward, recovers
#   Pounce    - crouch, leap forward, two quick head snaps, land
#   Roar      - rears up, head thrown back, shakes, settles
#   Stomp     - (quadrupeds) front half rears up, forefeet slam down
#   Gore      - (horned) head drops low, then tosses up with a twist
#   Frenzy    - (predators) neck thrust forward, three quick snaps left / right / centre
#   Slash     - (bipeds with hands) lean in, claws rake down left then right
#   Sidestep  - (small predators) hop to the side, turn back in and lunge-bite
# Every species shares the core bones (pelvis, spine_01-03, neck_01-02, head, tail_01-06, legs), so each move is defined
# ONCE as body-space rotations (Z = yaw/sideways, Y = pitch/up-down; meshes face +X) applied on top of the species' idle
# pose, then converted to each bone's local space by forward kinematics. Pelvis offsets are in units of pelvis height.
# Globals: SPECIES (list) and MOVES (list) can be set before exec to limit the run; DRY=True only logs.
import json
import math
import unreal

TAG = "[ATK]"
EAL = unreal.EditorAssetLibrary
FPS = 30
SKEL = json.load(open(r"C:/agentpy/skeletons.json"))
SPECIES = globals().get("SPECIES") or ["Raptor"]
MOVES = globals().get("MOVES") or ["TailSwipe"]
DRY = globals().get("DRY", False)
# sign conventions, verified by the FK self-check below (head goes DOWN for +pitch, tail goes toward +Y for +yaw)
PITCH_DOWN = globals().get("PITCH_DOWN", 1.0)
YAW_LEFT = globals().get("YAW_LEFT", 1.0)


# ---------------- quaternion helpers (x, y, z, w), Hamilton product: q1*q2 applies q2 first ----------------
def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz)


def qinv(q):
    return (-q[0], -q[1], -q[2], q[3])


def qaxis(axis, deg):
    h = math.radians(deg) / 2
    s = math.sin(h)
    return (axis[0] * s, axis[1] * s, axis[2] * s, math.cos(h))


def qrot(q, v):
    p = qmul(qmul(q, (v[0], v[1], v[2], 0.0)), qinv(q))
    return (p[0], p[1], p[2])


def qnorm(q):
    n = math.sqrt(sum(c * c for c in q)) or 1.0
    return tuple(c / n for c in q)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def env(t, keys):
    """piecewise smooth envelope: keys = [(time, value), ...] sorted; smoothstep between keys"""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * ease((t - t0) / max(1e-6, t1 - t0))
    return keys[-1][1]


Z = (0.0, 0.0, 1.0)
Y = (0.0, 1.0, 0.0)


# ---------------- the moves: f(t) -> ({bone: [(axis, deg), ...]}, pelvis_offset (fwd, side, up) in pelvis heights) --------
def tail_swipe(t):
    s = env(t, [(0, 0), (0.25, 1), (0.5, -1), (0.8, -0.6), (1.1, 0)])        # wind-up one way, whip the other
    r = {"pelvis": [(Z, 10 * s)], "spine_01": [(Z, 8 * s)], "spine_02": [(Z, 8 * s)], "spine_03": [(Z, 6 * s)],
         "neck_01": [(Z, -10 * s)], "head": [(Z, -12 * s)]}
    for i in range(1, 7):
        r["tail_%02d" % i] = [(Z, (6 + 4 * i) * s * YAW_LEFT)]                  # more swing toward the tip
    return r, (0.0, 0.0, -0.03 * abs(s))


def charge(t):
    d = env(t, [(0, 0), (0.3, 1), (0.55, 1), (1.0, 0)])                        # head down
    l = env(t, [(0, 0), (0.3, -0.15), (0.45, 0.45), (0.6, 0.45), (1.0, 0)])    # lean back, then lunge
    r = {"spine_02": [(Y, 6 * d * PITCH_DOWN)], "spine_03": [(Y, 6 * d * PITCH_DOWN)], "neck_01": [(Y, 14 * d * PITCH_DOWN)],
         "neck_02": [(Y, 12 * d * PITCH_DOWN)], "head": [(Y, 10 * d * PITCH_DOWN)],
         "tail_01": [(Y, -6 * d * PITCH_DOWN)], "tail_02": [(Y, -4 * d * PITCH_DOWN)]}
    return r, (l, 0.0, -0.06 * d)


def pounce(t):
    c = env(t, [(0, 0), (0.2, 1), (0.3, 0), (0.75, 0), (0.9, 0.6), (1.0, 0)])  # crouch, and absorb the landing
    a = env(t, [(0, 0), (0.2, 0), (0.35, 1), (0.6, 1), (0.85, 0)])             # airborne
    snap = math.sin(max(0.0, min(1.0, (t - 0.32) / 0.4)) * 2 * math.pi * 2) if 0.32 < t < 0.72 else 0.0   # two snaps
    r = {"leg_L_upper": [(Y, -18 * c * PITCH_DOWN)], "leg_R_upper": [(Y, -18 * c * PITCH_DOWN)],
         "leg_L_lower": [(Y, 30 * c * PITCH_DOWN)], "leg_R_lower": [(Y, 30 * c * PITCH_DOWN)],
         "spine_03": [(Y, 6 * a * PITCH_DOWN)], "neck_01": [(Y, 10 * a * PITCH_DOWN + 8 * snap * PITCH_DOWN)],
         "head": [(Y, 14 * snap * PITCH_DOWN)], "tail_01": [(Y, -8 * a * PITCH_DOWN)], "tail_02": [(Y, -6 * a * PITCH_DOWN)]}
    return r, (0.5 * a, 0.0, -0.18 * c + 0.35 * a)


def roar(t):
    u = env(t, [(0, 0), (0.35, 1), (1.25, 1), (1.6, 0)])                       # rear up and hold
    shake = math.sin(t * 2 * math.pi * 6) * env(t, [(0, 0), (0.4, 0), (0.5, 1), (1.15, 1), (1.3, 0)])
    r = {"pelvis": [(Y, -6 * u * PITCH_DOWN)], "spine_01": [(Y, -6 * u * PITCH_DOWN)], "spine_02": [(Y, -6 * u * PITCH_DOWN)],
         "spine_03": [(Y, -5 * u * PITCH_DOWN)], "neck_01": [(Y, -14 * u * PITCH_DOWN)], "neck_02": [(Y, -12 * u * PITCH_DOWN)],
         "head": [(Y, -16 * u * PITCH_DOWN), (Z, 7 * shake)], "tail_01": [(Y, 6 * u * PITCH_DOWN)], "tail_02": [(Y, 4 * u * PITCH_DOWN)]}
    return r, (-0.05 * u, 0.0, 0.05 * u)


def stomp(t):
    # quadrupeds: rear the front half up off the ground, then slam the forefeet down with the head
    u = env(t, [(0, 0), (0.4, 1), (0.55, 1), (0.7, -0.25), (0.85, -0.15), (1.2, 0)])
    lift, slam = max(0.0, u), max(0.0, -u) * 4
    r = {"pelvis": [(Y, -16 * u * PITCH_DOWN)], "spine_01": [(Y, -4 * u * PITCH_DOWN)],
         "neck_01": [(Y, (8 * lift + 12 * slam) * PITCH_DOWN)], "head": [(Y, (4 * lift + 10 * slam) * PITCH_DOWN)],
         # the hind legs hang off the pelvis: counter its pitch so the back feet stay planted
         "leg_L_upper": [(Y, 16 * u * PITCH_DOWN)], "leg_R_upper": [(Y, 16 * u * PITCH_DOWN)],
         "tail_01": [(Y, 10 * u * PITCH_DOWN)], "tail_02": [(Y, 6 * u * PITCH_DOWN)]}
    for b in ("arm_L_upper", "arm_R_upper"):
        r[b] = [(Y, -30 * lift * PITCH_DOWN)]                                # forelegs reach forward and up
    for b in ("arm_L_lower", "arm_R_lower"):
        r[b] = [(Y, 35 * lift * PITCH_DOWN)]                                 # knees fold
    return r, (-0.05 * lift, 0.0, 0.08 * lift - 0.06 * max(0.0, -u))


def gore(t):
    # horned heads: drop low, then a hard upward toss with a twist
    d = env(t, [(0, 0), (0.3, 1), (0.42, 1), (0.55, -1), (0.65, -1), (0.9, 0)])
    tw = env(t, [(0, 0), (0.42, 0), (0.55, 1), (0.7, 1), (0.9, 0)])
    l = env(t, [(0, 0), (0.3, -0.05), (0.5, 0.25), (0.65, 0.25), (0.9, 0)])
    r = {"spine_03": [(Y, 4 * d * PITCH_DOWN)], "neck_01": [(Y, 14 * d * PITCH_DOWN)], "neck_02": [(Y, 10 * d * PITCH_DOWN)],
         "head": [(Y, 16 * d * PITCH_DOWN), (Z, 14 * tw * YAW_LEFT)], "tail_01": [(Y, -4 * d * PITCH_DOWN)]}
    return r, (l, 0.0, -0.04 * max(0.0, d))


def frenzy(t):
    # predators: neck thrust forward, three fast snaps left-right-centre
    f = env(t, [(0, 0), (0.15, 1), (0.8, 1), (1.0, 0)])
    k = (t - 0.15) / 0.65
    snap = math.sin(k * 2 * math.pi * 3) if 0 < k < 1 else 0.0            # three bites
    side = env(k, [(0, -1), (0.33, -1), (0.4, 1), (0.66, 1), (0.73, 0)]) if 0 < k < 1 else 0.0
    r = {"spine_03": [(Y, 5 * f * PITCH_DOWN)], "neck_01": [(Y, 8 * f * PITCH_DOWN), (Z, 9 * side * f)],
         "neck_02": [(Y, 6 * f * PITCH_DOWN)], "head": [(Y, 16 * snap * f * PITCH_DOWN), (Z, 8 * side * f)],
         "tail_01": [(Z, -6 * side * f)], "tail_02": [(Z, -8 * side * f)], "tail_03": [(Z, -10 * side * f)]}
    return r, (0.15 * f, 0.0, -0.04 * f)


def slash(t):
    # bipeds with hands: lean in and rake both claws down, left then right
    lean = env(t, [(0, 0), (0.2, 1), (0.7, 1), (0.9, 0)])
    aL = env(t, [(0, 0), (0.2, 1), (0.38, -0.7), (0.55, 0), (0.9, 0)])
    aR = env(t, [(0, 0), (0.35, 1), (0.53, -0.7), (0.7, 0), (0.9, 0)])
    r = {"spine_02": [(Y, 5 * lean * PITCH_DOWN)], "spine_03": [(Y, 6 * lean * PITCH_DOWN), (Z, 6 * (aL - aR))],
         "neck_01": [(Y, -4 * lean * PITCH_DOWN)], "head": [(Y, 6 * lean * PITCH_DOWN)],
         "hand_arm_L_upper": [(Y, -55 * aL * PITCH_DOWN)], "hand_arm_L_lower": [(Y, -30 * aL * PITCH_DOWN)],
         "hand_arm_R_upper": [(Y, -55 * aR * PITCH_DOWN)], "hand_arm_R_lower": [(Y, -30 * aR * PITCH_DOWN)],
         "tail_01": [(Y, -4 * lean * PITCH_DOWN)]}
    return r, (0.2 * lean, 0.0, -0.03 * lean)


def sidestep(t):
    # small predators: hop to the side, turn back in and lunge-bite
    s = env(t, [(0, 0), (0.3, 1), (0.75, 1), (1.1, 0)])
    hop = math.sin(math.pi * t / 0.3) if t < 0.3 else 0.0                   # up and over during the side hop
    b = env(t, [(0, 0), (0.4, 0), (0.55, 1), (0.7, 0)])
    r = {"pelvis": [(Z, -14 * s)], "spine_03": [(Z, -6 * s)], "neck_01": [(Z, -8 * s), (Y, 10 * b * PITCH_DOWN)],
         "head": [(Y, 16 * b * PITCH_DOWN)], "tail_01": [(Z, 8 * s)], "tail_02": [(Z, 10 * s)],
         "leg_L_upper": [(Y, -12 * hop * PITCH_DOWN)], "leg_R_upper": [(Y, -12 * hop * PITCH_DOWN)],
         "leg_L_lower": [(Y, 22 * hop * PITCH_DOWN)], "leg_R_lower": [(Y, 22 * hop * PITCH_DOWN)]}
    return r, (0.25 * b, 0.6 * s, 0.25 * hop)


MOVE_DEFS = {"TailSwipe": (tail_swipe, 1.1), "Charge": (charge, 1.0), "Pounce": (pounce, 1.0), "Roar": (roar, 1.6),
             "Stomp": (stomp, 1.2), "Gore": (gore, 0.9), "Frenzy": (frenzy, 1.0), "Slash": (slash, 0.9),
             "Sidestep": (sidestep, 1.1)}


# ---------------- per-species base pose + FK ----------------
def apath(sp, clip):
    n = "SK_%s_Anim_SK_%s_%s" % (sp, sp, clip)
    return "/Game/Timeshift/Enemies/%s/%s.%s" % (sp, n, n)


def base_pose(sp, src):
    bones = SKEL[sp]
    loc = {}
    for nm, par in bones:
        tr = unreal.AnimationLibrary.get_bone_pose_for_frame(src, nm, 0, False)
        q = tr.rotation
        loc[nm] = ((tr.translation.x, tr.translation.y, tr.translation.z), qnorm((q.x, q.y, q.z, q.w)), tr.scale3d.x)
    return bones, loc


def fk(bones, local):
    cs = {}
    for nm, par in bones:
        p, q, s = local[nm]
        if par in cs:
            pp, pq, ps = cs[par]
            v = qrot(pq, (p[0] * ps, p[1] * ps, p[2] * ps))
            cs[nm] = ((pp[0] + v[0], pp[1] + v[1], pp[2] + v[2]), qnorm(qmul(pq, q)), ps * s)
        else:
            cs[nm] = (p, q, s)
    return cs


def posed(bones, base_local, base_cs, deltas, offset, unit):
    """apply body-space deltas (accumulating down the chain) + a pelvis offset; return new LOCAL transforms"""
    new_cs, new_local = {}, {}
    for nm, par in bones:
        bp, bq, bs = base_cs[nm]
        if par in new_cs:
            pq_new = new_cs[par][1]
            pdelta = qmul(pq_new, qinv(base_cs[par][1]))       # what the parent chain has rotated by so far
        else:
            pq_new, pdelta = None, (0, 0, 0, 1)
        d = (0, 0, 0, 1)
        for axis, deg in deltas.get(nm, []):
            d = qmul(qaxis(axis, deg), d)
        q_cs = qnorm(qmul(d, qmul(pdelta, bq)))
        lp, lq, ls = base_local[nm]
        if pq_new is not None:
            lq = qnorm(qmul(qinv(pq_new), q_cs))
            pp_new, _, ps = new_cs[par]
            pos = qrot(pdelta, qrot(base_cs[par][1], (lp[0] * ps, lp[1] * ps, lp[2] * ps)))
            p_cs = (pp_new[0] + pos[0], pp_new[1] + pos[1], pp_new[2] + pos[2])
            if nm == "pelvis":
                p_cs = (p_cs[0] + offset[0] * unit, p_cs[1] + offset[1] * unit, p_cs[2] + offset[2] * unit)
                rel = qrot(qinv(pq_new), (p_cs[0] - pp_new[0], p_cs[1] - pp_new[1], p_cs[2] - pp_new[2]))
                lp = (rel[0] / ps, rel[1] / ps, rel[2] / ps)
            new_cs[nm] = (p_cs, q_cs, ps * ls)
        else:
            new_cs[nm] = (bp, q_cs, bs)
            lq = q_cs
        new_local[nm] = (lp, lq, ls)
    return new_local, new_cs


def v3f(v):
    o = unreal.Vector3f()
    o.x, o.y, o.z = v
    return o


def q4f(q):
    # Quat4f exposes no fields to Python - set it from its text form
    o = unreal.Quat4f()
    o.import_text("(X=%.9f,Y=%.9f,Z=%.9f,W=%.9f)" % q)
    return o


def write_clip(sp, move, frames):
    skel_mesh = EAL.load_asset("/Game/Timeshift/Enemies/%s/SK_%s" % (sp, sp))
    skel = skel_mesh.skeleton
    name = "SK_%s_Anim_SK_%s_%s" % (sp, sp, move)
    folder = "/Game/Timeshift/Enemies/%s" % sp
    if EAL.does_asset_exist(folder + "/" + name):
        EAL.delete_asset(folder + "/" + name)
    f = unreal.AnimSequenceFactory()
    f.set_editor_property("target_skeleton", skel)
    seq = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, folder, unreal.AnimSequence, f)
    ctrl = seq.get_editor_property("controller")
    ctrl.open_bracket(unreal.Text("author %s" % move), True)
    ctrl.set_frame_rate(unreal.FrameRate(FPS, 1), True)
    ctrl.set_number_of_frames(unreal.FrameNumber(len(frames) - 1), True)
    for nm, _ in SKEL[sp]:
        # the Python-exposed SetBoneTrackKeys takes double-precision Vector / Quat arrays
        pos = [unreal.Vector(*fr[nm][0]) for fr in frames]
        rot = [unreal.Quat(*fr[nm][1]) for fr in frames]
        scl = [unreal.Vector(fr[nm][2], fr[nm][2], fr[nm][2]) for fr in frames]
        if hasattr(ctrl, "add_bone_curve"):
            ctrl.add_bone_curve(unreal.Name(nm), True)
        else:
            ctrl.add_bone_track(unreal.Name(nm), True)
        ctrl.set_bone_track_keys(unreal.Name(nm), pos, rot, scl, True)
    ctrl.close_bracket(True)
    EAL.save_asset(seq.get_path_name(), only_if_is_dirty=False)
    return seq


for sp in SPECIES:
    src = EAL.load_asset(apath(sp, "Idle"))
    bones, base_local = base_pose(sp, src)
    base_cs = fk(bones, base_local)
    unit = max(10.0, base_cs["pelvis"][0][2] - min(base_cs[b][0][2] for b in base_cs if "toe" in b or "foot" in b))
    for move in MOVES:
        fn, dur = MOVE_DEFS[move]
        n = int(round(dur * FPS)) + 1
        frames, probe = [], []
        for i in range(n):
            t = i / FPS
            deltas, off = fn(t)
            loc, cs = posed(bones, base_local, base_cs, deltas, off, unit)
            frames.append(loc)
            probe.append((t, cs["head"][0], cs["tail_06"][0], cs["pelvis"][0]))
        # self-check: head height / tail side at the peak frame vs the base pose
        h0, t0, p0 = base_cs["head"][0], base_cs["tail_06"][0], base_cs["pelvis"][0]
        pk = max(probe, key=lambda x: abs(x[1][2] - h0[2]) + abs(x[2][1] - t0[1]))
        unreal.log_warning("%s %s %s frames=%d unit=%.0f | base head z=%.0f tail y=%.0f | peak t=%.2f head z=%.0f (%+.0f) tail y=%.0f (%+.0f) pelvis=(%+.0f,%+.0f)" % (
            TAG, sp, move, n, unit, h0[2], t0[1], pk[0], pk[1][2], pk[1][2] - h0[2], pk[2][1], pk[2][1] - t0[1], pk[3][0] - p0[0], pk[3][2] - p0[2]))
        if not DRY:
            seq = write_clip(sp, move, frames)
            unreal.log_warning("%s wrote %s (%.2fs)" % (TAG, seq.get_path_name(), dur))
